"""
Retrieval Module for Domain-Specific RAG.
Implements:
1. Dense Semantic Retriever (FAISS / Cosine Similarity)
2. Sparse Lexical Retriever (BM25Okapi with domain tokenization)
3. Hybrid Retriever with Reciprocal Rank Fusion (RRF) and Convex Score Combination
"""

import re
import numpy as np
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi

from src.chunker import TextChunk
from src.embeddings import EmbeddingEngine
from src.vector_store import FAISSVectorStore, SearchResult

class DomainTokenizer:
    """Tokenizes text while preserving domain-critical alphanumeric entities, numbers, and symbols."""
    @staticmethod
    def tokenize(text: str) -> List[str]:
        # Keep alphanumeric, percentages, currency, hyphens, and dots in numbers
        tokens = re.findall(r"\b[a-zA-Z0-9_\$%\.-]+\b", text.lower())
        return tokens


class SparseRetriever:
    """BM25Okapi keyword retriever for precise lexical and code matching."""
    def __init__(self, chunks: List[TextChunk]):
        self.chunks = chunks
        self.tokenizer = DomainTokenizer()
        self.corpus_tokens = [self.tokenizer.tokenize(chunk.content) for chunk in chunks]
        self.bm25 = BM25Okapi(self.corpus_tokens) if self.corpus_tokens else None

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        if not self.bm25 or len(self.chunks) == 0:
            return []

        query_tokens = self.tokenizer.tokenize(query)
        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)
        top_k = min(top_k, len(self.chunks))
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for rank, idx in enumerate(top_indices, start=1):
            results.append(SearchResult(
                chunk=self.chunks[idx],
                score=float(scores[idx]),
                rank=rank,
                retrieval_type="sparse_bm25"
            ))
        return results


class DenseRetriever:
    """Dense vector retriever using embedding engine and vector store."""
    def __init__(self, vector_store: FAISSVectorStore, embedding_engine: EmbeddingEngine):
        self.vector_store = vector_store
        self.embedding_engine = embedding_engine

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        query_vec = self.embedding_engine.encode(query, normalize=True)
        return self.vector_store.search(query_vec, top_k=top_k)


class HybridRetriever:
    """
    Fuses dense semantic retrieval with sparse lexical BM25 retrieval.
    Offers both Reciprocal Rank Fusion (RRF) and Convex Score Fusion.
    """

    def __init__(
        self,
        dense_retriever: DenseRetriever,
        sparse_retriever: SparseRetriever,
        rrf_k: int = 60,
        alpha: float = 0.55  # Weight given to dense semantic retrieval
    ):
        self.dense_retriever = dense_retriever
        self.sparse_retriever = sparse_retriever
        self.rrf_k = rrf_k
        self.alpha = alpha

    def search(
        self,
        query: str,
        top_k: int = 5,
        fusion_method: str = "rrf"  # "rrf" or "convex"
    ) -> List[SearchResult]:
        """
        Retrieves top_k documents by fusing dense and sparse search.
        Args:
            query: User query string.
            top_k: Number of final results to return.
            fusion_method: 'rrf' (Reciprocal Rank Fusion) or 'convex' (Weighted linear combination).
        """
        candidate_k = max(top_k * 3, 15)
        dense_results = self.dense_retriever.search(query, top_k=candidate_k)
        sparse_results = self.sparse_retriever.search(query, top_k=candidate_k)

        if fusion_method == "rrf":
            return self._reciprocal_rank_fusion(dense_results, sparse_results, top_k)
        else:
            return self._convex_score_fusion(dense_results, sparse_results, top_k)

    def _reciprocal_rank_fusion(
        self,
        dense_results: List[SearchResult],
        sparse_results: List[SearchResult],
        top_k: int
    ) -> List[SearchResult]:
        """Calculates RRF score: score(d) = sum(1 / (k + rank_i))."""
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, TextChunk] = {}

        for rank, res in enumerate(dense_results, start=1):
            cid = res.chunk.chunk_id
            chunk_map[cid] = res.chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))

        for rank, res in enumerate(sparse_results, start=1):
            cid = res.chunk.chunk_id
            chunk_map[cid] = res.chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))

        # Sort by RRF score descending
        sorted_cids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)[:top_k]

        # Normalize RRF scores against theoretical maximum for 2 rank-1 lists: 2 / (k + 1)
        max_possible_rrf = 2.0 / (self.rrf_k + 1.0)
        fused_results: List[SearchResult] = []
        for rank, cid in enumerate(sorted_cids, start=1):
            normalized_score = min(1.0, rrf_scores[cid] / max_possible_rrf)
            fused_results.append(SearchResult(
                chunk=chunk_map[cid],
                score=normalized_score,
                rank=rank,
                retrieval_type="hybrid_rrf"
            ))

        return fused_results

    def _convex_score_fusion(
        self,
        dense_results: List[SearchResult],
        sparse_results: List[SearchResult],
        top_k: int
    ) -> List[SearchResult]:
        """Min-Max normalizes dense and BM25 scores and combines linearly."""
        chunk_map: Dict[str, TextChunk] = {}
        dense_norm: Dict[str, float] = {}
        sparse_norm: Dict[str, float] = {}

        if dense_results:
            d_scores = [r.score for r in dense_results]
            d_min, d_max = min(d_scores), max(d_scores)
            d_range = (d_max - d_min) if (d_max - d_min) > 1e-6 else 1.0
            for r in dense_results:
                cid = r.chunk.chunk_id
                chunk_map[cid] = r.chunk
                dense_norm[cid] = (r.score - d_min) / d_range

        if sparse_results:
            s_scores = [r.score for r in sparse_results]
            s_min, s_max = min(s_scores), max(s_scores)
            s_range = (s_max - s_min) if (s_max - s_min) > 1e-6 else 1.0
            for r in sparse_results:
                cid = r.chunk.chunk_id
                chunk_map[cid] = r.chunk
                sparse_norm[cid] = (r.score - s_min) / s_range

        all_cids = set(dense_norm.keys()).union(set(sparse_norm.keys()))
        combined_scores: Dict[str, float] = {}

        for cid in all_cids:
            s_dense = dense_norm.get(cid, 0.0)
            s_sparse = sparse_norm.get(cid, 0.0)
            combined_scores[cid] = (self.alpha * s_dense) + ((1.0 - self.alpha) * s_sparse)

        sorted_cids = sorted(combined_scores.keys(), key=lambda x: combined_scores[x], reverse=True)[:top_k]

        fused_results: List[SearchResult] = []
        for rank, cid in enumerate(sorted_cids, start=1):
            fused_results.append(SearchResult(
                chunk=chunk_map[cid],
                score=combined_scores[cid],
                rank=rank,
                retrieval_type="hybrid_convex"
            ))

        return fused_results
