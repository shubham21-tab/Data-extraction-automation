from pathlib import Path
from typing import List
from pypdf import PdfReader

def extract_text_with_page_markers(pdf_path: Path) -> str:
    """
    Extract text from a PDF file page by page and insert clear page markers.

    Parameters
    ----------
    pdf_path : Path
        Path to a single PDF file.

    Returns
    -------
    str
        Full extracted text with page separators.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    pages_text: List[str] = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        pages_text.append(f"\n\n--- PAGE {page_number} ---\n\n")
        pages_text.append(page_text)

    return "".join(pages_text)