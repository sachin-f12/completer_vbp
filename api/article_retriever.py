
# from enum import Enum
# from fastapi import APIRouter, HTTPException, Query
# from services.pubmed import fetch_pubmed_results
# from services.google_scholar import fetch_google_scholar_results
# from utils.search_utils import download_google_scholar_pdf
# from utils.pubmed_utils import download_pdf
# from utils.file_operations import rename_downloaded_files
# import os
# import json
# from pathlib import Path
# import asyncio

# router = APIRouter()

# RECENT_SEARCHES_FILE = "recent_searches.json"

# class SearchSourceEnum(str, Enum):
#     google_scholar = "Google Scholar"
#     pubmed = "PubMed"
#     both = "BOTH"

# def save_recent_search(search_data):
#     """Save the latest search query in a temporary JSON file (stores last 10 searches)."""
#     try:
#         if os.path.exists(RECENT_SEARCHES_FILE):
#             with open(RECENT_SEARCHES_FILE, "r") as file:
#                 recent_searches = json.load(file)
#         else:
#             recent_searches = {"recent_searches": []}

#         recent_searches["recent_searches"].insert(0, search_data)
#         recent_searches["recent_searches"] = recent_searches["recent_searches"][:10]

#         with open(RECENT_SEARCHES_FILE, "w") as file:
#             json.dump(recent_searches, file, indent=4)
#     except Exception as e:
#         print(f"Error saving recent search: {e}")

# @router.get("/recent-searches")
# async def get_recent_searches():
#     """Retrieve the last 10 search queries."""
#     try:
#         if os.path.exists(RECENT_SEARCHES_FILE):
#             with open(RECENT_SEARCHES_FILE, "r") as file:
#                 recent_searches = json.load(file)
#             return recent_searches
#         return {"recent_searches": []}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching recent searches: {e}")

# @router.get("/search")
# async def search_articles(
#     search_terms: list[str] = Query(None, description="List of search terms"),
#     search_operator: str = Query("AND", enum=["AND", "OR"], description="Search operation mode"),
#     search_source: SearchSourceEnum = Query(SearchSourceEnum.both, description="Search source"),
#     max_results: int = Query(10, ge=1, le=100)
# ):
#     try:
#         results = {"google_scholar": [], "pubmed": [], "stored_pdfs": []}

#         if not search_terms:
#             raise HTTPException(status_code=400, detail="At least one search term is required.")

#         combined_search_term = f" {search_operator} ".join(search_terms)
#         selected_term = combined_search_term
#         search_source_str = search_source.value

#         search_data = {
#             "search_terms": search_terms,
#             "search_operator": search_operator,
#             "search_source": search_source_str,
#             "max_results": max_results
#         }
#         save_recent_search(search_data)

#         if search_source == SearchSourceEnum.both:
#             half_results = max_results // 2
#             gs_task = fetch_google_scholar_results([combined_search_term], half_results + (max_results % 2), search_source="BOTH")

#             pubmed_task = fetch_pubmed_results([combined_search_term], half_results)
#             google_scholar_results, pubmed_results = await asyncio.gather(gs_task, pubmed_task)

#             pubmed_pdfs = await asyncio.gather(
#                 *[asyncio.to_thread(download_pdf, pmcid, selected_term, search_source="BOTH") for pmcid in pubmed_results]
#             )
#             google_scholar_pdfs = [result[0] for result in google_scholar_results if result[0]]

#             renamed_files = rename_downloaded_files(selected_term, "BOTH")
#             renamed_gs_files = [f for f in renamed_files if f.endswith('.pdf') and "Scholar" in f]

#             results.update({
#                 "google_scholar": renamed_gs_files,
#                 "pubmed": pubmed_results,
#                 "stored_pdfs": renamed_files
#             })

#         elif search_source == SearchSourceEnum.google_scholar:
#             google_scholar_results = await fetch_google_scholar_results([combined_search_term], max_results, search_source="Google Scholar")
#             google_scholar_pdfs = [result[0] for result in google_scholar_results if result[0]]

#             renamed_files = rename_downloaded_files(selected_term, "Google Scholar")
#             renamed_gs_files = [f for f in renamed_files if f.endswith('.pdf')]

#             results.update({
#                 "google_scholar": renamed_gs_files,
#                 "stored_pdfs": renamed_files
#             })

#         elif search_source == SearchSourceEnum.pubmed:
#             pubmed_results = await fetch_pubmed_results([combined_search_term], max_results)
#             pubmed_pdfs = await asyncio.gather(
#                 *[asyncio.to_thread(download_pdf, pmcid, selected_term, search_source="PubMed") for pmcid in pubmed_results]
#             )

#             renamed_files = rename_downloaded_files(selected_term, "PubMed")
#             results.update({
#                 "pubmed": pubmed_results,
#                 "stored_pdfs": renamed_files
#             })

#         return results
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
    
# from enum import Enum
# from fastapi import APIRouter, HTTPException, Query
# from services.pubmed import fetch_pubmed_results
# from services.google_scholar import fetch_google_scholar_results
# from utils.search_utils import download_google_scholar_pdf
# from utils.pubmed_utils import download_pdf
# from utils.file_operations import rename_downloaded_files
# import os
# import json
# from pathlib import Path
# import asyncio

# router = APIRouter()

# RECENT_SEARCHES_FILE = "recent_searches.json"

# class SearchSourceEnum(str, Enum):
#     google_scholar = "Google Scholar"
#     pubmed = "PubMed"
#     both = "BOTH"

# def save_recent_search(search_data):
#     try:
#         if os.path.exists(RECENT_SEARCHES_FILE):
#             with open(RECENT_SEARCHES_FILE, "r") as file:
#                 recent_searches = json.load(file)
#         else:
#             recent_searches = {"recent_searches": []}

#         recent_searches["recent_searches"].insert(0, search_data)
#         recent_searches["recent_searches"] = recent_searches["recent_searches"][:10]

#         with open(RECENT_SEARCHES_FILE, "w") as file:
#             json.dump(recent_searches, file, indent=4)
#     except Exception as e:
#         print(f"Error saving recent search: {e}")

# @router.get("/recent-searches")
# async def get_recent_searches():
#     try:
#         if os.path.exists(RECENT_SEARCHES_FILE):
#             with open(RECENT_SEARCHES_FILE, "r") as file:
#                 recent_searches = json.load(file)
#             return recent_searches
#         return {"recent_searches": []}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching recent searches: {e}")

# @router.get("/search")
# async def search_articles(
#     search_terms: list[str] = Query(None, description="List of search terms"),
#     search_operator: str = Query("AND", enum=["AND", "OR"], description="Search operation mode"),
#     search_source: SearchSourceEnum = Query(SearchSourceEnum.both, description="Search source"),
#     max_results: int = Query(10, ge=1, le=100)
# ):
#     try:
#         results = {"google_scholar": [], "pubmed": [], "stored_pdfs": []}

#         if not search_terms:
#             raise HTTPException(status_code=400, detail="At least one search term is required.")

#         combined_search_term = f" {search_operator} ".join(search_terms)
#         selected_term = combined_search_term
#         search_source_str = search_source.value

#         search_data = {
#             "search_terms": search_terms,
#             "search_operator": search_operator,
#             "search_source": search_source_str,
#             "max_results": max_results
#         }
#         save_recent_search(search_data)

#         if search_source == SearchSourceEnum.both:
#             half_results = max_results // 2
#             gs_task = fetch_google_scholar_results([combined_search_term], half_results + (max_results % 2), search_source="BOTH")
#             pubmed_task = fetch_pubmed_results([combined_search_term], half_results)
#             google_scholar_results, pubmed_results = await asyncio.gather(gs_task, pubmed_task)

#             # Process PubMed downloads with exact count
#             pubmed_pdfs = await asyncio.gather(
#                 *[asyncio.to_thread(download_pdf, pmcid, selected_term, search_source="BOTH") 
#                   for pmcid in pubmed_results[:half_results]]
#             )
#             google_scholar_pdfs = [result[0] for result in google_scholar_results[:half_results + (max_results % 2)] if result[0]]

#             renamed_files = rename_downloaded_files(selected_term, "BOTH")
#             renamed_gs_files = [f for f in renamed_files if "Scholar" in f and f.endswith('.pdf')]
#             renamed_pm_files = [f for f in renamed_files if "PubMed" in f and f.endswith('.pdf')]

#             results.update({
#                 "google_scholar": renamed_gs_files,
#                 "pubmed": renamed_pm_files,
#                 "stored_pdfs": renamed_files
#             })

#         elif search_source == SearchSourceEnum.google_scholar:
#             google_scholar_results = await fetch_google_scholar_results([combined_search_term], max_results, search_source="Google Scholar")
#             google_scholar_pdfs = [result[0] for result in google_scholar_results[:max_results] if result[0]]

#             renamed_files = rename_downloaded_files(selected_term, "Google Scholar")
#             renamed_gs_files = [f for f in renamed_files if f.endswith('.pdf')]

#             results.update({
#                 "google_scholar": renamed_gs_files,
#                 "stored_pdfs": renamed_files
#             })

#         elif search_source == SearchSourceEnum.pubmed:
#             pubmed_results = await fetch_pubmed_results([combined_search_term], max_results)
#             pubmed_pdfs = await asyncio.gather(
#                 *[asyncio.to_thread(download_pdf, pmcid, selected_term, search_source="PubMed") 
#                   for pmcid in pubmed_results[:max_results]]
#             )

#             renamed_files = rename_downloaded_files(selected_term, "PubMed")
#             renamed_pm_files = [f for f in renamed_files if f.endswith('.pdf')]

#             results.update({
#                 "pubmed": renamed_pm_files,
#                 "stored_pdfs": renamed_files
#             })

#         return results
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")



from enum import Enum
from fastapi import APIRouter, HTTPException, Query
from services.pubmed import fetch_pubmed_results
from services.google_scholar import fetch_google_scholar_results
from utils.search_utils import download_google_scholar_pdf
from utils.pubmed_utils import download_pdf
from utils.file_operations import rename_downloaded_files
import os
import json
from pathlib import Path
import asyncio

router = APIRouter()

RECENT_SEARCHES_FILE = "recent_searches.json"

class SearchSourceEnum(str, Enum):
    google_scholar = "Google Scholar"
    pubmed = "PubMed"
    both = "BOTH"

def save_recent_search(search_data):
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
    try:
        if os.path.exists(RECENT_SEARCHES_FILE):
            with open(RECENT_SEARCHES_FILE, "r") as file:
                recent_searches = json.load(file)
            return recent_searches
        return {"recent_searches": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent searches: {e}")

async def download_pubmed_pdfs_limited(pmcids, search_term, search_source, max_results, concurrency_limit=5):
    """Download PubMed PDFs with a concurrency limit."""
    semaphore = asyncio.Semaphore(concurrency_limit)
    async def limited_download(pmcid):
        async with semaphore:
            return await asyncio.to_thread(download_pdf, pmcid, search_term, search_source)
    
    tasks = [limited_download(pmcid) for pmcid in pmcids[:max_results]]
    return await asyncio.gather(*tasks, return_exceptions=True)

@router.get("/search")
async def search_articles(
    search_terms: list[str] = Query(None, description="List of search terms"),
    search_operator: str = Query("AND", enum=["AND", "OR"], description="Search operation mode"),
    search_source: SearchSourceEnum = Query(SearchSourceEnum.both, description="Search source"),
    max_results: int = Query(10, ge=1, le=100)
):
    try:
        results = {"google_scholar": [], "pubmed": [], "stored_pdfs": []}

        if not search_terms:
            raise HTTPException(status_code=400, detail="At least one search term is required.")

        combined_search_term = f" {search_operator} ".join(search_terms)
        selected_term = combined_search_term
        search_source_str = search_source.value

        search_data = {
            "search_terms": search_terms,
            "search_operator": search_operator,
            "search_source": search_source_str,
            "max_results": max_results
        }
        save_recent_search(search_data)

        if search_source == SearchSourceEnum.both:
            half_results = max_results // 2
            gs_task = fetch_google_scholar_results([combined_search_term], half_results + (max_results % 2), search_source="BOTH")
            pubmed_task = fetch_pubmed_results([combined_search_term], half_results)
            google_scholar_results, pubmed_results = await asyncio.gather(gs_task, pubmed_task)

            # Controlled PubMed downloads
            pubmed_pdfs = await download_pubmed_pdfs_limited(pubmed_results, selected_term, "BOTH", half_results)
            google_scholar_pdfs = [result[0] for result in google_scholar_results[:half_results + (max_results % 2)] if result[0]]

            renamed_files = rename_downloaded_files(selected_term, "BOTH")
            renamed_gs_files = [f for f in renamed_files if "Scholar" in f and f.endswith('.pdf')]
            renamed_pm_files = [f for f in renamed_files if "PubMed" in f and f.endswith('.pdf')]

            results.update({
                "google_scholar": renamed_gs_files,
                "pubmed": renamed_pm_files,
                "stored_pdfs": renamed_files
            })

        elif search_source == SearchSourceEnum.google_scholar:
            google_scholar_results = await fetch_google_scholar_results([combined_search_term], max_results, search_source="Google Scholar")
            google_scholar_pdfs = [result[0] for result in google_scholar_results[:max_results] if result[0]]

            renamed_files = rename_downloaded_files(selected_term, "Google Scholar")
            renamed_gs_files = [f for f in renamed_files if f.endswith('.pdf')]

            results.update({
                "google_scholar": renamed_gs_files,
                "stored_pdfs": renamed_files
            })

        elif search_source == SearchSourceEnum.pubmed:
            pubmed_results = await fetch_pubmed_results([combined_search_term], max_results)
            pubmed_pdfs = await download_pubmed_pdfs_limited(pubmed_results, selected_term, "PubMed", max_results)

            renamed_files = rename_downloaded_files(selected_term, "PubMed")
            renamed_pm_files = [f for f in renamed_files if f.endswith('.pdf')]

            results.update({
                "pubmed": renamed_pm_files,
                "stored_pdfs": renamed_files
            })

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")