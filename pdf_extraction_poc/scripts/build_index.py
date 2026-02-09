from pathlib import Path

print(">>> build_index.py started")

from src.indexing.vector_index import VectorIndex


CHUNKS_DIR = Path("data/chunks")
VECTOR_STORE_DIR = Path("index/vector_store")


def main():

    print(">>> main() entered")

    chunk_files = list(CHUNKS_DIR.glob("*_chunks.json"))

    if not chunk_files:
        raise FileNotFoundError("No chunk files found")

    chunks_path = chunk_files[2]

    print(f"Using: {chunks_path.name}")

    index_path = VECTOR_STORE_DIR / "faiss.index"
    metadata_path = VECTOR_STORE_DIR / "metadata.json"

    vector_index = VectorIndex()

    chunks = vector_index.load_chunks(chunks_path)

    print(f"Loaded {len(chunks)} chunks")

    vector_index.build_index(chunks)

    vector_index.save(index_path, metadata_path)


if __name__ == "__main__":
    main()