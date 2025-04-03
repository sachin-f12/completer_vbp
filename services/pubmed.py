import os
from utils.pubmed_utils import search_pubmed, extract_pmcids,download_pdf

async def fetch_pubmed_results(search_terms: list[str], max_results: int):
    """PubMed se PDFs fetch karne ka function."""
    pmcids = []
    page = 1

    for term in search_terms:
        while len(pmcids) < max_results:
            html_content = search_pubmed(term, page)
            if not html_content:
                break
            new_pmcids = extract_pmcids(html_content)
            pmcids.extend(new_pmcids[:max_results])
            page += 1

    return pmcids

async def fetch_pubmed_results_last(search_terms: list[str], max_results: int):
    """Fetch PMC IDs from PubMed."""
    print("[DEBUG] Fetching PubMed results...")
    pmcids = set()  # Use a set to prevent duplicates
    for term in search_terms:
        page = 1
        while len(pmcids) < max_results:
            print(f"[DEBUG] Searching PubMed: term={term}, page={page}")
            html_content = search_pubmed(term, page)  # Fetch HTML content from PubMed
            if not html_content:
                print("[DEBUG] No HTML content returned from PubMed. Exiting loop.")
                break

            new_pmcids = extract_pmcids(html_content)  # Extract PMC IDs
            if not new_pmcids:  # If no new results, stop the loop
                print(f"[DEBUG] No PMCIDs found on page {page}. Stopping search.")
                break

            for pmcid in new_pmcids:
                if len(pmcids) < max_results:
                    pmcids.add(pmcid)
                else:
                    break

            page += 1  # Move to the next page

        if len(pmcids) >= max_results:
            break  # Stop if we have enough results

    print(f"[DEBUG] Found PubMed PMCIDs: {pmcids}")
    return list(pmcids)
