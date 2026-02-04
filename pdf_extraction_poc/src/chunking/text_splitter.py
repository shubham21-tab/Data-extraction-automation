import re
from typing import List, Dict, Tuple


PAGE_PATTERN = re.compile(r"--- PAGE (\d+) ---")


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text before chunking.
    """

    # Remove references section (case-insensitive)
    text = re.split(r"\nreferences\n", text, flags=re.I)[0]

    # Remove common journal header/footer patterns (customize if needed)
    text = re.sub(r"IJID.*?\n", "", text, flags=re.I)

    # Remove multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove excessive spaces
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


def _split_by_pages(text: str) -> List[Tuple[int, str]]:
    """
    Split full text into (page_number, page_text).
    """

    parts = PAGE_PATTERN.split(text)

    pages = []

    # parts = ["", "1", "text...", "2", "text...", ...]
    for i in range(1, len(parts), 2):
        page_num = int(parts[i])
        page_text = parts[i + 1].strip()
        pages.append((page_num, page_text))

    return pages


def split_text_into_chunks(
    full_text: str,
    max_words: int = 600,
    overlap_words: int = 120
) -> List[Dict]:
    """
    Split text into overlapping, semantically coherent chunks.
    """

    # Clean first
    full_text = clean_text(full_text)

    # Split by pages
    pages = _split_by_pages(full_text)

    if not pages:
        raise ValueError("No page markers found in text")

    # Build word stream with page tracking
    word_stream = []

    for page_num, page_text in pages:

        # Try to preserve sentence structure
        sentences = re.split(r"(?<=[.!?])\s+", page_text)

        for sent in sentences:
            words = sent.split()

            for w in words:
                word_stream.append((w, page_num))

    # Sliding window
    chunks = []
    chunk_id = 1

    step = max_words - overlap_words

    for start in range(0, len(word_stream), step):

        end = start + max_words

        window = word_stream[start:end]

        if not window:
            continue

        words = [w for w, _ in window]
        pages_used = sorted(set(p for _, p in window))

        chunk_text = " ".join(words)

        # Skip very small chunks
        if len(words) < 100:
            continue

        chunks.append({
            "chunk_id": chunk_id,
            "text": chunk_text,
            "pages": pages_used,
            "start_word": start,
            "end_word": end
        })

        chunk_id += 1

    return chunks



