import os
from utils.search_utils import search_google_scholar, extract_pdf_links
import asyncio
from utils.search_utils import search_google_scholar, extract_pdf_links, download_google_scholar_pdf

# async def fetch_google_scholar_results(search_terms: list[str], max_results: int):

    # print('7777777777777')
    # """Fetches Google Scholar PDF links asynchronously."""
    # pdf_links = set()  # Use a set to avoid duplicates
    # start = 0

    # for term in search_terms:
    #     while len(pdf_links) < max_results+5:
    #         data = await asyncio.to_thread(search_google_scholar, term, start)  # Run sync function in thread
    #         if not data:
    #             break  # Stop if we get no data
            
    #         new_links = set(extract_pdf_links(data))  # Convert to set to avoid adding duplicates

    #         pdf_links.update(new_links)

    #         # Stop when we reach max_results
    #         if len(pdf_links) >= max_results:
    #             break  

    #         start += 10
    #         await asyncio.sleep(1)  # Delay to avoid rate limiting

    # return list(pdf_links)[:max_results]  # Convert set back to list
    
    # Modified fetch_google_scholar_results function for google_scholor.py
async def fetch_google_scholar_results(search_terms: list[str], max_results: int):
    """Fetches and downloads Google Scholar PDF links asynchronously."""
    pdf_links = set()  # Use a set to avoid duplicates
    downloaded_files = []
    start = 0

    for term in search_terms:
        while len(pdf_links) < max_results+5:
            print(f"Searching for: {term} - Start index: {start}")
            data = await asyncio.to_thread(search_google_scholar, term, start)  # Run sync function in thread
            if not data:
                print(f"No data returned for {term} at start {start}")
                break  # Stop if we get no data
            
            new_links = set(extract_pdf_links(data))  # Convert to set to avoid adding duplicates
            print(f"Found {len(new_links)} new PDF links")
            
            pdf_links.update(new_links)

            # Download the newly found PDFs
            for link in new_links:
                file_path = await asyncio.to_thread(download_google_scholar_pdf, link, term)
                if file_path:
                    downloaded_files.append(file_path)
                    print(f"Downloaded: {file_path}")
                else:
                    print(f"Failed to download: {link}")
                
                # Add a small delay between downloads to avoid rate limiting
                await asyncio.sleep(0.5)

            # Stop when we reach max_results for downloads
            if len(downloaded_files) >= max_results:
                print(f"Reached max downloads ({max_results}). Stopping.")
                break  

            start += 10
            await asyncio.sleep(1)  # Delay to avoid rate limiting

    print(f"Total PDF links found: {len(pdf_links)}")
    print(f"Total PDFs successfully downloaded: {len(downloaded_files)}")
    
    return downloaded_files[:max_results]  # Return the list of downloaded file paths