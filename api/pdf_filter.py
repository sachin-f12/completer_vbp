from fastapi import FastAPI, HTTPException, Query,APIRouter
from pathlib import Path
import shutil
import fitz  # PyMuPDF
from typing import List, Optional
import os

from utils.file_operations import extract_text_from_pdf, list_all_directories, search_terms_in_text 
router = APIRouter()

INPUT_DIR = "download"  # Set your base input directory
OUTPUT_DIR = r"download\filtered_pdfs"  # Set output directory for filtered PDFs



@router.get("/list-all-directories")
def get_all_directories():
    """ Returns all directories and subdirectories under INPUT_DIR. """
    return {"directories": list_all_directories(INPUT_DIR)}

@router.post("/filter-pdfs")
def filter_pdfs(
    src_directory: str,
    include_terms: Optional[List[str]] = Query(default=[]),
    exclude_terms: Optional[List[str]] = Query(default=[]),
    any_terms: Optional[List[str]] = Query(default=[]),
):
    """Filters PDFs based on search terms and copies matching files to OUTPUT_DIR."""
    src_path = Path(src_directory)
    dest_path = Path(OUTPUT_DIR) / f"filtered_results_include-{'_'.join(include_terms)}_exclude-{'_'.join(exclude_terms)}_any-{'_'.join(any_terms)}"
    dest_path.mkdir(parents=True, exist_ok=True)
    
    if not src_path.exists() or not src_path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid source directory")
    
    pdf_files = list(src_path.rglob("*.pdf"))
    matched_files = 0
    
    for pdf_file in pdf_files:
        text = extract_text_from_pdf(pdf_file)
        if search_terms_in_text(text, include_terms, exclude_terms, any_terms):
            shutil.copy(str(pdf_file), str(dest_path / pdf_file.name))
            matched_files += 1
    
    return {"message": "Filtering complete", "matched_files": matched_files, "output_directory": str(dest_path)}
