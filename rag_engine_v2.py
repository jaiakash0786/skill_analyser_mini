import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class MetadataRAGEngine:
    def __init__(self, docs_path="rag/documents"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.text_chunks = []
        self.metadata = []
        self.index = None

        self._load_documents(docs_path)
        self._build_index()

    # -----------------------------------------

    def _load_documents(self, docs_path):
        for root, _, files in os.walk(docs_path):
            for file in files:
                if not file.endswith(".md"):
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, docs_path)
                parts = rel_path.split(os.sep)

                doc_type = parts[0]
                name = file.replace(".md", "")

                meta = {
                    "doc_type": doc_type,
                    "role": None,
                    "domain": None,
                    "skill": None
                }

                if doc_type == "roles":
                    meta["role"] = name
                elif doc_type == "domains":
                    meta["domain"] = name
                elif doc_type in ["skills", "learning"]:
                    meta["skill"] = name

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                self._chunk_and_store(content, meta)

    # -----------------------------------------

    def _chunk_and_store(self, text, meta, chunk_size=300):
        words = text.split()
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            self.text_chunks.append(chunk)
            self.metadata.append(meta.copy())

    # -----------------------------------------

    def _build_index(self):
        embeddings = self.model.encode(self.text_chunks)
        embeddings = np.array(embeddings).astype("float32")

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

    # -----------------------------------------

    def retrieve(
        self,
        query,
        top_k=10,
        role=None,
        domain=None,
        doc_types=None
    ):
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype("float32")

        distances, indices = self.index.search(query_embedding, top_k * 2)

        results = []
        for idx in indices[0]:
            meta = self.metadata[idx]

            if role and meta["role"] and meta["role"] != role:
                continue

            if domain and meta["domain"] and meta["domain"] != domain:
                continue

            if doc_types and meta["doc_type"] not in doc_types:
                continue

            results.append(self.text_chunks[idx])

            if len(results) >= top_k:
                break

        return results
