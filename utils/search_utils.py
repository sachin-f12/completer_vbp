# # grok code
# import os
# import requests
# import logging
# import asyncio
# import aiohttp  # Added missing import
# from pathlib import Path
# from dotenv import load_dotenv
# from utils.file_operations import sanitize_filename

# load_dotenv()
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# OUTPUT_DIR = Path("download/Scholar")
# OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
# USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
# CHUNK_SIZE = 1024
# RETRIES = 1
# BACKOFF_FACTOR = 0.1

# async def search_google_scholar(keyword, start=0):
#     """Searches Google Scholar using SerpAPI synchronously (wrapped in async)."""
#     url = "https://serpapi.com/search"
#     params = {
#         "engine": "google_scholar",
#         "q": keyword,
#         "api_key": os.getenv("SERP_API_KEY"),
#         "start": start
#     }
#     try:
#         response = await asyncio.to_thread(requests.get, url, params=params)
#         response.raise_for_status()
#         return response.json()
#     except Exception as e:
#         logging.error(f"Error in search_google_scholar: {e}")
#         return None

# def extract_pdf_links(data):
#     """Extracts valid PDF links and metadata from search results."""
#     links_with_metadata = []
#     if not data or "organic_results" not in data:
#         logging.warning("No organic results found in data")
#         return links_with_metadata

#     for result in data.get("organic_results", []):
#         metadata = {
#             "title": result.get("title", "Unknown Title"),
#             "authors": result.get("publication_info", {}).get("authors", "Unknown Authors"),
#             "year": result.get("publication_info", {}).get("year", "Unknown Year"),
#             "source": result.get("publication_info", {}).get("summary", "Unknown Source")
#         }

#         for resource in result.get("resources", []):
#             link = resource.get("link", "")
#             if resource.get("file_format") == "PDF" and link.lower().endswith(".pdf"):
#                 links_with_metadata.append({
#                     "link": link,
#                     "metadata": metadata
#                 })

#     logging.info(f"Extracted {len(links_with_metadata)} valid PDF links")
#     return links_with_metadata



# async def download_google_scholar_pdf(pdf_url, search_term, metadata, search_source="Google Scholar"):
#     """Downloads the PDF and saves metadata asynchronously."""
#     safe_search_term = sanitize_filename(search_term).replace(".pdf", "")
    
#     if search_source.lower() == "both":
#         output_dir = Path(f"download/Both/Scholar/{safe_search_term}")
#     else:
#         output_dir = Path(f"download/Scholar/{safe_search_term}")
    
#     os.makedirs(output_dir, exist_ok=True)

#     pdf_filename = sanitize_filename(pdf_url.split("/")[-1].split("?")[0])
#     pdf_path = output_dir / pdf_filename
#     metadata_path = pdf_path.with_suffix('.txt')

#     if pdf_path.exists() and pdf_path.stat().st_size > 1000:
#         logging.info(f"PDF already exists: {pdf_path}")
#         return str(pdf_path), str(metadata_path)

#     for attempt in range(RETRIES):
#         try:
#             headers = {'User-Agent': USER_AGENT, 'Accept': 'application/pdf'}
#             async with aiohttp.ClientSession() as session:
#                 async with session.get(pdf_url, headers=headers, timeout=30) as response:
#                     response.raise_for_status()

#                     content_type = response.headers.get("Content-Type", "").lower()
#                     if "pdf" not in content_type:
#                         logging.warning(f"Skipped non-PDF file (Content-Type: {content_type}) from {pdf_url}")
#                         return None, None

#                     content = await response.read()


#             with open(pdf_path, 'wb') as f:
#                 f.write(content)

#             if pdf_path.stat().st_size < 1000:
#                 pdf_path.unlink()
#                 logging.error(f"Downloaded file too small: {pdf_url}")
#                 return None, None

#             with open(metadata_path, 'w', encoding='utf-8') as meta_file:
#                 meta_file.write(f"Title: {metadata['title']}\n")
#                 meta_file.write(f"Authors: {metadata['authors']}\n")
#                 meta_file.write(f"Year: {metadata['year']}\n")
#                 meta_file.write(f"Source: {metadata['source']}\n")
#                 meta_file.write(f"URL: {pdf_url}\n")

#             logging.info(f"Successfully downloaded PDF and metadata: {pdf_path}")
#             return str(pdf_path), str(metadata_path)

#         except Exception as e:
#             logging.error(f"Attempt {attempt + 1} failed for {pdf_url}: {e}")
#             if attempt < RETRIES - 1:
#                 await asyncio.sleep(BACKOFF_FACTOR * (2 ** attempt))
#             else:
#                 return None, None


# # grok code
# import os
# import requests
# import logging
# import asyncio
# import aiohttp
# from pathlib import Path
# from dotenv import load_dotenv
# from utils.file_operations import sanitize_filename

# load_dotenv()
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# OUTPUT_DIR = Path("download/Scholar")
# OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
# CHUNK_SIZE = 1024
# RETRIES = 1
# BACKOFF_FACTOR = 0.1


# async def search_google_scholar(keyword, start=0):
#     """Searches Google Scholar using SerpAPI synchronously (wrapped in async)."""
#     url = "https://serpapi.com/search"
#     params = {
#         "engine": "google_scholar",
#         "q": keyword,
#         "api_key": os.getenv("SERP_API_KEY"),
#         "start": start
#     }
#     try:
#         response = await asyncio.to_thread(requests.get, url, params=params)
#         response.raise_for_status()
#         return response.json()
#     except Exception as e:
#         logging.error(f"Error in search_google_scholar: {e}")
#         return None


# def extract_pdf_links(data):
#     """Extracts valid PDF links and metadata from search results."""
#     links_with_metadata = []
#     if not data or "organic_results" not in data:
#         logging.warning("No organic results found in data")
#         return links_with_metadata

#     for result in data.get("organic_results", []):
#         metadata = {
#             "title": result.get("title", "Unknown Title"),
#             "authors": result.get("publication_info", {}).get("authors", "Unknown Authors"),
#             "year": result.get("publication_info", {}).get("year", "Unknown Year"),
#             "source": result.get("publication_info", {}).get("summary", "Unknown Source")
#         }

#         for resource in result.get("resources", []):
#             link = resource.get("link", "")
#             if resource.get("file_format") == "PDF" and link.lower().endswith(".pdf"):
#                 links_with_metadata.append({
#                     "link": link,
#                     "metadata": metadata
#                 })

#     logging.info(f"Extracted {len(links_with_metadata)} valid PDF links")
#     return links_with_metadata


# async def download_google_scholar_pdf(pdf_url, search_term, metadata, search_source="Google Scholar"):
#     """Downloads the PDF and saves metadata asynchronously with standardized paths and naming."""
#     safe_search_term = sanitize_filename(search_term).replace(".pdf", "")

#     # Determine correct storage path
#     if search_source == "BOTH":
#         output_dir = Path(f"download/Both/Scholar/{safe_search_term}")
#     else:
#         output_dir = Path(f"download/Scholar/{safe_search_term}")

#     output_dir.mkdir(parents=True, exist_ok=True)
# # Generate next available filename like 1.pdf, 2.pdf...
#     existing_pdfs = sorted(output_dir.glob("*.pdf"), key=os.path.getctime)
#     next_index = len(existing_pdfs) + 1

#     pdf_path = output_dir / f"{next_index}.pdf"
#     metadata_path = output_dir / f"{next_index}.txt"


#     if pdf_path.exists() and pdf_path.stat().st_size > 1000:
#         logging.info(f"PDF already exists: {pdf_path}")
#         return str(pdf_path), str(metadata_path)

#     for attempt in range(RETRIES):
#         try:
#             headers = {'User-Agent': USER_AGENT, 'Accept': 'application/pdf'}
#             async with aiohttp.ClientSession() as session:
#                 async with session.get(pdf_url, headers=headers, timeout=30) as response:
#                     response.raise_for_status()

#                     content_type = response.headers.get("Content-Type", "").lower()
#                     if "pdf" not in content_type:
#                         logging.warning(f"Skipped non-PDF file (Content-Type: {content_type}) from {pdf_url}")
#                         return None, None

#                     content = await response.read()

#             with open(pdf_path, 'wb') as f:
#                 f.write(content)

#             if pdf_path.stat().st_size < 1000:
#                 pdf_path.unlink()
#                 logging.error(f"Downloaded file too small: {pdf_url}")
#                 return None, None

#             with open(metadata_path, 'w', encoding='utf-8') as meta_file:
#                 meta_file.write(f"Title: {metadata.get('title', 'N/A')}\n")
#                 meta_file.write(f"Authors: {metadata.get('authors', 'N/A')}\n")
#                 meta_file.write(f"Year: {metadata.get('year', 'N/A')}\n")
#                 meta_file.write(f"Source: {metadata.get('source', 'N/A')}\n")
#                 meta_file.write(f"URL: {pdf_url}\n")

#             logging.info(f"Successfully downloaded PDF and metadata: {pdf_path}")
#             return str(pdf_path), str(metadata_path)

#         except Exception as e:
#             logging.error(f"Attempt {attempt + 1} failed for {pdf_url}: {e}")
#             if attempt < RETRIES - 1:
#                 await asyncio.sleep(BACKOFF_FACTOR * (2 ** attempt))
#             else:
#                 return None, None


# import os
# import requests
# import logging
# import asyncio
# import aiohttp
# from pathlib import Path
# from dotenv import load_dotenv
# from utils.file_operations import sanitize_filename

# load_dotenv()
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# OUTPUT_DIR = Path("download/Scholar")
# OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
# CHUNK_SIZE = 8192  # Increased for faster downloads
# RETRIES = 2  # Increased retries
# BACKOFF_FACTOR = 0.1

# async def search_google_scholar(keyword, start=0):
#     url = "https://serpapi.com/search"
#     params = {
#         "engine": "google_scholar",
#         "q": keyword,
#         "api_key": os.getenv("SERP_API_KEY"),
#         "start": start
#     }
#     try:
#         response = await asyncio.to_thread(requests.get, url, params=params)
#         response.raise_for_status()
#         return response.json()
#     except Exception as e:
#         logging.error(f"Error in search_google_scholar: {e}")
#         return None

# def extract_pdf_links(data):
#     links_with_metadata = []
#     if not data or "organic_results" not in data:
#         return links_with_metadata

#     for result in data.get("organic_results", []):
#         metadata = {
#             "title": result.get("title", "Unknown Title"),
#             "authors": result.get("publication_info", {}).get("authors", "Unknown Authors"),
#             "year": result.get("publication_info", {}).get("year", "Unknown Year"),
#             "source": result.get("publication_info", {}).get("summary", "Unknown Source")
#         }
#         for resource in result.get("resources", []):
#             link = resource.get("link", "")
#             if resource.get("file_format") == "PDF" and link.lower().endswith(".pdf"):
#                 links_with_metadata.append({
#                     "link": link,
#                     "metadata": metadata
#                 })
#     return links_with_metadata

# async def download_google_scholar_pdf(pdf_url, search_term, metadata, search_source="Google Scholar"):
#     safe_search_term = sanitize_filename(search_term).replace(".pdf", "")
#     output_dir = Path(f"download/Both/Scholar/{safe_search_term}") if search_source == "BOTH" else Path(f"download/Scholar/{safe_search_term}")
#     output_dir.mkdir(parents=True, exist_ok=True)

#     existing_pdfs = sorted(output_dir.glob("*.pdf"), key=os.path.getctime)
#     next_index = len(existing_pdfs) + 1

#     pdf_path = output_dir / f"{next_index}.pdf"
#     metadata_path = output_dir / f"{next_index}.txt"

#     if pdf_path.exists() and pdf_path.stat().st_size > 1000:
#         return str(pdf_path), str(metadata_path)

#     for attempt in range(RETRIES):
#         try:
#             headers = {'User-Agent': USER_AGENT, 'Accept': 'application/pdf'}
#             async with aiohttp.ClientSession() as session:
#                 async with session.get(pdf_url, headers=headers, timeout=15) as response:
#                     response.raise_for_status()
#                     if "pdf" not in response.headers.get("Content-Type", "").lower():
#                         return None, None
#                     content = await response.read()

#             with open(pdf_path, 'wb') as f:
#                 f.write(content)

#             if pdf_path.stat().st_size < 1000:
#                 pdf_path.unlink()
#                 return None, None

#             with open(metadata_path, 'w', encoding='utf-8') as meta_file:
#                 meta_file.write(f"Title: {metadata.get('title', 'N/A')}\n")
#                 meta_file.write(f"Authors: {metadata.get('authors', 'N/A')}\n")
#                 meta_file.write(f"Year: {metadata.get('year', 'N/A')}\n")
#                 meta_file.write(f"Source: {metadata.get('source', 'N/A')}\n")
#                 meta_file.write(f"URL: {pdf_url}\n")

#             return str(pdf_path), str(metadata_path)

#         except Exception as e:
#             if attempt < RETRIES - 1:
#                 await asyncio.sleep(BACKOFF_FACTOR * (2 ** attempt))
#             else:
#                 return None, None

#testing
import os
import requests
import logging
import asyncio
import aiohttp
from pathlib import Path
from dotenv import load_dotenv
from utils.file_operations import sanitize_filename

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

OUTPUT_DIR = Path("download/Scholar")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
CHUNK_SIZE = 16384  # Increased further for faster downloads
RETRIES = 2
BACKOFF_FACTOR = 0.05  # Reduced for faster retries

async def search_google_scholar(keyword, start=0):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_scholar",
        "q": keyword,
        "api_key": os.getenv("SERP_API_KEY"),
        "start": start
    }
    print(f"Requesting search from SerpAPI for keyword '{keyword}', start: {start}")
    try:
        response = await asyncio.to_thread(requests.get, url, params=params)
        response.raise_for_status()
        print(f"Received search results for '{keyword}'")
        return response.json()
    except Exception as e:
        logging.error(f"Error in search_google_scholar: {e}")
        print(f"Search failed for '{keyword}': {e}")
        return None

def extract_pdf_links(data):
    links_with_metadata = []
    if not data or "organic_results" not in data:
        print("No organic results found in search data")
        return links_with_metadata

    for result in data.get("organic_results", []):
        metadata = {
            "title": result.get("title", "Unknown Title"),
            "authors": result.get("publication_info", {}).get("authors", "Unknown Authors"),
            "year": result.get("publication_info", {}).get("year", "Unknown Year"),
            "source": result.get("publication_info", {}).get("summary", "Unknown Source")
        }
        for resource in result.get("resources", []):
            link = resource.get("link", "")
            if resource.get("file_format") == "PDF" and link.lower().endswith(".pdf"):
                links_with_metadata.append({
                    "link": link,
                    "metadata": metadata
                })
    print(f"Extracted {len(links_with_metadata)} valid PDF links from search results")
    return links_with_metadata

async def download_google_scholar_pdf(pdf_url, search_term, metadata, search_source="Google Scholar"):
    safe_search_term = sanitize_filename(search_term).replace(".pdf", "")
    output_dir = Path(f"download/Both/Scholar/{safe_search_term}") if search_source == "BOTH" else Path(f"download/Scholar/{safe_search_term}")
    output_dir.mkdir(parents=True, exist_ok=True)

    existing_pdfs = sorted(output_dir.glob("*.pdf"), key=os.path.getctime)
    next_index = len(existing_pdfs) + 1

    pdf_path = output_dir / f"{next_index}.pdf"
    metadata_path = output_dir / f"{next_index}.txt"

    if pdf_path.exists() and pdf_path.stat().st_size > 1000:
        print(f"PDF already exists at {pdf_path}")
        return str(pdf_path), str(metadata_path)

    print(f"Starting download of PDF from {pdf_url}")
    for attempt in range(RETRIES):
        try:
            headers = {'User-Agent': USER_AGENT, 'Accept': 'application/pdf'}
            async with aiohttp.ClientSession() as session:
                async with session.get(pdf_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    if "pdf" not in response.headers.get("Content-Type", "").lower():
                        print(f"Skipping non-PDF content from {pdf_url}")
                        return None, None
                    content = await response.read()
                    print(f"Downloaded {len(content)} bytes from {pdf_url}")

            with open(pdf_path, 'wb') as f:
                f.write(content)

            if pdf_path.stat().st_size < 1000:
                pdf_path.unlink()
                print(f"Downloaded file too small at {pdf_path}, removing")
                return None, None

            with open(metadata_path, 'w', encoding='utf-8') as meta_file:
                meta_file.write(f"Title: {metadata.get('title', 'N/A')}\n")
                meta_file.write(f"Authors: {metadata.get('authors', 'N/A')}\n")
                meta_file.write(f"Year: {metadata.get('year', 'N/A')}\n")
                meta_file.write(f"Source: {metadata.get('source', 'N/A')}\n")
                meta_file.write(f"URL: {pdf_url}\n")
            print(f"Successfully saved PDF to {pdf_path} and metadata to {metadata_path}")

            return str(pdf_path), str(metadata_path)

        except Exception as e:
            print(f"Download attempt {attempt + 1} failed for {pdf_url}: {e}")
            if attempt < RETRIES - 1:
                await asyncio.sleep(BACKOFF_FACTOR * (2 ** attempt))
            else:
                print(f"All retries exhausted for {pdf_url}")
                return None, None