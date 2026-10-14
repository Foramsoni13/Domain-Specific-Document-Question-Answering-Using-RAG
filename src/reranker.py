"""
Reranking Module for Domain-Specific RAG.
Implements Cross-Encoder deep neural reranking (ms-marco-MiniLM-L-6-v2)
to calculate query-chunk joint attention and calibrated relevance scores.
"""

import numpy as np
from typing import List, Tuple, Optional
from src.chunker import TextChunk
from src.vector_store import SearchResult

class CrossEncoderReranker:
    """
    Cross-Encoder Reranker using cross-encoder/ms-marco-MiniLM-L-6-v2.
    Computes full cross-attention over (query, document) pairs to re-order candidate chunks.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        device: Optional[str] = None
    ):
        self.model_name = model_name
        self.device = device or self._detect_device()
        self.model = None
        self._load_model()

    def _detect_device(self) -> str:
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
        try:
            from sentence_transformers import CrossEncoder
            print(f"[CrossEncoderReranker] Loading '{self.model_name}' on '{self.device}'...")
            self.model = CrossEncoder(self.model_name, device=self.device)
            print("[CrossEncoderReranker] Loaded reranker model successfully.")
        except Exception as e:
            print(f"[CrossEncoderReranker] Failed to load CrossEncoder ({e}). Utilizing heuristic score fallback.")
            self.model = None

    @staticmethod
    def _sigmoid(x: np.ndarray) -> np.ndarray:
        """Converts raw cross-encoder logits into calibrated probabilities in [0, 1]."""
        return 1.0 / (1.0 + np.exp(-np.clip(x, -15.0, 15.0)))

    def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_n: int = 3
    ) -> List[SearchResult]:
        """
        Reranks a list of initial search results using the cross-encoder.
        Args:
            query: The user question.
            results: List of candidate SearchResults from dense/hybrid retrieval.
            top_n: Number of reranked results to return.
        Returns:
            List of SearchResult objects reordered by cross-encoder score.
        """
        if not results:
            return []

        top_n = min(top_n, len(results))

        pairs = [(query, r.chunk.content) for r in results]

        if self.model is not None:
            raw_scores = self.model.predict(pairs, convert_to_numpy=True)
            norm_scores = self._sigmoid(raw_scores)
        else:
            # Fallback heuristic: token overlap & length penalty
            q_words = set(query.lower().split())
            norm_scores = []
            for _, content in pairs:
                c_words = set(content.lower().split())
                overlap = len(q_words.intersection(c_words))
                score = overlap / max(1, len(q_words))
                norm_scores.append(score)
            norm_scores = np.array(norm_scores, dtype=np.float32)

        # Sort indices by reranker score descending
        sorted_indices = np.argsort(norm_scores)[::-1][:top_n]

        reranked_results: List[SearchResult] = []
        for rank, idx in enumerate(sorted_indices, start=1):
            original = results[idx]
            reranked_results.append(SearchResult(
                chunk=original.chunk,
                score=float(norm_scores[idx]),
                rank=rank,
                retrieval_type="cross_encoder_reranked"
            ))

        return reranked_results
