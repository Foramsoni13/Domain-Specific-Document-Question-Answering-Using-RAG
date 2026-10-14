"""
Unit and Integration Tests for Domain-Specific RAG Pipeline.
"""

import os
import pytest
import numpy as np

from src.document_loader import DocumentLoader, DocumentPreprocessor, DocumentPage
from src.chunker import RecursiveCharacterChunker, TextChunk
from src.embeddings import EmbeddingEngine
from src.vector_store import FAISSVectorStore, SearchResult
from src.retriever import DenseRetriever, SparseRetriever, HybridRetriever
from src.reranker import CrossEncoderReranker
from src.guardrails import RAGGuardrails
from src.rag_engine import RAGEngine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

def test_document_preprocessor():
    raw_text = "  Section  1.1   —   Introduction \n\n\n  Multiple   spaces and quotes “test”.  "
    clean = DocumentPreprocessor.clean_text(raw_text)
    assert "“" not in clean
    assert "—" not in clean
    assert "Multiple spaces" in clean
    assert "\n\n\n" not in clean

def test_document_loader():
    loader = DocumentLoader()
    sample_pdf = os.path.join(DATA_DIR, "university_academic_regulations_2025.pdf")
    pages = loader.load_file(sample_pdf)
    assert len(pages) > 0
    assert pages[0].page_number == 1
    assert "APEX TECHNICAL UNIVERSITY" in pages[0].content

def test_recursive_chunker():
    chunker = RecursiveCharacterChunker(chunk_size=300, chunk_overlap=50)
    page = DocumentPage(
        doc_name="test_policy.txt",
        page_number=1,
        content="Section 1. Minimum attendance is 75%. Medical leave can condone down to 65% with approval. Failure leads to grade FA. Students must register on portal."
    )
    chunks = chunker.chunk_document_page(page)
    assert len(chunks) >= 1
    assert chunks[0].doc_name == "test_policy.txt"
    assert chunks[0].page_number == 1
    assert chunks[0].chunk_id.startswith("test_policy")

def test_embedding_engine():
    engine = EmbeddingEngine()
    texts = ["Attendance requirements", "Parental leave policy"]
    emb = engine.encode(texts, normalize=True)
    assert emb.shape == (2, 384)
    # Check unit norm
    norms = np.linalg.norm(emb, axis=1)
    np.testing.assert_allclose(norms, [1.0, 1.0], atol=1e-4)

def test_vector_store():
    store = FAISSVectorStore(embedding_dim=384)
    chunks = [
        TextChunk(chunk_id="c1", doc_name="doc1.pdf", page_number=1, content="Attendance criteria", chunk_index=0),
        TextChunk(chunk_id="c2", doc_name="doc2.pdf", page_number=2, content="Parental benefits", chunk_index=1),
    ]
    engine = EmbeddingEngine()
    embs = engine.encode([c.content for c in chunks], normalize=True)
    store.add_documents(chunks, embs)

    q_vec = engine.encode("How much attendance?", normalize=True)
    results = store.search(q_vec, top_k=2)
    assert len(results) == 2
    assert results[0].chunk.chunk_id == "c1"
    assert results[0].score > results[1].score

def test_guardrails_ood_refusal():
    guardrail = RAGGuardrails(rerank_threshold=0.20, similarity_threshold=0.35)
    # Simulate a very low scoring match
    dummy_chunk = TextChunk(chunk_id="c1", doc_name="doc1.pdf", page_number=1, content="University syllabus", chunk_index=0)
    low_res = [SearchResult(chunk=dummy_chunk, score=0.04, rank=1, retrieval_type="cross_encoder_reranked")]

    verdict = guardrail.evaluate_answerability("How do I bake a chocolate cake?", low_res)
    assert verdict.is_answerable is False
    assert "below the confidence threshold" in verdict.reason

def test_end_to_end_rag():
    engine = RAGEngine(enable_reranking=True, rerank_threshold=0.20)
    engine.ingest_documents(DATA_DIR)
    
    # In-domain query
    response = engine.query("What is the minimum attendance requirement?")
    assert not response.is_refused
    assert len(response.citations) > 0
    assert "75%" in response.answer

    # Out-of-domain query
    ood_response = engine.query("What is the capital of Australia?")
    assert ood_response.is_refused
    assert "Information Notice" in ood_response.answer

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
