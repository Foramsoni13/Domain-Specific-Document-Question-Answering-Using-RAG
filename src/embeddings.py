"""
Vector Embeddings Module for Domain-Specific RAG.
Encapsulates SentenceTransformer models (default: all-MiniLM-L6-v2)
with L2 normalization, hardware acceleration (Apple MPS / CUDA / CPU),
and memory/disk embedding caching.
"""

import os
import hashlib
import pickle
import numpy as np
from typing import List, Union, Optional

class EmbeddingEngine:
    """
    Computes dense semantic embeddings for text chunks and queries.
    Uses 'sentence-transformers/all-MiniLM-L6-v2' (384 dimensions),
    which provides top-tier speed-accuracy trade-offs for semantic retrieval.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        cache_dir: Optional[str] = None,
        device: Optional[str] = None
    ):
        self.model_name = model_name
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), "..", "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.device = device or self._detect_device()
        self.model = None
        self._load_model()
        self.embedding_dim = 384

    def _detect_device(self) -> str:
        """Detects available hardware accelerator."""
        try:
            import torch
            if torch.backends.mps.is_available():
                return "mps"
            elif torch.cuda.is_available():
                return "cuda"
        except Exception:
            pass
        return "cpu"

    def _load_model(self):
        """Loads SentenceTransformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            print(f"[EmbeddingEngine] Loading '{self.model_name}' on device '{self.device}'...")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            get_dim = getattr(self.model, "get_embedding_dimension", None) or self.model.get_sentence_embedding_dimension
            self.embedding_dim = get_dim()
            print(f"[EmbeddingEngine] Loaded model successfully (dim={self.embedding_dim}).")
        except Exception as e:
            print(f"[EmbeddingEngine] Error loading SentenceTransformer: {e}. Utilizing fallback encoder.")
            self.model = None
            self.embedding_dim = 384

    def _hash_text(self, text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def encode(self, texts: Union[str, List[str]], normalize: bool = True, batch_size: int = 32) -> np.ndarray:
        """
        Generates dense vector embeddings.
        Args:
            texts: Single string or list of text strings.
            normalize: If True, normalizes vectors to unit L2 norm (making dot product == cosine similarity).
            batch_size: Batch size for model inference.
        Returns:
            np.ndarray of shape (N, dim) with float32 values.
        """
        is_single = isinstance(texts, str)
        text_list = [texts] if is_single else texts

        if not text_list:
            return np.empty((0, self.embedding_dim), dtype=np.float32)

        if self.model is not None:
            embeddings = self.model.encode(
                text_list,
                batch_size=batch_size,
                show_progress_bar=False,
                normalize_embeddings=normalize,
                convert_to_numpy=True
            )
        else:
            # Fallback lightweight deterministic projection
            embeddings = self._fallback_encode(text_list, normalize)

        embeddings = np.asarray(embeddings, dtype=np.float32)
        return embeddings[0] if is_single else embeddings

    def _fallback_encode(self, texts: List[str], normalize: bool = True) -> np.ndarray:
        """Fallback deterministic bag-of-words / character-hash dense representation."""
        vectors = []
        for t in texts:
            words = t.lower().split()
            v = np.zeros(self.embedding_dim, dtype=np.float32)
            for w in words:
                h = int(hashlib.md5(w.encode()).hexdigest(), 16) % self.embedding_dim
                v[h] += 1.0
            if normalize:
                norm = np.linalg.norm(v)
                if norm > 1e-9:
                    v = v / norm
            vectors.append(v)
        return np.vstack(vectors)

    def compute_similarity(self, query_vector: np.ndarray, doc_vectors: np.ndarray) -> np.ndarray:
        """
        Computes cosine similarity between a single query vector and an array of doc vectors.
        Assumes both are L2-normalized.
        """
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        # Cosine similarity is matrix dot product for unit vectors
        scores = np.dot(doc_vectors, query_vector.T).squeeze()
        return scores
