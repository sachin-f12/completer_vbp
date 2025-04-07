from enum import Enum
from fastapi import APIRouter, HTTPException, Query
import os
import json
from services.pubmed import fetch_pubmed_results
from services.google_scholar import fetch_google_scholar_results
from utils.search_utils import download_google_scholar_pdf
from utils.pubmed_utils import download_pdf
from utils.file_operations import rename_downloaded_files

router = APIRouter()
RECENT_SEARCHES_FILE = "recent_searches.json"

class SearchSourceEnum(str, Enum):
    GOOGLE_SCHOLAR = "Google Scholar"
    PUBMED = "PubMed"
    BOTH = "BOTH"

def save_recent_search(search_data: dict):
    """Save the latest search query in a JSON file (stores last 10 searches)."""
    try:
        recent_searches = {"recent_searches": []}
        if os.path.exists(RECENT_SEARCHES_FILE):
            with open(RECENT_SEARCHES_FILE, "r") as file:
                recent_searches = json.load(file)

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
                return json.load(file)
        return {"recent_searches": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent searches: {e}")

@router.get("/search")
async def search_articles(
    search_terms: list[str] = Query(..., description="List of search terms"),
    search_operator: str = Query("AND", enum=["AND", "OR"], description="Search operation mode"),
    search_source: SearchSourceEnum = Query(SearchSourceEnum.BOTH, description="Search source"),
    max_results: int = Query(10, ge=1, le=100)
):
    try:
        if not search_terms:
            raise HTTPException(status_code=400, detail="At least one search term is required.")

        combined_search_term = f" {search_operator} ".join(search_terms)
        search_data = {
            "search_terms": search_terms,
            "search_operator": search_operator,
            "search_source": search_source.value,
            "max_results": max_results
        }
        save_recent_search(search_data)

        results = {"google_scholar": [], "pubmed": [], "stored_pdfs": []}

        if search_source in [SearchSourceEnum.BOTH, SearchSourceEnum.GOOGLE_SCHOLAR]:
            gs_results = await fetch_google_scholar_results([combined_search_term], max_results // (2 if search_source == SearchSourceEnum.BOTH else 1))
            gs_pdfs = [download_google_scholar_pdf(url, combined_search_term, metadata, search_source.value) for url, metadata in gs_results]
            renamed_gs_files = rename_downloaded_files(combined_search_term, search_source.value)
            results["google_scholar"] = [f for f in renamed_gs_files if f.endswith('.pdf')]
            results["stored_pdfs"].extend(renamed_gs_files)

        if search_source in [SearchSourceEnum.BOTH, SearchSourceEnum.PUBMED]:
            pm_results = await fetch_pubmed_results([combined_search_term], max_results // (2 if search_source == SearchSourceEnum.BOTH else 1))
            pm_pdfs = [download_pdf(pmcid, combined_search_term, search_source.value) for pmcid in pm_results]
            renamed_pm_files = rename_downloaded_files(combined_search_term, search_source.value)
            results["pubmed"] = pm_results
            results["stored_pdfs"].extend(renamed_pm_files)

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
