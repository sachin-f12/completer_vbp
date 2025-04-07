import re
import fitz  # PyMuPDF
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()
DOWNLOADS_DIR = Path("download")

@router.get("/extract-metadata/")
async def extract_metadata(pdf_path: str = Query(None, description="Relative path of the selected PDF")):
    if not pdf_path:
        pdf_files = [str(pdf.relative_to(DOWNLOADS_DIR)) for pdf in DOWNLOADS_DIR.rglob("*.pdf")]
        return {"available_pdfs": pdf_files} if pdf_files else {"message": "No PDFs found in the downloads directory."}

    file_path = DOWNLOADS_DIR / pdf_path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"PDF not found: {pdf_path}")

    try:
        with fitz.open(file_path) as doc:
            metadata = doc.metadata
            first_page_text = doc[0].get_text("text")
            full_text = "\n".join(page.get_text("text") for page in doc)

        title = metadata.get("title", "Unknown")
        authors = metadata.get("author", "Unknown")

        match = re.search(r'(?:journal of|published in|appeared in)\s+([A-Za-z0-9\s]+)[,\s]+(\d{4})', first_page_text, re.IGNORECASE)
        journal_name, publication_year = (match.groups() if match else ("Not Found", metadata.get("creationDate", "Unknown")[2:6] if metadata.get("creationDate") else "Unknown"))

        doi_match = re.search(r'10\.\d{4,}/[^\s]+', full_text)
        url_match = re.search(r'https?://[^\s]+', full_text)
        link = doi_match.group() if doi_match else (url_match.group() if url_match else "Not Found")

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
        raise HTTPException(status_code=500, detail=f"Error extracting metadata: {str(e)}")
