import fitz
import re
import io
def extract_metadata_from_pdf(file_path):
    """Extract actual metadata from a PDF file."""
    try:
        doc = fitz.open(file_path)
        metadata = doc.metadata
        doc.close()

        return {
            "Title": metadata.get("title", "Unknown"),
            "Authors": metadata.get("author", "Unknown"),
            "Publication Year": metadata.get("creationDate", "Unknown")[2:6],  # Extract Year
            "Journal Name": "Not Available",  # Journal info usually missing in metadata
            "DOI/Link": "Not Available"  # DOI usually not in metadata
        }
    except Exception as e:
        return {"Error": f"Failed to extract metadata: {str(e)}"}



def extract_text_from_pdf(pdf_path):
    # Extract text from PDF using PyMuPDF
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text


def remove_unwanted_sections(text, section_to_remove="References"):
    # Remove the specified section from the text
    pattern = re.compile(rf'{section_to_remove}.*', re.DOTALL | re.IGNORECASE)
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text
