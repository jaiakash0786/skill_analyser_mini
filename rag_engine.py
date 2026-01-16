import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from hashlib import md5

MODEL_NAME = "all-MiniLM-L6-v2"


class RAGEngine:
    def __init__(self, docs_path="rag/documents"):
        self.model = SentenceTransformer(MODEL_NAME)
        self.text_chunks = []
        self.chunk_hashes = set()  # Track unique chunks
        self.index = None
        self._load_documents(docs_path)
        self._build_index()

    def _load_documents(self, docs_path):
        for root, _, files in os.walk(docs_path):
            for file in files:
                if file.endswith(".md"):
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        content = f.read()
                        self._chunk_text(content)

    def _chunk_text(self, text, chunk_size=300):
        words = text.split()
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunk_hash = md5(chunk.encode()).hexdigest()
            
            # Only add unique chunks
            if chunk_hash not in self.chunk_hashes:
                self.chunk_hashes.add(chunk_hash)
                self.text_chunks.append(chunk)

    def _build_index(self):
        if not self.text_chunks:
            print("Warning: No documents loaded!")
            return
            
        embeddings = self.model.encode(self.text_chunks)
        embeddings = np.array(embeddings).astype("float32")

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        print(f"Index built with {len(self.text_chunks)} unique chunks")

    def retrieve(self, query, top_k=5):
        if self.index is None or len(self.text_chunks) == 0:
            print("Error: Index not built or no documents available")
            return []
            
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype("float32")

        # Get more results than needed for deduplication
        distances, indices = self.index.search(query_embedding, min(top_k * 2, len(self.text_chunks)))
        
        # Deduplicate results by content similarity
        unique_results = []
        seen_content = set()
        
        for i in indices[0]:
            if i < len(self.text_chunks):  # Safety check
                chunk = self.text_chunks[i]
                # Simple deduplication: check for very similar content
                if len(unique_results) >= top_k:
                    break
                    
                # Check if this chunk is too similar to already selected chunks
                is_similar = False
                for existing in unique_results:
                    # If chunks are very similar (e.g., 80% overlap), skip
                    if self._similarity_score(chunk, existing) > 0.8:
                        is_similar = True
                        break
                
                if not is_similar:
                    unique_results.append(chunk)
        
        return unique_results
    
    def _similarity_score(self, text1, text2):
        """Calculate simple similarity between two texts"""
        # You can replace this with a more sophisticated method
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        if not set1 or not set2:
            return 0
        return len(set1.intersection(set2)) / len(set1.union(set2))

    def print_statistics(self):
        """Print statistics about the loaded documents"""
        print(f"Total unique chunks: {len(self.text_chunks)}")
        print(f"Index built: {self.index is not None}")
        if self.text_chunks:
            avg_len = sum(len(chunk) for chunk in self.text_chunks) / len(self.text_chunks)
            print(f"Average chunk length: {avg_len:.0f} characters")