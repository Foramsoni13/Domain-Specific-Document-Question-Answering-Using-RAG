"""
RAG Engine Orchestrator for Domain-Specific Question Answering.
Coordinates Preprocessing, Chunking, Embeddings, Hybrid Retrieval,
Cross-Encoder Reranking, Guardrails, and Grounded Citation Generation.
"""

import os
import time
import re
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np

from src.document_loader import DocumentLoader, DocumentPage
from src.chunker import RecursiveCharacterChunker, TextChunk
from src.embeddings import EmbeddingEngine
from src.vector_store import FAISSVectorStore, SearchResult
from src.retriever import DenseRetriever, SparseRetriever, HybridRetriever
from src.reranker import CrossEncoderReranker
from src.guardrails import RAGGuardrails, GuardrailVerdict

class RAGResponse:
    """Encapsulates the end-to-end question-answering result with citations and telemetry."""
    def __init__(
        self,
        query: str,
        answer: str,
        is_refused: bool,
        citations: List[Dict[str, Any]],
        retrieved_chunks: List[SearchResult],
        guardrail_verdict: GuardrailVerdict,
        telemetry: Dict[str, float]
    ):
        self.query = query
        self.answer = answer
        self.is_refused = is_refused
        self.citations = citations
        self.retrieved_chunks = retrieved_chunks
        self.guardrail_verdict = guardrail_verdict
        self.telemetry = telemetry

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "answer": self.answer,
            "is_refused": self.is_refused,
            "citations": self.citations,
            "retrieved_chunks": [r.to_dict() for r in self.retrieved_chunks],
            "guardrail_verdict": self.guardrail_verdict.to_dict(),
            "telemetry": self.telemetry
        }

    def __repr__(self) -> str:
        status = "REFUSED" if self.is_refused else "ANSWERED"
        return f"<RAGResponse [{status}] query='{self.query[:40]}' citations={len(self.citations)} latency={self.telemetry.get('total_ms', 0):.1f}ms>"


class RAGEngine:
    """
    Main Domain-Specific RAG System orchestrator.
    """

    def __init__(
        self,
        chunk_size: int = 450,
        chunk_overlap: int = 80,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        enable_reranking: bool = True,
        rerank_threshold: float = 0.20
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.enable_reranking = enable_reranking

        # Pipeline components
        self.loader = DocumentLoader()
        self.chunker = RecursiveCharacterChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.embedding_engine = EmbeddingEngine(model_name=embedding_model)
        self.vector_store = FAISSVectorStore(embedding_dim=self.embedding_engine.embedding_dim)
        self.reranker = CrossEncoderReranker(model_name=reranker_model) if enable_reranking else None
        self.guardrails = RAGGuardrails(rerank_threshold=rerank_threshold)

        # Corpus state
        self.chunks: List[TextChunk] = []
        self.dense_retriever: Optional[DenseRetriever] = None
        self.sparse_retriever: Optional[SparseRetriever] = None
        self.hybrid_retriever: Optional[HybridRetriever] = None
        self.is_indexed: bool = False

    def ingest_documents(self, file_paths_or_dir: Union[str, List[str]]):
        """Loads and indexes documents into both dense and sparse vector stores."""
        start_time = time.time()
        pages: List[DocumentPage] = []

        if isinstance(file_paths_or_dir, str):
            if os.path.isdir(file_paths_or_dir):
                pages = self.loader.load_directory(file_paths_or_dir)
            else:
                pages = self.loader.load_file(file_paths_or_dir)
        else:
            for p in file_paths_or_dir:
                pages.extend(self.loader.load_file(p))

        if not pages:
            print("[RAGEngine] Warning: No pages loaded.")
            return

        print(f"[RAGEngine] Ingested {len(pages)} pages. Generating text chunks...")
        self.chunks = self.chunker.chunk_document_pages(pages)
        print(f"[RAGEngine] Generated {len(self.chunks)} text chunks.")

        # Compute dense embeddings
        print("[RAGEngine] Encoding chunks into vector space...")
        chunk_texts = [c.content for c in self.chunks]
        embeddings = self.embedding_engine.encode(chunk_texts, normalize=True)

        # Index in FAISS
        self.vector_store.clear()
        self.vector_store.add_documents(self.chunks, embeddings)

        # Build dense, sparse, and hybrid retrievers
        self.dense_retriever = DenseRetriever(self.vector_store, self.embedding_engine)
        self.sparse_retriever = SparseRetriever(self.chunks)
        self.hybrid_retriever = HybridRetriever(self.dense_retriever, self.sparse_retriever)

        self.is_indexed = True
        elapsed = time.time() - start_time
        print(f"[RAGEngine] Indexing completed in {elapsed:.2f}s across {len(self.chunks)} chunks.")

    def query(
        self,
        question: str,
        retrieval_mode: str = "hybrid",  # "dense", "sparse", or "hybrid"
        top_k: int = 4,
        apply_reranking: Optional[bool] = None,
        confidence_threshold: Optional[float] = None
    ) -> RAGResponse:
        """
        Executes end-to-end question answering on the ingested corpus.
        """
        if not self.is_indexed or not self.chunks:
            verdict = GuardrailVerdict(is_answerable=False, confidence_score=0.0, reason="No corpus indexed.")
            return RAGResponse(
                query=question,
                answer="No documents have been indexed in the system yet. Please ingest documents first.",
                is_refused=True,
                citations=[],
                retrieved_chunks=[],
                guardrail_verdict=verdict,
                telemetry={"total_ms": 0.0}
            )

        t_start = time.time()
        use_rerank = self.enable_reranking if apply_reranking is None else apply_reranking

        # 1. Retrieval Phase
        t_ret_start = time.time()
        retrieval_candidates = top_k * 3 if use_rerank else top_k

        if retrieval_mode == "dense" and self.dense_retriever:
            retrieved = self.dense_retriever.search(question, top_k=retrieval_candidates)
        elif retrieval_mode == "sparse" and self.sparse_retriever:
            retrieved = self.sparse_retriever.search(question, top_k=retrieval_candidates)
        else:
            retrieved = self.hybrid_retriever.search(question, top_k=retrieval_candidates, fusion_method="rrf")

        retrieval_ms = (time.time() - t_ret_start) * 1000

        # 2. Reranking Phase
        t_rerank_start = time.time()
        if use_rerank and self.reranker and retrieved:
            final_passages = self.reranker.rerank(question, retrieved, top_n=top_k)
        else:
            final_passages = retrieved[:top_k]
        rerank_ms = (time.time() - t_rerank_start) * 1000

        # 3. Guardrail / Refusal Phase
        if confidence_threshold is not None:
            self.guardrails.rerank_threshold = confidence_threshold

        verdict = self.guardrails.evaluate_answerability(question, final_passages)

        if not verdict.is_answerable:
            refusal_text = self.guardrails.generate_refusal_message(question, verdict)
            total_ms = (time.time() - t_start) * 1000
            return RAGResponse(
                query=question,
                answer=refusal_text,
                is_refused=True,
                citations=[],
                retrieved_chunks=final_passages,
                guardrail_verdict=verdict,
                telemetry={
                    "retrieval_ms": round(retrieval_ms, 2),
                    "rerank_ms": round(rerank_ms, 2),
                    "generation_ms": 0.0,
                    "total_ms": round(total_ms, 2)
                }
            )

        # 4. Grounded Synthesis & Citation Phase
        t_gen_start = time.time()
        answer, citations = self._synthesize_grounded_answer(question, final_passages)
        gen_ms = (time.time() - t_gen_start) * 1000

        total_ms = (time.time() - t_start) * 1000
        return RAGResponse(
            query=question,
            answer=answer,
            is_refused=False,
            citations=citations,
            retrieved_chunks=final_passages,
            guardrail_verdict=verdict,
            telemetry={
                "retrieval_ms": round(retrieval_ms, 2),
                "rerank_ms": round(rerank_ms, 2),
                "generation_ms": round(gen_ms, 2),
                "total_ms": round(total_ms, 2)
            }
        )

    def _synthesize_grounded_answer(
        self,
        query: str,
        passages: List[SearchResult]
    ) -> (str, List[Dict[str, Any]]):
        """
        Synthesizes a grounded, verifiable answer from retrieved passages
        and formats explicit document/page reference citations.
        """
        citations: List[Dict[str, Any]] = []
        answer_paragraphs: List[str] = []

        q_terms = set(re.findall(r"\b[a-zA-Z0-9_\$%-]+\b", query.lower()))

        for rank, res in enumerate(passages, start=1):
            chunk = res.chunk
            citation_item = {
                "source_doc": chunk.doc_name,
                "page": chunk.page_number,
                "chunk_id": chunk.chunk_id,
                "relevance_score": round(res.score, 4),
                "rank": rank,
                "text_snippet": chunk.content[:140] + "..." if len(chunk.content) > 140 else chunk.content
            }
            citations.append(citation_item)

            # Extract sentences from chunk that address the query
            sentences = re.split(r"(?<=[.!?])\s+", chunk.content)
            scored_sentences = []
            for s in sentences:
                s_lower = s.lower()
                matches = sum(1 for term in q_terms if term in s_lower)
                if matches > 0:
                    scored_sentences.append((matches, s.strip()))

            if scored_sentences:
                scored_sentences.sort(key=lambda x: x[0], reverse=True)
                top_s = [item[1] for item in scored_sentences[:3]]
                para = " ".join(top_s)
                answer_paragraphs.append(
                    f"{para} **[Ref: {chunk.doc_name}, Page {chunk.page_number}]**"
                )
            else:
                answer_paragraphs.append(
                    f"{chunk.content} **[Ref: {chunk.doc_name}, Page {chunk.page_number}]**"
                )

        # Synthesize consolidated answer
        lead_summary = f"Based on the official provisions in **{passages[0].chunk.doc_name}** (Page {passages[0].chunk.page_number}):\n\n"
        body = "\n\n".join(f"• {p}" for p in answer_paragraphs[:2])

        citations_footer = "\n\n### Supporting Document References:\n"
        for c in citations[:3]:
            citations_footer += f"- **Document**: `{c['source_doc']}` | **Page**: `{c['page']}` | **Confidence**: `{c['relevance_score']}`\n"

        full_answer = lead_summary + body + citations_footer
        return full_answer, citations
