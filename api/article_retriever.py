

from enum import Enum
from fastapi import APIRouter, HTTPException, Query
from services.pubmed import fetch_pubmed_results
from services.google_scholar import fetch_google_scholar_results
from utils.search_utils import download_google_scholar_pdf
from utils.pubmed_utils import download_pdf
from utils.file_operations import rename_downloaded_files
import os
import json

router = APIRouter()

RECENT_SEARCHES_FILE = "recent_searches.json"

class SearchSourceEnum(str, Enum):
    google_scholar = "Google Scholar"
    pubmed = "PubMed"
    both = "BOTH"

def save_recent_search(search_data):
    """Save the latest search query in a temporary JSON file (stores last 10 searches)."""
    try:
        if os.path.exists(RECENT_SEARCHES_FILE):
            with open(RECENT_SEARCHES_FILE, "r") as file:
                recent_searches = json.load(file)
        else:
            recent_searches = {"recent_searches": []}

        recent_searches["recent_searches"].insert(0, search_data)
        recent_searches["recent_searches"] = recent_searches["recent_searches"][:10]

        with open(RECENT_SEARCHES_FILE, "w") as file:
            json.dump(recent_searches, file, indent=4)
    except Exception as e:
        print(f"Error saving recent search: {e}")

@router.get("/recent-searches")
async def get_recent_searches():
    """Retrieve the last 10 search queries."""
    try:
        if os.path.exists(RECENT_SEARCHES_FILE):
            with open(RECENT_SEARCHES_FILE, "r") as file:
                recent_searches = json.load(file)
            return recent_searches
        return {"recent_searches": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent searches: {e}")

@router.get("/search")
async def search_articles(
    search_terms: list[str] = Query(None, description="List of search terms"),
    search_operator: str = Query("OR", enum=["AND", "OR"], description="Search operation mode"),
    search_source: SearchSourceEnum = Query(SearchSourceEnum.both, description="Search source"),
    max_results: int = Query(10, ge=1, le=100)
):
    try:
        results = {"google_scholar": [], "pubmed": [], "stored_pdfs": []}

        if not search_terms or len(search_terms) == 0:
            raise HTTPException(status_code=400, detail="At least one search term is required.")

        if search_operator == "AND":
            combined_search_term = " AND ".join(search_terms)
            search_terms = [combined_search_term]
        elif search_operator == "OR":
            combined_search_term = " OR ".join(search_terms)
            search_terms = [search_terms[0]]

        selected_term = search_terms[0]
        search_data = {
            "search_terms": search_terms,
            "search_operator": search_operator,
            "search_source": search_source.value,
            "max_results": max_results
        }
        save_recent_search(search_data)

        if search_source == SearchSourceEnum.both:
            half_results = max_results // 2
            google_scholar_results = await fetch_google_scholar_results(search_terms, half_results + (max_results % 2))
            pubmed_results = await fetch_pubmed_results(search_terms, half_results)

            pubmed_pdfs = [
                download_pdf(pmcid, selected_term, search_source="BOTH") for pmcid in pubmed_results
            ]
            google_scholar_pdfs = [
                download_google_scholar_pdf(url, selected_term, search_source="BOTH") for url in google_scholar_results
            ]

            renamed_files = rename_downloaded_files(selected_term, "BOTH")

            results["google_scholar"] = google_scholar_results
            results["pubmed"] = pubmed_results
            results["stored_pdfs"] = renamed_files  # Return renamed files instead of original ones

        elif search_source == SearchSourceEnum.google_scholar:
            google_scholar_results = await fetch_google_scholar_results(search_terms, max_results)
            google_scholar_pdfs = [
                download_google_scholar_pdf(url, selected_term, search_source="Google Scholar") for url in google_scholar_results
            ]

            renamed_files = rename_downloaded_files(selected_term, "Google Scholar")

            results["google_scholar"] = google_scholar_results
            results["stored_pdfs"] = renamed_files  # Return renamed files instead of original ones

        elif search_source == SearchSourceEnum.pubmed:
            pubmed_results = await fetch_pubmed_results(search_terms, max_results)
            pubmed_pdfs = [
                download_pdf(pmcid, selected_term, search_source="PubMed") for pmcid in pubmed_results
            ]

            renamed_files = rename_downloaded_files(selected_term, "PubMed")

            results["pubmed"] = pubmed_results
            results["stored_pdfs"] = renamed_files  # Return renamed files instead of original ones

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
