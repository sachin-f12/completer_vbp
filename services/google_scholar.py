


# # grok code
# import asyncio
# from utils.search_utils import download_google_scholar_pdf, search_google_scholar, extract_pdf_links
# async def fetch_google_scholar_results(search_terms: list[str], max_results: int, search_source: str = "Google Scholar"):
#     """Fetches and downloads Google Scholar PDF links asynchronously."""
#     pdf_links_with_metadata = set()  # Avoid duplicates
#     downloaded_files = []

#     async def process_term(term):
#         nonlocal downloaded_files
#         start = 0
#         while len(downloaded_files) < max_results:
#             data = await search_google_scholar(term, start)
#             if not data:
#                 break

#             new_links_with_metadata = extract_pdf_links(data)
#             tasks = []
#             for link_data in new_links_with_metadata:
#                 link_tuple = (link_data["link"], str(link_data["metadata"]))
#                 if link_tuple not in pdf_links_with_metadata and len(downloaded_files) < max_results:
#                     pdf_links_with_metadata.add(link_tuple)
#                     tasks.append(download_google_scholar_pdf(
#                         link_data["link"],
#                         term,
#                         link_data["metadata"],
#                         search_source=search_source
#                     ))

#             if tasks:
#                 results = await asyncio.gather(*tasks, return_exceptions=True)
#                 for result in results:
#                     if isinstance(result, tuple) and result[0] and result[1]:
#                         downloaded_files.append(result)

#             if len(downloaded_files) >= max_results:
#                 break
#             start += 10
#             await asyncio.sleep(1)

#     await asyncio.gather(*(process_term(term) for term in search_terms))
#     return downloaded_files[:max_results]


# import asyncio
# from utils.search_utils import download_google_scholar_pdf, search_google_scholar, extract_pdf_links

# async def fetch_google_scholar_results(search_terms: list[str], max_results: int, search_source: str = "Google Scholar"):
#     """Fetches and downloads Google Scholar PDF links asynchronously."""
#     pdf_links_with_metadata = set()  # Avoid duplicates
#     downloaded_files = []
#     async def process_term(term):
#         nonlocal downloaded_files
#         start = 0
#         while len(downloaded_files) < max_results:
#             data = await search_google_scholar(term, start)
#             if not data:
#                 break

#             new_links_with_metadata = extract_pdf_links(data)
#             tasks = []
#             for link_data in new_links_with_metadata:
#                 link_tuple = (link_data["link"], str(link_data["metadata"]))
#                 if link_tuple not in pdf_links_with_metadata and len(downloaded_files) < max_results:
#                     pdf_links_with_metadata.add(link_tuple)
#                     tasks.append(download_google_scholar_pdf(
#                         link_data["link"],
#                         term,
#                         link_data["metadata"],
#                         search_source=search_source
#                     ))

#             if tasks:
#                 results = await asyncio.gather(*tasks, return_exceptions=True)
#                 downloaded_files.extend([r for r in results if isinstance(r, tuple) and r[0] and r[1]])

#             if len(downloaded_files) >= max_results:
#                 break
#             start += 10
#             await asyncio.sleep(0.5)  # Reduced sleep time for faster processing

#     await asyncio.gather(*(process_term(term) for term in search_terms))
#     return downloaded_files[:max_results]



import asyncio
from utils.search_utils import download_google_scholar_pdf, search_google_scholar, extract_pdf_links

async def fetch_google_scholar_results(search_terms: list[str], max_results: int, search_source: str = "Google Scholar"):
    """Fetches and downloads Google Scholar PDF links asynchronously."""
    pdf_links_with_metadata = set()  # Avoid duplicates
    downloaded_files = []
    
    print(f"Starting fetch for {max_results} results from {search_source} with terms: {search_terms}")

    async def process_term(term):
        nonlocal downloaded_files
        start = 0
        while len(downloaded_files) < max_results:
            print(f"Searching Google Scholar for term '{term}', start: {start}")
            data = await search_google_scholar(term, start)
            if not data:
                print(f"No more data returned for term '{term}'")
                break

            new_links_with_metadata = extract_pdf_links(data)
            print(f"Extracted {len(new_links_with_metadata)} PDF links for term '{term}'")
            
            tasks = []
            for link_data in new_links_with_metadata:
                link_tuple = (link_data["link"], str(link_data["metadata"]))
                if link_tuple not in pdf_links_with_metadata and len(downloaded_files) < max_results:
                    pdf_links_with_metadata.add(link_tuple)
                    tasks.append(download_google_scholar_pdf(
                        link_data["link"],
                        term,
                        link_data["metadata"],
                        search_source=search_source
                    ))

            if tasks:
                print(f"Starting download of {len(tasks)} PDFs for term '{term}'")
                results = await asyncio.gather(*tasks, return_exceptions=True)
                valid_results = [r for r in results if isinstance(r, tuple) and r[0] and r[1]]
                downloaded_files.extend(valid_results)
                print(f"Downloaded {len(valid_results)} PDFs, total now: {len(downloaded_files)}")

            if len(downloaded_files) >= max_results:
                print(f"Reached target of {max_results} downloads for term '{term}'")
                break
            start += 10
            await asyncio.sleep(0.2)  # Reduced sleep time further for speed

    await asyncio.gather(*(process_term(term) for term in search_terms))
    print(f"Fetch complete. Returning {len(downloaded_files[:max_results])} results")
    return downloaded_files[:max_results]