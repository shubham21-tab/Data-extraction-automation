from pathlib import Path
from src.ingestion.pdf_reader import extract_text_with_page_markers


# Directories (relative to project root)
RAW_PDF_DIR = Path("data/raw_pdfs")
PROCESSED_TEXT_DIR = Path("data/processed_text")


def get_single_pdf(pdf_dir: Path) -> Path:
    """
    Return the first PDF found in the given directory.
    Raises an error if no PDF is found.
    """
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {pdf_dir}")
    return pdf_files[0]


def save_text(text: str, output_path: Path) -> None:
    """
    Save extracted text to a file.
    """
    output_path.write_text(text, encoding="utf-8")


def main():
    # Ensure output directory exists
    PROCESSED_TEXT_DIR.mkdir(parents=True, exist_ok=True)

    # Get one PDF (single-document POC)
    pdf_path = get_single_pdf(RAW_PDF_DIR)
    print(f"Processing PDF: {pdf_path.name}")

    # Extract text
    extracted_text = extract_text_with_page_markers(pdf_path)

    # Save output
    output_file = PROCESSED_TEXT_DIR / f"{pdf_path.stem}.txt"
    save_text(extracted_text, output_file)

    print(f"Text successfully saved to: {output_file}")


if __name__ == "__main__":
    main()
