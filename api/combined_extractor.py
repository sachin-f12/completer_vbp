from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from io import BytesIO

from services.pdf_extractor import extract_images_from_pdf, extract_tables_from_pdf

router = APIRouter()
BASE_FOLDER = Path("download/combined_extractions")
BASE_FOLDER.mkdir(parents=True, exist_ok=True)

@router.post("/combined_extractor/")
async def extract_combined(pdf_file: UploadFile = File(...)):
    """Extract images and tables from an uploaded PDF and save them in a dedicated folder."""
    try:
        pdf_bytes = await pdf_file.read()
        pdf_name = Path(pdf_file.filename).stem  # Get filename without extension
        save_folder = BASE_FOLDER / pdf_name
        save_folder.mkdir(parents=True, exist_ok=True)

        extracted_images = extract_images_from_pdf(BytesIO(pdf_bytes), save_folder)
        extracted_tables = extract_tables_from_pdf(pdf_bytes, save_folder)

        if not (extracted_images or extracted_tables):
            raise HTTPException(status_code=400, detail="No tables or images found in the PDF.")

        return {
            "message": f"Extraction completed. Files saved in: {save_folder}",
            "image_files": extracted_images,
            "table_files": extracted_tables
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting content: {e}")
