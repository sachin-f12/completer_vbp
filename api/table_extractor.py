from fastapi import APIRouter, UploadFile, File, HTTPException
from io import BytesIO
import csv
import os
from dotenv import load_dotenv
import fitz

from services.pdf_extractor import extract_tables_from_image  # PyMuPDF

# Load environment variables
load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("Missing OpenAI API key. Ensure it is set in the environment variables.")

router = APIRouter()
BASE_FOLDER = "download/extracted_tables"
os.makedirs(BASE_FOLDER, exist_ok=True)


@router.post("/extract-tables/")
async def extract_tables_from_pdf(pdf_file: UploadFile = File(...)):
    """Extracts tables from a PDF file and saves CSV files inside a folder named after the PDF."""
    try:
        pdf_bytes = await pdf_file.read()
        pdf_name = pdf_file.filename.rsplit(".", 1)[0]  # Get filename without extension
        save_folder = os.path.join(BASE_FOLDER, pdf_name)  # Ensure correct folder

        os.makedirs(save_folder, exist_ok=True)  # Create folder if not exists

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
                csv_filename = os.path.join(save_folder, f"table_page_{i + 1}.csv")
                
                with open(csv_filename, "w", newline="") as f:
                    csv_writer = csv.writer(f)
                    for line in extracted_text.split("\n"):
                        columns = [cell.strip() for cell in line.split("|") if cell.strip()]
                        if columns:
                            csv_writer.writerow(columns)

                extracted_tables.append(csv_filename)
        
        if not extracted_tables:
            raise HTTPException(status_code=400, detail="No tables found in the PDF.")

        return {"message": f"Extraction completed. Tables saved in: {save_folder}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting tables: {str(e)}")