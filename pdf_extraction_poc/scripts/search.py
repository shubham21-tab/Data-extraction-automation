from pathlib import Path

from src.indexing.vector_index import VectorIndex


VECTOR_STORE_DIR = Path("index/vector_store")


def main():

    index_path = VECTOR_STORE_DIR / "faiss.index"
    metadata_path = VECTOR_STORE_DIR / "metadata.json"

    vector_index = VectorIndex()

    vector_index.load(index_path, metadata_path)

    print("\nVector index loaded.\n")

    while True:

        query = input("\nEnter your question (or 'exit'): ").strip()

        if query.lower() == "exit":
            break

        results = vector_index.search(query, top_k=5)

        print("\nTop Results:\n")

        for res in results:

            print(f"Rank: {res['rank']}")
            print(f"Cosine Similarity: {res['score']:.4f}")
            print(f"Pages: {res['pages']}")
            print("Text Preview:")
            print(res["text"])
            print("-" * 50)


if __name__ == "__main__":
    main()
