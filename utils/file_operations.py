
import logging
import os
from pathlib import Path
import re
def sanitize_filename(filename):
    """Sanitizes filenames by removing invalid characters and ensuring a valid length."""
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename).strip()
    max_length=200
    if not filename:
        return "default"  # ✅ No .pdf for folder names

    name, ext = os.path.splitext(filename)

    if len(name) > max_length - len(ext):
        name = name[:max_length - len(ext)]

    return f"{name}{ext}" if ext else f"{name}"

def rename_downloaded_files(search_term, search_source):
    """
    Rename downloaded PDFs based on the search query with sequential numbering.
    Returns a list of renamed file paths.
    """

    safe_search_term = sanitize_filename(search_term)
    renamed_files = []

    if search_source == "Google Scholar":
        output_dir = Path(f"download/Scholar/{safe_search_term}")
        renamed_files.extend(rename_pdfs_in_folder(output_dir, safe_search_term))
    elif search_source == "PubMed":
        output_dir = Path(f"download/PubMed/{safe_search_term}")
        renamed_files.extend(rename_pdfs_in_folder(output_dir, safe_search_term))
    elif search_source == "BOTH":
        output_dir_pubmed = Path(f"download/Both/PubMed/{safe_search_term}")
        output_dir_scholar = Path(f"download/Both/Scholar/{safe_search_term}")
        renamed_files.extend(rename_pdfs_in_folder(output_dir_pubmed, safe_search_term))
        renamed_files.extend(rename_pdfs_in_folder(output_dir_scholar, safe_search_term))
    else:
        logging.error(f"Invalid search source: {search_source}")
        return []

    return renamed_files  # Ensure function returns renamed files list

def rename_pdfs_in_folder(folder_path, search_term):
    if not folder_path.exists():
        logging.warning(f"Directory not found: {folder_path}")
        return []

    pdf_files = sorted(folder_path.glob("*.pdf"), key=os.path.getctime)
    renamed_files = []

    if not pdf_files:
        logging.warning(f"No PDFs found in {folder_path}")
        return []

    for index, pdf_file in enumerate(pdf_files, start=1):
        new_filename = f"{search_term}{index}.pdf"
        new_path = folder_path / new_filename

        try:
            pdf_file.rename(new_path)
            renamed_files.append(str(new_path))  # Store renamed file paths
            logging.info(f"Renamed {pdf_file.name} → {new_filename}")
        except PermissionError:
            logging.error(f"Permission error renaming {pdf_file}. Check file permissions.")
        except FileExistsError:
            logging.error(f"File {new_path} already exists. Cannot rename.")
        except Exception as e:
            logging.error(f"Error renaming {pdf_file}: {e}")

    logging.info(f"Renaming process completed for {folder_path}")
    return renamed_files  # Return renamed file paths
