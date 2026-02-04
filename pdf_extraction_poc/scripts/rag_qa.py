import os
from pathlib import Path

from google import genai

from src.indexing.vector_index import VectorIndex
print(">>> rag_qa.py started")



VECTOR_STORE_DIR = Path("index/vector_store")


SYSTEM_PROMPT = """
You are a medical research assistant.

Answer the question using ONLY the provided context.

If the answer is not in the context, say:
"I could not find this information in the document."

Always mention page numbers in your answer.
"""


def build_context(chunks, max_chars=4000):
    """
    Combine chunks into a single context string.
    """

    context_parts = []
    total_chars = 0

    for ch in chunks:

        part = f"[Pages {ch['pages']}]\n{ch['text']}\n\n"

        if total_chars + len(part) > max_chars:
            break

        context_parts.append(part)
        total_chars += len(part)

    return "".join(context_parts)


def main():
    print(">>> main() entered")
     
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")

    client = genai.Client(api_key=api_key)

    # Load vector index
    vector_index = VectorIndex()

    index_path = VECTOR_STORE_DIR / "faiss.index"
    metadata_path = VECTOR_STORE_DIR / "metadata.json"

    vector_index.load(index_path, metadata_path)

    print("\nRAG system ready.\n")

    while True:

        question = input("\nAsk a question (or 'exit'): ").strip()

        if question.lower() == "exit":
            break

        # Retrieve top chunks
        results = vector_index.search(question, top_k=5)

        if not results:
            print("\nNo relevant context found.\n")
            continue

        # Build context
        context = build_context(results)

        prompt = f"""
{SYSTEM_PROMPT}

Context:
{context}

Question:
{question}

Answer:
"""

        print("\nGenerating answer...\n")

        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )

        print("\nAnswer:\n")
        print(response.text)


if __name__ == "__main__":
    main()
