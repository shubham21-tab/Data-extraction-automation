import json
import os
from pathlib import Path
from typing import List, Dict

import faiss
import numpy as np
from google import genai


class VectorIndex:
    """
    Vector index using Gemini embeddings (text-embedding-004).
    """

    def __init__(self, model_name: str = "models/text-embedding-004"):

        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set")

        self.client = genai.Client(api_key=api_key)

        self.model = model_name
        self.index = None
        self.metadata: List[Dict] = []

    def load_chunks(self, chunks_path: Path) -> List[Dict]:
        """
        Load chunk JSON file.
        """

        if not chunks_path.exists():
            raise FileNotFoundError(chunks_path)

        with open(chunks_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings using Gemini API.
        """

        print("Generating embeddings (Gemini API)...")

        vectors = []

        for i, text in enumerate(texts, start=1):

            print(f"Embedding chunk {i}/{len(texts)}")

            response = self.client.models.embed_content(model=self.model,
    contents=text,
    )
    


            # New SDK format: list of embeddings
            vectors.append(response.embeddings[0].values)

        return np.array(vectors).astype("float32")

    def build_index(self, chunks: List[Dict]) -> None:
        """
        Build FAISS index.
        """

        texts = [c["text"] for c in chunks]

        embeddings = self._embed_texts(texts)
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]

        print(f"Embedding dimension: {dimension}")

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        self.metadata = chunks

        print(f"Index built with {self.index.ntotal} vectors")

    def save(self, index_path: Path, metadata_path: Path) -> None:
        """
        Save index and metadata.
        """

        if self.index is None:
            raise ValueError("Index not built")

        index_path.parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(index_path))

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2)

        print("Index and metadata saved")

    def load(self, index_path: Path, metadata_path: Path) -> None:
        """
        Load index and metadata.
        """

        if not index_path.exists():
            raise FileNotFoundError(index_path)

        if not metadata_path.exists():
            raise FileNotFoundError(metadata_path)

        self.index = faiss.read_index(str(index_path))

        with open(metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        print("Index loaded")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search similar chunks.
        """

        if self.index is None:
            raise ValueError("Index not loaded")

        print("Embedding query...")

        response = self.client.models.embed_content(
            model=self.model,
            contents=query
        )

        query_vec = np.array(
            [response.embeddings[0].values]
        ).astype("float32")

        faiss.normalize_L2(query_vec)

        distances, indices = self.index.search(query_vec, top_k)

        results = []

        for rank, idx in enumerate(indices[0]):

            if idx < 0:
                continue

            chunk = self.metadata[idx]

            results.append({
                "rank": rank + 1,
                "score": float(distances[0][rank]),
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "pages": chunk["pages"],
                "source_file": chunk["source_file"]
            })

        return results




