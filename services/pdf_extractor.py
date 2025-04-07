
import base64
import csv
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException
import fitz
from openai import api_key
import requests


def encode_image(image_bytes):
    """Encodes image bytes to Base64 format."""
    return base64.b64encode(image_bytes).decode("utf-8")

def extract_tables_from_image(image_bytes):
    """Extracts tables from an image using OpenAI's GPT-4o-mini."""
    base64_image = encode_image(image_bytes)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    print("working on images tables")
    content_text = (
        "Extract all tables from the provided image. If no tables are found, return 'no table found'. "
        "If multiple tables exist, separate them properly."
    )
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": content_text},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
        "max_tokens": 800
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error processing image with OpenAI API.")
    
    return response.json()['choices'][0]['message']['content']

def extract_images_from_pdf(pdf_file: BytesIO, save_dir: Path):
    """Extract images from a PDF file and save them to a directory."""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    save_dir.mkdir(parents=True, exist_ok=True)
    print("working on images")
    extracted_images = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            img_ext = base_image["ext"]
            img_name = f"image_{page_num + 1}_{img_index}.{img_ext}"
            img_path = save_dir / img_name

            with open(img_path, "wb") as f:
                f.write(img_bytes)

            extracted_images.append(str(img_path))
    
    return extracted_images

def extract_tables_from_pdf(pdf_bytes: bytes, save_dir: Path):
    """Extract tables from a PDF and store as CSV files in a folder."""
    # Use PyMuPDF to convert PDF to images
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    extracted_tables = []

    for i in range(len(doc)):
        page = doc[i]
        # Render page to an image with a higher resolution for better OCR
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_bytes = pix.tobytes(output="jpeg")
        
        extracted_text = extract_tables_from_image(img_bytes)

        if extracted_text and "no table found" not in extracted_text.lower():
            csv_filename = save_dir / f"table_page_{i + 1}.csv"
            
            with open(csv_filename, "w", newline="") as f:
                csv_writer = csv.writer(f)
                for line in extracted_text.split("\n"):
                    columns = [cell.strip() for cell in line.split("|") if cell.strip()]
                    if columns:
                        csv_writer.writerow(columns)

            extracted_tables.append(str(csv_filename))
    
    return extracted_tables