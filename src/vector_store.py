"""
Vector Store Module for Domain-Specific RAG.
Implements FAISS IndexFlatIP (Inner Product / Cosine Similarity)
with metadata tracking, persistence, and NumPy fallback.
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from src.chunker import TextChunk

class SearchResult:
    """Represents a single retrieval match."""
    def __init__(self, chunk: TextChunk, score: float, rank: int, retrieval_type: str = "dense"):
        self.chunk = chunk
        self.score = float(score)
        self.rank = int(rank)
        self.retrieval_type = retrieval_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk.chunk_id,
            "doc_name": self.chunk.doc_name,
            "page_number": self.chunk.page_number,
            "content": self.chunk.content,
            "score": round(self.score, 4),
            "rank": self.rank,
            "retrieval_type": self.retrieval_type,
            "metadata": self.chunk.metadata
        }

    def __repr__(self) -> str:
        return f"<SearchResult rank={self.rank} score={self.score:.4f} doc='{self.chunk.doc_name}' page={self.chunk.page_number}>"


class FAISSVectorStore:
    """
    FAISS-based vector index supporting fast exact or approximate nearest neighbor search.
    Defaults to IndexFlatIP (Inner Product) on L2-normalized vectors.
    """

    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.chunks: List[TextChunk] = []
        self.embeddings: Optional[np.ndarray] = None
        self.index = None
        self._init_index()

    def _init_index(self):
        """Initializes FAISS IndexFlatIP or prepares fallback."""
        try:
            import faiss
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self._use_faiss = True
        except ImportError:
            self._use_faiss = False
            self.index = None

    def add_documents(self, chunks: List[TextChunk], embeddings: np.ndarray):
        """
        Adds text chunks and their corresponding embeddings to the vector store.
        Args:
            chunks: List of TextChunk objects.
            embeddings: Numpy array of shape (N, dim), L2 normalized.
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Number of chunks ({len(chunks)}) does not match embeddings ({len(embeddings)})")

        if len(chunks) == 0:
            return

        embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)

        if self._use_faiss and self.index is not None:
            self.index.add(embeddings)
        
        # Keep tracked in memory
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])

        self.chunks.extend(chunks)

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[SearchResult]:
        """
        Performs cosine similarity search against stored vectors.
        Args:
            query_vector: 1D array of shape (dim,) or 2D of shape (1, dim), L2-normalized.
            top_k: Number of nearest neighbors to retrieve.
        Returns:
            List of SearchResult objects sorted in descending order of similarity.
        """
        if len(self.chunks) == 0:
            return []

        query_vector = np.ascontiguousarray(query_vector.reshape(1, -1), dtype=np.float32)
        top_k = min(top_k, len(self.chunks))

        if self._use_faiss and self.index is not None and self.index.ntotal > 0:
            scores, indices = self.index.search(query_vector, top_k)
            scores = scores[0]
            indices = indices[0]
        else:
            # Fallback pure NumPy dot product
            scores_all = np.dot(self.embeddings, query_vector.T).squeeze()
            if scores_all.ndim == 0:
                scores_all = np.array([scores_all])
            top_indices = np.argsort(scores_all)[::-1][:top_k]
            indices = top_indices
            scores = scores_all[top_indices]

        results: List[SearchResult] = []
        for rank, (idx, score) in enumerate(zip(indices, scores), start=1):
            if idx < 0 or idx >= len(self.chunks):
                continue
            chunk = self.chunks[idx]
            results.append(SearchResult(
                chunk=chunk,
                score=float(score),
                rank=rank,
                retrieval_type="dense_faiss"
            ))

        return results

    def save(self, directory: str, index_name: str = "faiss_index"):
        """Persists the FAISS index and chunk metadata to disk."""
        os.makedirs(directory, exist_ok=True)
        meta_path = os.path.join(directory, f"{index_name}_meta.pkl")
        with open(meta_path, "wb") as f:
            pickle.dump({
                "chunks": self.chunks,
                "embeddings": self.embeddings,
                "dim": self.embedding_dim
            }, f)

        if self._use_faiss and self.index is not None:
            import faiss
            index_path = os.path.join(directory, f"{index_name}.faiss")
            faiss.write_index(self.index, index_path)

    @classmethod
    def load(cls, directory: str, index_name: str = "faiss_index") -> "FAISSVectorStore":
        """Loads a persisted FAISS index and chunk metadata from disk."""
        meta_path = os.path.join(directory, f"{index_name}_meta.pkl")
        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"Metadata file not found: {meta_path}")

        with open(meta_path, "rb") as f:
            data = pickle.load(f)

        store = cls(embedding_dim=data.get("dim", 384))
        store.chunks = data.get("chunks", [])
        store.embeddings = data.get("embeddings", None)

        index_path = os.path.join(directory, f"{index_name}.faiss")
        if os.path.exists(index_path):
            try:
                import faiss
                store.index = faiss.read_index(index_path)
                store._use_faiss = True
            except Exception:
                store._use_faiss = False
        else:
            store._use_faiss = False

        return store

    def clear(self):
        """Resets the vector store."""
        self.chunks.clear()
        self.embeddings = None
        self._init_index()
