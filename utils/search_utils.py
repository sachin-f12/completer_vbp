import os
import requests
import logging
import time
from pathlib import Path
from dotenv import load_dotenv
from utils.file_operations import sanitize_filename

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

OUTPUT_DIR = Path("download/Scholar")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
CHUNK_SIZE = 1024
RETRIES = 3
BACKOFF_FACTOR = 0.3

def search_google_scholar(keyword, start=0):
    """Searches Google Scholar using SerpAPI."""
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_scholar",
        "q": keyword,
        "api_key": os.getenv("SERP_API_KEY"),
        "start": start
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error in search_google_scholar: {e}")
        return None

def extract_pdf_links(data):
    """Extracts PDF links and metadata from search results."""
    links_with_metadata = []
    if not data or "organic_results" not in data:
        logging.warning("No organic results found in data")
        return links_with_metadata
        
    for result in data.get("organic_results", []):
        metadata = {
            "title": result.get("title", "Unknown Title"),
            "authors": result.get("publication_info", {}).get("authors", "Unknown Authors"),
            "year": result.get("publication_info", {}).get("year", "Unknown Year"),
            "source": result.get("publication_info", {}).get("summary", "Unknown Source")
        }
        for resource in result.get("resources", []):
            if resource.get("file_format") == "PDF":
                links_with_metadata.append({
                    "link": resource["link"],
                    "metadata": metadata
                })
    
    logging.info(f"Extracted {len(links_with_metadata)} PDF links with metadata")
    return links_with_metadata

def download_google_scholar_pdf(pdf_url, search_term, metadata, search_source="Google Scholar"):
    """Downloads the PDF and saves metadata in a txt file with the same base name."""
    safe_search_term = sanitize_filename(search_term).replace(".pdf", "")

    if search_source.lower() == "both":
        output_dir = Path(f"download/Both/Scholar/{safe_search_term}")
    else:
        output_dir = Path(f"download/Scholar/{safe_search_term}")
    
    os.makedirs(output_dir, exist_ok=True)

    pdf_filename = sanitize_filename(pdf_url.split("/")[-1].split("?")[0])
    pdf_path = output_dir / pdf_filename
    metadata_path = pdf_path.with_suffix('.txt')  # Ensure .txt matches PDF base name exactly

    if pdf_path.exists() and pdf_path.stat().st_size > 1000:
        logging.info(f"PDF already exists: {pdf_path}")
        return str(pdf_path), str(metadata_path)

    for attempt in range(RETRIES):
        try:
            headers = {'User-Agent': USER_AGENT, 'Accept': 'application/pdf'}
            response = requests.get(pdf_url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()

            with open(pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)

            if pdf_path.stat().st_size < 1000:
                pdf_path.unlink()
                logging.error(f"Downloaded file too small: {pdf_url}")
                return None, None

            # Save metadata with matching name
            with open(metadata_path, 'w', encoding='utf-8') as meta_file:
                meta_file.write(f"Title: {metadata['title']}\n")
                meta_file.write(f"Authors: {metadata['authors']}\n")
                meta_file.write(f"Year: {metadata['year']}\n")
                meta_file.write(f"Source: {metadata['source']}\n")
                meta_file.write(f"URL: {pdf_url}\n")

            logging.info(f"Successfully downloaded PDF and metadata: {pdf_path}")
            return str(pdf_path), str(metadata_path)

        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed for {pdf_url}: {e}")
            if attempt < RETRIES - 1:
                time.sleep(BACKOFF_FACTOR * (2 ** attempt))
            else:
                return None, None