import os
from utils.search_utils import download_google_scholar_pdf, search_google_scholar, extract_pdf_links
import asyncio

async def fetch_google_scholar_results(search_terms: list[str], max_results: int):
    """Fetches and downloads Google Scholar PDF links asynchronously."""
    pdf_links_with_metadata = set()  # Use a set of tuples (link, metadata) to avoid duplicates
    downloaded_files = []
    start = 0

    for term in search_terms:
        while len(downloaded_files) < max_results:
            print(f"Searching for: {term} - Start index: {start}")
            data = await asyncio.to_thread(search_google_scholar, term, start)
            if not data:
                print(f"No data returned for {term} at start {start}")
                break
            
            new_links_with_metadata = extract_pdf_links(data)
            print(f"Found {len(new_links_with_metadata)} new PDF links")
            
            for link_data in new_links_with_metadata:
                link_tuple = (link_data["link"], str(link_data["metadata"]))
                if link_tuple not in pdf_links_with_metadata:
                    pdf_links_with_metadata.add(link_tuple)
                    file_path, meta_path = await asyncio.to_thread(
                        download_google_scholar_pdf, 
                        link_data["link"], 
                        term,
                        link_data["metadata"]
                    )
                    if file_path and meta_path:
                        downloaded_files.append((file_path, link_data["metadata"]))
                        print(f"Downloaded: {file_path}")
                    else:
                        print(f"Failed to download: {link_data['link']}")
                    
                    await asyncio.sleep(0.5)

            if len(downloaded_files) >= max_results:
                print(f"Reached max downloads ({max_results}). Stopping.")
                break  

            start += 10
            await asyncio.sleep(1)

    print(f"Total PDF links found: {len(pdf_links_with_metadata)}")
    print(f"Total PDFs successfully downloaded: {len(downloaded_files)}")
    
    return downloaded_files[:max_results]