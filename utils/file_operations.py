import ast
import logging
import os
from pathlib import Path
import re
from typing import List

from fastapi import HTTPException
import fitz

from settings import BASE_DIR


#pdf filter
def list_all_directories(base_path: str):
    """ Recursively lists all directories and subdirectories. """
    path = Path(base_path)
    all_dirs = []

    for folder in path.rglob("*"):
        if folder.is_dir():
            all_dirs.append(str(folder))  # Convert Path to string

    return all_dirs


def extract_text_from_pdf(pdf_file: Path) -> str:
    """Extracts text from a PDF file."""
    text = ""
    with fitz.open(str(pdf_file)) as doc:
        for page in doc:
            text += page.get_text()
    return text.lower()


def search_terms_in_text(text: str, include_terms: List[str], exclude_terms: List[str], any_terms: List[str]) -> bool:
    """Checks if a text satisfies AND, NOT, and OR conditions."""
    include_pass = all(term.lower() in text for term in include_terms)
    exclude_pass = not any(term.lower() in text for term in exclude_terms)
    or_pass = any(term.lower() in text for term in any_terms) if any_terms else True
    return include_pass and exclude_pass and or_pass


# common worda analysis
# 3️⃣ Convert OpenAI output to a Python list
def string_to_python_list(string: str):
    cleaned_string = re.sub(r'```(?:python)?|```', '', string).strip()
    list_match = re.search(r'\[.*\]', cleaned_string, re.DOTALL)
    return ast.literal_eval(list_match.group()) if list_match else []


# 4️⃣ Truncate text to fit OpenAI's token limit
def truncate_text_to_fit_token_limit(text: str, max_tokens: int = 15000) -> str:
    from tiktoken import encoding_for_model
    
    enc = encoding_for_model("gpt-3.5-turbo")
    tokens = enc.encode(text)

    if len(tokens) > max_tokens:
        truncated_text = enc.decode(tokens[:max_tokens])
        logging.info(f"Truncated token count: {len(tokens[:max_tokens])}")
        return truncated_text
    
    return text

# Function to extract text from PDF in chunks
def extract_text_in_chunks(pdf_path: Path, chunk_size: int = 14999) -> List[str]:
    text = ""
    chunks = []
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + " "
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading PDF {pdf_path.name}: {str(e)}")
    return chunks

def get_categories(source: str):
    source_path = BASE_DIR / source
    return {d.name: d.name for d in source_path.iterdir() if d.is_dir()} if source_path.exists() else {}


def sanitize_filename(filename):
    """Sanitizes filenames by removing invalid characters and ensuring a valid length."""
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename).strip()
    max_length = 200

    if not filename:
        return "default"  

    name, ext = os.path.splitext(filename)

    if len(name) > max_length - len(ext):
        name = name[:max_length - len(ext)]

    return f"{name}{ext}" if ext else f"{name}"

def rename_downloaded_files(search_term, search_source):
    """
    Rename downloaded PDFs and corresponding TXT metadata files based on the search query.
    Returns a list of renamed file paths.
    """
    safe_search_term = sanitize_filename(search_term)
    renamed_files = []

    if search_source == "Google Scholar":
        output_dir = Path(f"download/Scholar/{safe_search_term}")
        renamed_files.extend(rename_files_in_folder(output_dir, safe_search_term))
    elif search_source == "PubMed":
        output_dir = Path(f"download/PubMed/{safe_search_term}")
        renamed_files.extend(rename_files_in_folder(output_dir, safe_search_term))
    elif search_source == "BOTH":
        output_dir_pubmed = Path(f"download/Both/PubMed/{safe_search_term}")
        output_dir_scholar = Path(f"download/Both/Scholar/{safe_search_term}")
        renamed_files.extend(rename_files_in_folder(output_dir_pubmed, safe_search_term))
        renamed_files.extend(rename_files_in_folder(output_dir_scholar, safe_search_term))
    else:
        logging.error(f"Invalid search source: {search_source}")
        return []

    return renamed_files  # Ensure function returns renamed files list

def rename_files_in_folder(folder_path, search_term):
    """
    Renames PDFs and corresponding TXT files sequentially in a folder.
    Ensures metadata TXT files are renamed alongside their corresponding PDFs.
    """
    if not folder_path.exists():
        logging.warning(f"Directory not found: {folder_path}")
        return []

    pdf_files = sorted(folder_path.glob("*.pdf"), key=os.path.getctime)
    renamed_files = []

    if not pdf_files:
        logging.warning(f"No PDFs found in {folder_path}")
        return []

    for index, pdf_file in enumerate(pdf_files, start=1):
        new_pdf_name = f"{search_term}{index}.pdf"
        new_pdf_path = folder_path / new_pdf_name

        # Check for corresponding TXT file before renaming the PDF
        original_txt_path = pdf_file.with_suffix('.txt')
        new_txt_name = f"{search_term}{index}.txt"
        new_txt_path = folder_path / new_txt_name

        # Rename TXT file first if it exists
        if original_txt_path.exists():
            try:
                original_txt_path.rename(new_txt_path)
                renamed_files.append(str(new_txt_path))
                logging.info(f"Renamed {original_txt_path.name} → {new_txt_name}")
            except Exception as e:
                logging.error(f"Error renaming {original_txt_path}: {e}")

        # Now rename the PDF
        try:
            pdf_file.rename(new_pdf_path)
            renamed_files.append(str(new_pdf_path))
            logging.info(f"Renamed {pdf_file.name} → {new_pdf_name}")
        except Exception as e:
            logging.error(f"Error renaming {pdf_file}: {e}")

    logging.info(f"Renaming process completed for {folder_path}")
    return renamed_files  # Return renamed file paths