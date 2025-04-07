import os
import logging
import re
import ast
import asyncio
from pathlib import Path
from typing import List, Dict

import fitz  # PyMuPDF
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Query

from services.pubmed import fetch_pubmed_results
from services.google_scholar import fetch_google_scholar_results
from utils.search_utils import download_google_scholar_pdf
from utils.pubmed_utils import download_pdf
from utils.file_operations import extract_text_in_chunks, get_categories, rename_downloaded_files, string_to_python_list, truncate_text_to_fit_token_limit
from run_analysis import run_openai_finding_keywords_for_search

# Load environment variables
load_dotenv(override=True)

router = APIRouter()
app = FastAPI()

BASE_DIR = Path("download")

# 1️⃣ Fetch folder structure dynamically
@router.get("/fetch-folder-structure")
def fetch_folder_structure(source: str = Query(..., enum=["Scholar", "pubmed"])):
    """Retrieve available categories for a given data source."""
    categories = get_categories(source)
    if not categories:
        raise HTTPException(status_code=404, detail="No categories found.")
    return {"source": source, "categories": list(categories.keys())}


# 2️⃣ Fetch PDFs within selected categories
@router.get("/fetch-articles")
def fetch_articles(
    source: str = Query(..., enum=["Scholar", "pubmed"]),
    categories: List[str] = Query(...)
):
    """Retrieve available PDFs in the selected categories."""
    selected_pdfs = {
        category: [f.name for f in (BASE_DIR / source / category).iterdir() if f.suffix == ".pdf"]
        for category in categories if (BASE_DIR / source / category).exists()
    }

    if not selected_pdfs:
        raise HTTPException(status_code=404, detail="No PDFs found.")
    
    return {"source": source, "selected_categories": selected_pdfs}



# 5️⃣ Analyze selected PDFs for keywords
@router.post("/analyze-common-words")
def analyze_common_words(
    source: str = Query(..., enum=["Scholar", "pubmed"]),
    categories: List[str] = Query(...),
    pdfs: List[str] = Query(...),
    num_matches: int = Query(10, ge=1, le=100)
):
    """Extract technical keywords from selected PDFs."""
    all_keywords = []

    for category in categories:
        pdf_dir = BASE_DIR / source / category

        for pdf in pdfs:
            pdf_path = pdf_dir / pdf
            if not pdf_path.exists():
                raise HTTPException(status_code=404, detail=f"PDF not found: {pdf}")

            text_chunks = extract_text_in_chunks(pdf_path, chunk_size=5000)
            
            for chunk in text_chunks:
                truncated_text = truncate_text_to_fit_token_limit(chunk, max_tokens=3000)
                raw_output = run_openai_finding_keywords_for_search(truncated_text)
                common_words = string_to_python_list(raw_output)
                all_keywords.extend(common_words)

    return {"common_words": list(set(all_keywords))[:num_matches]}


# 6️⃣ Fetch articles using analyzed keywords
@router.get("/analyse_common_words")
async def search_articles(
    search_terms: List[str] = Query(...),
    search_source: str = Query("Google Scholar", enum=["Google Scholar", "PubMed"]),
    max_results: int = Query(10, ge=1, le=100)
):
    """Fetch articles using extracted common words."""
    if not search_terms:
        raise HTTPException(status_code=400, detail="At least one search term is required.")

    selected_term = search_terms[0]
    folder_path = BASE_DIR / "common_word_analysis" / selected_term
    folder_path.mkdir(parents=True, exist_ok=True)

    results = {"google_scholar": [], "pubmed": [], "stored_pdfs": []}

    if search_source == "Google Scholar":
        google_scholar_results = await fetch_google_scholar_results(search_terms, max_results)
        google_scholar_pdfs = [
            download_google_scholar_pdf(url, folder_path, "Google Scholar") for url in google_scholar_results
        ]
        rename_downloaded_files(folder_path, "Google Scholar")
        results.update({"google_scholar": google_scholar_results, "stored_pdfs": google_scholar_pdfs})

    elif search_source == "PubMed":
        pubmed_results = await fetch_pubmed_results(search_terms, max_results)
        pubmed_pdfs = [
            download_pdf(pmcid, folder_path, "PubMed") for pmcid in pubmed_results
        ]
        rename_downloaded_files(folder_path, "PubMed")
        results.update({"pubmed": pubmed_results, "stored_pdfs": pubmed_pdfs})

    return results
