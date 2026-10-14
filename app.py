"""
Streamlit Web Application for Domain-Specific Document Question Answering (RAG).
Provides an interactive GUI for document ingestion, semantic search, neural reranking,
grounded question answering with citations, and evaluation benchmarking.
"""

import os
import sys
import time
import json
import streamlit as st
import pandas as pd
import numpy as np

# Add workspace directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.rag_engine import RAGEngine
from src.metrics import RAGEvaluator

# Streamlit Page Configuration
st.set_page_config(
    page_title="DomainDoc-RAG | Question Answering System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .citation-card {
        background-color: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
    .refusal-card {
        background-color: #FEF2F2;
        border-left: 4px solid #EF4444;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 12px;
    }
    .success-card {
        background-color: #F0FDF4;
        border-left: 4px solid #10B981;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 12px;
    }
    .metric-badge {
        display: inline-block;
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_rag_engine():
    """Initializes and caches the RAG engine and pre-loads sample documents."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(base_dir, "data", "raw")
    
    engine = RAGEngine(
        chunk_size=450,
        chunk_overlap=80,
        enable_reranking=True,
        rerank_threshold=0.20
    )
    if os.path.exists(docs_dir):
        engine.ingest_documents(docs_dir)
    return engine

engine = load_rag_engine()

# --- SIDEBAR CONFIGURATION ---
st.sidebar.title("⚙️ RAG Engine Configuration")

st.sidebar.subheader("1. Ingestion & Documents")
uploaded_files = st.sidebar.file_uploader(
    "Upload Domain Documents (PDF, TXT, MD):",
    type=["pdf", "txt", "md", "docx"],
    accept_multiple_files=True
)

if uploaded_files:
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    new_paths = []
    for f in uploaded_files:
        save_path = os.path.join(upload_dir, f.name)
        with open(save_path, "wb") as out:
            out.write(f.getbuffer())
        new_paths.append(save_path)
    
    if st.sidebar.button("Re-Index Corpus with Uploads", type="primary"):
        with st.spinner("Ingesting and indexing documents..."):
            engine.ingest_documents(new_paths)
            st.sidebar.success(f"Indexed {len(new_paths)} uploaded documents!")

st.sidebar.subheader("2. Retrieval & Reranking")
retrieval_mode = st.sidebar.selectbox(
    "Retrieval Algorithm:",
    options=["hybrid", "dense", "sparse"],
    format_func=lambda x: {
        "hybrid": "Hybrid Search (Dense + BM25 RRF)",
        "dense": "Dense Semantic Only (FAISS)",
        "sparse": "Sparse Keyword Only (BM25)"
    }[x]
)

enable_rerank = st.sidebar.toggle("Cross-Encoder Neural Reranking", value=True)
top_k = st.sidebar.slider("Top-K Context Passages", min_value=1, max_value=8, value=3)
confidence_threshold = st.sidebar.slider(
    "Out-of-Domain Refusal Threshold",
    min_value=0.05,
    max_value=0.60,
    value=0.20,
    step=0.05,
    help="Queries scoring below this threshold are flagged as unanswerable to prevent hallucinations."
)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Corpus Statistics")
st.sidebar.metric("Indexed Chunks", len(engine.chunks))
st.sidebar.metric("Vector Dimensions", engine.embedding_engine.embedding_dim)
st.sidebar.caption("Model: all-MiniLM-L6-v2 | Reranker: ms-marco-MiniLM-L-6-v2")

# --- MAIN CONTENT TABS ---
st.markdown('<div class="main-header">Domain-Specific Document QA System</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Retrieval-Augmented Generation (RAG) with Dense Semantic Search, '
    'BM25 Hybrid Fusion, Cross-Encoder Reranking, and Hallucination Refusal Guardrails.</div>',
    unsafe_allow_html=True
)

tab_qa, tab_corpus, tab_eval, tab_arch = st.tabs([
    "💬 Question Answering",
    "📄 Document Corpus & Chunks",
    "📈 Benchmark Evaluation",
    "🏛️ System Architecture"
])

# --- TAB 1: QA PLAYGROUND ---
with tab_qa:
    st.markdown("### Ask a Domain-Specific Question")
    
    # Quick sample query pills
    sample_queries = [
        "What is the minimum attendance percentage for final exams?",
        "How many weeks of paid primary caregiver parental leave are provided?",
        "What is the property tax rebate for paying before June 30th?",
        "What is the capital of Australia and its population?",
        "What is the weekend dormitory curfew time for PhD students?"
    ]
    
    col_pills = st.columns(len(sample_queries))
    selected_query = None
    for i, sq in enumerate(sample_queries):
        label = sq[:28] + "..." if len(sq) > 28 else sq
        if col_pills[i].button(label, key=f"sq_{i}", help=sq):
            selected_query = sq

    user_query = st.text_input(
        "Enter question regarding university policies, HR guidelines, or municipal circulars:",
        value=selected_query or "",
        placeholder="e.g. What is the penalty for plagiarism in capstone projects?"
    )

    if st.button("Search & Generate Answer", type="primary") or user_query:
        if not user_query.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Retrieving, reranking, and verifying context..."):
                response = engine.query(
                    question=user_query,
                    retrieval_mode=retrieval_mode,
                    top_k=top_k,
                    apply_reranking=enable_rerank,
                    confidence_threshold=confidence_threshold
                )

            # Telemetry display
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            col_t1.metric("Retrieval Latency", f"{response.telemetry.get('retrieval_ms', 0):.1f} ms")
            col_t2.metric("Rerank Latency", f"{response.telemetry.get('rerank_ms', 0):.1f} ms")
            col_t3.metric("Total Latency", f"{response.telemetry.get('total_ms', 0):.1f} ms")
            conf_val = response.guardrail_verdict.confidence_score
            col_t4.metric("Relevance Confidence", f"{conf_val:.3f}", delta=f"{conf_val - confidence_threshold:.2f} vs thresh")

            # Answer or Refusal Banner
            if response.is_refused:
                st.markdown(
                    f'<div class="refusal-card">'
                    f'<h4>🛡️ Guardrail Alert: Question Refused</h4>'
                    f'<p>{response.answer}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="success-card">'
                    f'<h4>✅ Grounded Answer Generated</h4>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                st.markdown(response.answer)

            # Supporting Citations & Evidence
            st.markdown("---")
            st.markdown("### 🔍 Retrieved Evidence & Passage Inspector")
            if not response.retrieved_chunks:
                st.info("No passages were retrieved.")
            else:
                for idx, res in enumerate(response.retrieved_chunks, start=1):
                    chunk = res.chunk
                    with st.expander(f"Passage #{idx} | Doc: {chunk.doc_name} | Page {chunk.page_number} | Score: {res.score:.4f}", expanded=(idx == 1)):
                        st.markdown(f"**Document**: `{chunk.doc_name}` | **Page**: `{chunk.page_number}` | **Chunk ID**: `{chunk.chunk_id}`")
                        st.markdown(f"**Retrieval Type**: `{res.retrieval_type}` | **Relevance Score**: `{res.score:.4f}`")
                        st.text_area("Passage Text Content:", value=chunk.content, height=120, key=f"chunk_view_{idx}")

# --- TAB 2: DOCUMENT CORPUS VIEWER ---
with tab_corpus:
    st.markdown("### Ingested Document Collection & Chunks")
    st.write(f"The system currently maintains **{len(engine.chunks)} chunks** across domain documents.")

    if engine.chunks:
        docs_summary = {}
        for c in engine.chunks:
            docs_summary[c.doc_name] = docs_summary.get(c.doc_name, 0) + 1

        col_d1, col_d2 = st.columns([1, 2])
        with col_d1:
            st.markdown("#### Document Summary")
            for d_name, count in docs_summary.items():
                st.write(f"- **{d_name}**: {count} chunks")
        with col_d2:
            st.markdown("#### Chunk Browser")
            selected_doc = st.selectbox("Select document to inspect:", list(docs_summary.keys()))
            doc_chunks = [c for c in engine.chunks if c.doc_name == selected_doc]
            
            chunk_options = [f"{c.chunk_id} (Page {c.page_number}, {c.word_count} words)" for c in doc_chunks]
            selected_c_label = st.selectbox("Select chunk:", chunk_options)
            c_idx = chunk_options.index(selected_c_label)
            chosen_chunk = doc_chunks[c_idx]

            st.json({
                "chunk_id": chosen_chunk.chunk_id,
                "doc_name": chosen_chunk.doc_name,
                "page_number": chosen_chunk.page_number,
                "word_count": chosen_chunk.word_count,
                "char_count": chosen_chunk.char_count,
                "content": chosen_chunk.content
            })

# --- TAB 3: BENCHMARK EVALUATION ---
with tab_eval:
    st.markdown("### Quantitative Evaluation & Ablation Study")
    st.markdown(
        "Evaluate the RAG system against the standardized benchmark test suite "
        "comprising factoid, numeric threshold, and out-of-domain unanswerable queries."
    )

    benchmarks_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "eval_benchmarks.json")
    results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_results.json")

    if st.button("Run Live Benchmark Evaluation Suite", type="primary"):
        with st.spinner("Running ablation benchmarks across all configurations..."):
            evaluator = RAGEvaluator(benchmarks_path)
            configs = [
                {"name": "Dense Semantic Only (Bi-Encoder)", "mode": "dense", "rerank": False},
                {"name": "Sparse Lexical Only (BM25)", "mode": "sparse", "rerank": False},
                {"name": "Hybrid (Dense + BM25 RRF)", "mode": "hybrid", "rerank": False},
                {"name": "Full System (Hybrid + Cross-Encoder)", "mode": "hybrid", "rerank": True}
            ]
            eval_data = []
            for cfg in configs:
                res = evaluator.evaluate_engine(engine, retrieval_mode=cfg["mode"], apply_reranking=cfg["rerank"])
                res["pipeline_name"] = cfg["name"]
                eval_data.append(res)
            
            with open(results_path, "w", encoding="utf-8") as f:
                json.dump(eval_data, f, indent=2)
            st.success("Evaluation complete! Results saved.")

    # Load and display evaluation results
    if os.path.exists(results_path):
        with open(results_path, "r", encoding="utf-8") as f:
            eval_data = json.load(f)

        df_metrics = pd.DataFrame([
            {
                "Configuration": item["pipeline_name"],
                "Hit Rate@1 (%)": round(item["hit_rate_at_1"] * 100, 1),
                "Hit Rate@3 (%)": round(item["hit_rate_at_3"] * 100, 1),
                "MRR": round(item["mrr"], 3),
                "Refusal Accuracy (%)": round(item["refusal_accuracy"] * 100, 1),
                "Groundedness (%)": round(item["groundedness_score"] * 100, 1),
                "Avg Latency (ms)": round(item["avg_latency_ms"], 1)
            }
            for item in eval_data
        ])

        st.dataframe(df_metrics, use_container_width=True)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("#### Retrieval Accuracy: Hit Rate@1 vs MRR")
            st.bar_chart(df_metrics.set_index("Configuration")[["Hit Rate@1 (%)", "Hit Rate@3 (%)"]])
        with col_c2:
            st.markdown("#### Latency vs Groundedness Trade-off")
            st.line_chart(df_metrics.set_index("Configuration")[["Groundedness (%)", "Avg Latency (ms)"]])
    else:
        st.info("Run the benchmark evaluation above or run `python3 evaluate.py` to view metrics.")

# --- TAB 4: ARCHITECTURE & METHODOLOGY ---
with tab_arch:
    st.markdown("### System Architecture & NLP Workflow")
    st.markdown("""
    The system follows a production-grade 6-stage Retrieval-Augmented Generation (RAG) architecture:
    
    1. **Document Ingestion & Preprocessing**:
       - Page-aware PDF and text parsing preserving layout and metadata.
       - Text normalization: Unicode standardization, whitespace correction, bullet point retention.
       
    2. **Recursive Character Chunking**:
       - Splits along hierarchical boundaries (`\\n\\n`, `\\n`, `. `, words) with chunk overlap.
       - Injects document and page number metadata into every chunk for citation tracking.
       
    3. **Vector Embeddings**:
       - Encodes chunks using `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions).
       - L2 unit-norm vectors indexed into FAISS `IndexFlatIP` for exact cosine similarity search.
       
    4. **Hybrid Retrieval**:
       - Combines Dense Semantic Search (FAISS) with Sparse Lexical Search (BM25Okapi).
       - Merges candidates using **Reciprocal Rank Fusion (RRF)**:
         $$RRF(d) = \\sum_{m \\in \\{dense, sparse\\}} \\frac{1}{k + \\text{rank}_m(d)}$$
         
    5. **Cross-Encoder Neural Reranking**:
       - Joint query-passage cross-attention using `cross-encoder/ms-marco-MiniLM-L-6-v2`.
       - Sigmoid score calibration maps logits into $[0, 1]$ confidence probabilities.
       
    6. **Guardrails & Grounded Generation**:
       - Identifies unanswerable/out-of-domain queries when reranker confidence drops below threshold $\\tau$.
       - Grounded answer synthesis with explicit document and page number references.
    """)
