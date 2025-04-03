from fastapi import FastAPI, File, UploadFile,APIRouter
import fitz  # PyMuPDF
import io

router=APIRouter()

# def extract_metadata_from_pdf(file_bytes):
#     """Extract actual metadata from a PDF file."""
#     try:
#         doc = fitz.open(stream=file_bytes, filetype="pdf")
#         metadata = doc.metadata
#         doc.close()

#         return {
#             "Title": metadata.get("title", "Unknown"),
#             "Authors": metadata.get("author", "Unknown"),
#             "Publication Year": metadata.get("creationDate", "Unknown")[2:6],  # Extract Year
#             "Journal Name": "Not Available",  # Journal info usually missing in metadata
#             "DOI/Link": "Not Available"  # DOI usually not in metadata
#         }
#     except Exception as e:
#         return {"Error": f"Failed to extract metadata: {str(e)}"}

# @router.post("/extract-metadata/")
# async def extract_metadata(file: UploadFile = File(...)):
#     try:
#         # Read file into memory
#         file_bytes = await file.read()
        
#         # Extract metadata using the provided function
#         metadata = extract_metadata_from_pdf(file_bytes)
        
#         return {"filename": file.filename, "metadata": metadata}
#     except Exception as e:
#         return {"error": str(e)}
from pathlib import Path
import re
from fastapi import HTTPException,APIRouter, Query
import fitz
router=APIRouter()
DOWNLOADS_DIR = Path("download")  # Change this if your folder is named differently

@router.get("/extract-metadata/")
async def extract_metadata(pdf_path: str = Query(None, description="Relative path of the selected PDF")):
    """
    If pdf_path is not provided, return a list of available PDFs for selection.
    If pdf_path is provided, extract metadata from the selected PDF.
    """
    # If no file is selected, return all available PDFs
    if not pdf_path:
        pdf_files = [str(pdf.relative_to(DOWNLOADS_DIR)) for pdf in DOWNLOADS_DIR.rglob("*.pdf")]
        if not pdf_files:
            return {"message": "No PDFs found in the downloads directory."}
        return {"available_pdfs": pdf_files}

    # Get absolute path of the selected PDF
    file_path = DOWNLOADS_DIR / pdf_path

    # Check if the PDF exists
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"PDF not found: {pdf_path}")

    try:
        doc = fitz.open(file_path)  # Open the PDF
        
        # Extract metadata
        metadata = doc.metadata
        first_page = doc[0]  # Load first page
        first_page_text = first_page.get_text("text")

        # Extract text from all pages for links
        full_text = "\n".join(page.get_text("text") for page in doc)

        doc.close()

        # Extract metadata fields
        title = metadata.get("title", "Unknown")
        authors = metadata.get("author", "Unknown")

        # Extract journal name and publication year
        journal_year_pattern = r'(?:journal of|published in|appeared in)\s+([A-Za-z0-9\s]+)[,\s]+(\d{4})'
        match = re.search(journal_year_pattern, first_page_text, re.IGNORECASE)
        if match:
            journal_name = match.group(1).strip()
            publication_year = match.group(2)
        else:
            journal_name = "Not Found"
            publication_year = metadata.get("creationDate", "Unknown")[2:6] if metadata.get("creationDate") else "Unknown"

        # Extract link (DOI or URL)
        doi_pattern = r'10\.\d{4,}/[^\s]+'
        url_pattern = r'https?://[^\s]+'
        doi_match = re.search(doi_pattern, full_text)
        link = doi_match.group() if doi_match else re.search(url_pattern, full_text).group() if re.search(url_pattern, full_text) else "Not Found"

        return {
            "filename": pdf_path,
            "metadata": {
                "Title": title,
                "Authors": authors,
                "Publication Year": publication_year,
                "Journal Name": journal_name,
                "Link": link
            }
        }

    except Exception as e:
        return {"error": str(e)}