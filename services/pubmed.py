import os
from utils.pubmed_utils import search_pubmed, extract_pmcids

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
   
   
#-------------------------------------------------------------------#
# import os
# from utils.pubmed_utils import search_pubmed, extract_pmcids

# async def fetch_pubmed_results(search_terms: list[str], max_results: int):
#     """Fetch PubMed results and ensure we gather the specified number of results."""
#     pmcids = []
#     page = 1

#     for term in search_terms:
#         while len(pmcids) < max_results:
#             html_content = search_pubmed(term, page)
#             if not html_content:
#                 break
#             new_pmcids = extract_pmcids(html_content)
#             pmcids.extend(new_pmcids)
            
#             # If the required number of PMCIDs is found, break out of the loop
#             if len(pmcids) >= max_results:
#                 pmcids = pmcids[:max_results]
#                 break

#             page += 1  # Increase the page number for the next search

#     return pmcids


# import os
# from utils.pubmed_utils import search_pubmed, extract_pmcids

# async def fetch_pubmed_results(search_terms: list[str], max_results: int):
#     """Fetch PubMed results and ensure we gather the specified number of results."""
#     pmcids = []
#     page = 1

#     for term in search_terms:
#         while len(pmcids) < max_results:
#             html_content = search_pubmed(term, page)
#             if not html_content:
#                 break
#             new_pmcids = extract_pmcids(html_content)
#             pmcids.extend(new_pmcids)
            
#             if len(pmcids) >= max_results:
#                 pmcids = pmcids[:max_results]
#                 break

#             page += 1

#     return pmcids[:max_results]  # Ensure exact number