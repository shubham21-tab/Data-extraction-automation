import json
from pathlib import Path
from datetime import datetime

from src.chunking.text_splitter import split_text_into_chunks


PROCESSED_TEXT_DIR = Path("data/processed_text")
CHUNKS_DIR = Path("data/chunks")


def main():
    # Ensure chunks directory exists
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    # Find extracted text file
    txt_files = list(PROCESSED_TEXT_DIR.glob("*.txt"))

    if not txt_files:
        raise FileNotFoundError("No .txt files found in data/processed_text")

    text_path = txt_files[0]

    print(f"\nChunking file: {text_path.name}\n")

    # Read full text
    full_text = text_path.read_text(encoding="utf-8")

    # Create chunks
    chunks = split_text_into_chunks(
        full_text,
        max_words=400,
        overlap_words=50
    )

    # Add extra metadata
    enriched_chunks = []

    for chunk in chunks:
        chunk_record = {
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "pages": chunk["pages"],
            "start_word": chunk["start_word"],
            "end_word": chunk["end_word"],
            "source_file": text_path.name,
            "created_at": datetime.utcnow().isoformat()
        }

        enriched_chunks.append(chunk_record)

    # Save to JSON
    output_file = CHUNKS_DIR / f"{text_path.stem}_chunks.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(enriched_chunks, f, indent=2, ensure_ascii=False)

    print(f"Total chunks created: {len(enriched_chunks)}")
    print(f"Chunks saved to: {output_file}\n")


if __name__ == "__main__":
    main()


