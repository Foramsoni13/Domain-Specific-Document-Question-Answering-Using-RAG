"""
Streamlit Web Application for Domain-Specific Document Question Answering (RAG).
Enterprise-Grade UI with Clean Modern Aesthetics, Real-Time Telemetry,
Grounded Citations, Passage Inspection, and Interactive Evaluation.
"""

import os
import sys
import time
import json
import streamlit as st
import pandas as pd
import numpy as np

# Auto-launch with Streamlit CLI if executed directly via `python3 app.py`
try:
    import streamlit.runtime
    if not streamlit.runtime.exists():
        from streamlit.web import cli as stcli
        sys.argv = ["streamlit", "run", sys.argv[0]] + sys.argv[1:]
        sys.exit(stcli.main())
except (ImportError, Exception):
    pass

# Add workspace directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.rag_engine import RAGEngine
from src.metrics import RAGEvaluator

# Streamlit Page Configuration
st.set_page_config(
    page_title="DocGrounded RAG | Enterprise Document QA",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Design System CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Top Brand Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
    }
    
    .hero-tagline {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(56, 189, 248, 0.12);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    
    .hero-title {
        color: #FFFFFF;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0 0 6px 0;
        line-height: 1.2;
    }
    
    .hero-desc {
        color: #94A3B8;
        font-size: 0.95rem;
        margin: 0;
        max-width: 900px;
        line-height: 1.5;
    }

    .hero-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 14px;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.06);
        color: #E2E8F0;
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 500;
    }

    /* Cards & Glassmorphism */
    .pro-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    /* Success / Grounded Card */
    .grounded-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .answer-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 20px;
        font-size: 1.0rem;
        line-height: 1.65;
        color: #1E293B;
        margin-top: 8px;
    }

    /* Guardrail Refusal Card */
    .refusal-container {
        background: #FFF1F2;
        border: 1px solid #FECDD3;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 20px;
    }

    .refusal-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #FFE4E6;
        color: #9F1239;
        border: 1px solid #FDA4AF;
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 10px;
    }

    /* Micro-Telemetry Cards */
    .telemetry-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 16px;
    }

    .telemetry-chip {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 10px 14px;
        text-align: center;
    }

    .telemetry-chip .val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
    }

    .telemetry-chip .lbl {
        font-size: 0.72rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 2px;
    }

    /* Citation Tag */
    .citation-tag {
        display: inline-block;
        background: #EFF6FF;
        color: #1E40AF;
        border: 1px solid #BFDBFE;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Citation Summary Card */
    .citation-summary-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #2563EB;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Document Capsule Card */
    .doc-capsule {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        transition: border-color 0.2s ease;
    }
    .doc-capsule:hover {
        border-color: #3B82F6;
    }

    /* Step Card */
    .step-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    .step-number {
        display: inline-block;
        background: #2563EB;
        color: white;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        text-align: center;
        line-height: 26px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-right: 8px;
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

# --- TOP BRAND HERO BANNER ---
st.markdown("""
<div class="hero-container">
    <div class="hero-tagline">
        <span>⚡ Enterprise NLP Architecture</span> • <span>Problem Statement #9</span>
    </div>
    <h1 class="hero-title">Domain-Specific Document Question Answering</h1>
    <p class="hero-desc">
        A grounded, audit-ready Retrieval-Augmented Generation (RAG) platform. Features page-level PDF ingestion, 
        dense-sparse hybrid retrieval (FAISS + BM25Okapi), deep neural cross-encoder reranking, and proactive hallucination guardrails.
    </p>
    <div class="hero-badges">
        <span class="status-pill">🟢 <b>Vector Index</b>: FAISS IndexFlatIP (384-dim)</span>
        <span class="status-pill">🧠 <b>Bi-Encoder</b>: all-MiniLM-L6-v2</span>
        <span class="status-pill">🎯 <b>Neural Reranker</b>: ms-marco-MiniLM-L-6-v2</span>
        <span class="status-pill">🛡️ <b>Refusal Guardrail</b>: Calibrated Sigmoid (τ = 0.20)</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.markdown("### ⚙️ Engine Control Panel")
    
    with st.expander("📁 Document Ingestion & Corpus", expanded=True):
        st.caption("Upload institutional circulars, regulations, or handbooks:")
        uploaded_files = st.file_uploader(
            "Upload Files (PDF, TXT, DOCX):",
            type=["pdf", "txt", "md", "docx"],
            accept_multiple_files=True,
            label_visibility="collapsed"
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
            
            if st.button("⚡ Index Uploaded Documents", type="primary", use_container_width=True):
                with st.spinner("Parsing pages and computing vector embeddings..."):
                    engine.ingest_documents(new_paths)
                    st.success(f"Indexed {len(new_paths)} documents!")

    with st.expander("🔍 Retrieval & Neural Tuning", expanded=True):
        retrieval_mode = st.selectbox(
            "Retrieval Strategy:",
            options=["hybrid", "dense", "sparse"],
            format_func=lambda x: {
                "hybrid": "🔀 Hybrid Search (Dense + BM25 RRF)",
                "dense": "🧬 Dense Semantic Only (FAISS)",
                "sparse": "🔤 Sparse Keyword Only (BM25)"
            }[x]
        )

        enable_rerank = st.toggle("Cross-Encoder Neural Reranking", value=True, help="Computes joint query-passage cross-attention for high precision.")
        top_k = st.slider("Top-K Context Passages", min_value=1, max_value=8, value=3)
        confidence_threshold = st.slider(
            "Out-of-Domain Refusal Threshold (τ)",
            min_value=0.05,
            max_value=0.60,
            value=0.20,
            step=0.05,
            help="Queries scoring below this threshold trigger safe refusal to prevent hallucinations."
        )

    st.markdown("---")
    st.markdown("#### 📊 Corpus Telemetry")
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("Indexed Chunks", len(engine.chunks))
    col_s2.metric("Embedding Dim", engine.embedding_engine.embedding_dim)
    st.caption(f"Hardware: **{engine.embedding_engine.device.upper()}** • FAISS Index: **Active**")

# --- MAIN NAVIGATION TABS ---
tab_qa, tab_corpus, tab_eval, tab_arch = st.tabs([
    "💬 Question Answering Console",
    "📚 Document Corpus & Chunks",
    "📈 Quantitative Evaluation & Ablation",
    "🏛️ System Architecture & Workflow"
])

# --- TAB 1: QA PLAYGROUND ---
with tab_qa:
    st.markdown("### 💬 Ask a Regulatory or Policy Question")
    st.caption("Select a curated sample query or type your own question across University, HR, or Municipal domains:")

    # Quick prompt presets with domain pills
    col_q1, col_q2, col_q3 = st.columns(3)
    preset_query = None

    if col_q1.button("🎓 [Univ] Attendance requirement?", use_container_width=True):
        preset_query = "What is the minimum attendance percentage required to be eligible for the End-Semester Examination?"
    if col_q2.button("💼 [HR] Parental leave duration?", use_container_width=True):
        preset_query = "How much paid primary caregiver parental leave is provided, and what is the eligibility criteria?"
    if col_q3.button("🏛️ [Muni] Property tax early rebate?", use_container_width=True):
        preset_query = "What is the rebate percentage for early settlement of annual property tax before June 30th?"

    col_q4, col_q5 = st.columns(2)
    if col_q4.button("🚫 [OOD] Capital of Australia? (Safe Refusal Test)", use_container_width=True):
        preset_query = "What is the capital city of Australia and what is its population?"
    if col_q5.button("🚫 [OOD] PhD weekend curfew rule? (Domain Absence)", use_container_width=True):
        preset_query = "What is the dormitory curfew time on weekends for postgraduate doctoral students?"

    # Query Input Bar
    user_query = st.text_input(
        "Enter query:",
        value=preset_query or "",
        placeholder="Type a policy, regulation, or citizen service question...",
        label_visibility="collapsed"
    )

    col_btn, _ = st.columns([1, 4])
    run_search = col_btn.button("🔍 Search & Generate Answer", type="primary", use_container_width=True)

    if run_search or user_query:
        if not user_query.strip():
            st.warning("Please enter a question to query the system.")
        else:
            with st.spinner("Executing hybrid retrieval, cross-encoder reranking, and guardrail verification..."):
                response = engine.query(
                    question=user_query,
                    retrieval_mode=retrieval_mode,
                    top_k=top_k,
                    apply_reranking=enable_rerank,
                    confidence_threshold=confidence_threshold
                )

            # Telemetry Bar
            t_ret = response.telemetry.get("retrieval_ms", 0.0)
            t_rr = response.telemetry.get("rerank_ms", 0.0)
            t_tot = response.telemetry.get("total_ms", 0.0)
            c_score = response.guardrail_verdict.confidence_score

            st.markdown(f"""
            <div class="telemetry-grid">
                <div class="telemetry-chip">
                    <div class="val">{t_ret:.1f} ms</div>
                    <div class="lbl">Hybrid Retrieval</div>
                </div>
                <div class="telemetry-chip">
                    <div class="val">{t_rr:.1f} ms</div>
                    <div class="lbl">Neural Rerank</div>
                </div>
                <div class="telemetry-chip">
                    <div class="val">{t_tot:.1f} ms</div>
                    <div class="lbl">Total Latency</div>
                </div>
                <div class="telemetry-chip">
                    <div class="val">{c_score:.3f}</div>
                    <div class="lbl">Relevance Confidence</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Display Response or Guardrail Notice
            if response.is_refused:
                st.markdown(f"""
                <div class="refusal-container">
                    <div class="refusal-badge">🛡️ Guardrail Intercepted: Out-of-Domain / Unanswerable</div>
                    <h4 style="margin: 4px 0 8px 0; color: #881337;">Question Safely Declined to Prevent Hallucination</h4>
                    <p style="margin: 0; color: #4C0519; font-size: 0.95rem;">{response.guardrail_verdict.reason}</p>
                    <div style="margin-top: 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #9F1239;">
                        Observed Confidence: <b>{c_score:.4f}</b> &lt; Threshold: <b>{confidence_threshold:.2f}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="grounded-badge">✅ 100% Grounded Context • Verifiable Attributions</div>
                """, unsafe_allow_html=True)
                
                # Render answer cleanly
                st.markdown(f'<div class="answer-box">{response.answer}</div>', unsafe_allow_html=True)

            # Evidence & Passage Inspector
            st.markdown("---")
            st.markdown("### 🔍 Retrieved Evidence & Cross-Attention Inspector")

            if not response.retrieved_chunks:
                st.info("No passages retrieved.")
            else:
                for idx, res in enumerate(response.retrieved_chunks, start=1):
                    chunk = res.chunk
                    badge_color = "#2563EB" if idx == 1 else "#64748B"
                    
                    with st.expander(f"Passage #{idx} • {chunk.doc_name} (Page {chunk.page_number}) • Score: {res.score:.4f}", expanded=(idx == 1)):
                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                        col_m1.markdown(f"**Document**: `{chunk.doc_name}`")
                        col_m2.markdown(f"**Page**: `{chunk.page_number}`")
                        col_m3.markdown(f"**Retrieval Type**: `{res.retrieval_type}`")
                        col_m4.markdown(f"**Rerank Score**: `{res.score:.4f}`")

                        st.markdown("**Evidence Text Chunk:**")
                        st.info(chunk.content)
                        st.caption(f"Chunk ID: `{chunk.chunk_id}` | Words: {chunk.word_count} | Characters: {chunk.char_count}")

# --- TAB 2: DOCUMENT CORPUS VIEWER ---
with tab_corpus:
    st.markdown("### 📚 Institutional Knowledge Base")
    st.write(f"The system maintains **{len(engine.chunks)} indexed text chunks** with page-level provenance across regulatory documents.")

    if engine.chunks:
        docs_summary = {}
        for c in engine.chunks:
            docs_summary[c.doc_name] = docs_summary.get(c.doc_name, 0) + 1

        col_left, col_right = st.columns([1, 2])
        with col_left:
            st.markdown("#### Indexed Document Catalog")
            for d_name, count in docs_summary.items():
                domain_tag = "🎓 University" if "univ" in d_name.lower() else ("💼 HR Policy" if "hr" in d_name.lower() else "🏛️ Municipal")
                st.markdown(f"""
                <div class="doc-capsule">
                    <div style="font-weight: 700; color: #1E293B; font-size: 0.95rem;">{d_name}</div>
                    <div style="font-size: 0.8rem; color: #64748B; margin: 4px 0;">{domain_tag}</div>
                    <div style="display: flex; gap: 8px; margin-top: 6px;">
                        <span class="citation-tag">{count} Chunks</span>
                        <span class="citation-tag">Page-Aware</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col_right:
            st.markdown("#### Chunk Deep Inspector")
            selected_doc = st.selectbox("Select document to browse:", list(docs_summary.keys()))
            doc_chunks = [c for c in engine.chunks if c.doc_name == selected_doc]
            
            chunk_labels = [f"Page {c.page_number} • Chunk {c.chunk_index + 1} ({c.word_count} words)" for c in doc_chunks]
            selected_c_label = st.selectbox("Select chunk to view:", chunk_labels)
            c_idx = chunk_labels.index(selected_c_label)
            chosen_chunk = doc_chunks[c_idx]

            st.markdown(f"**Chunk ID**: `{chosen_chunk.chunk_id}`")
            st.text_area("Normalized Content:", value=chosen_chunk.content, height=180)
            st.json({
                "doc_name": chosen_chunk.doc_name,
                "page_number": chosen_chunk.page_number,
                "word_count": chosen_chunk.word_count,
                "char_count": chosen_chunk.char_count,
                "metadata": chosen_chunk.metadata
            })

# --- TAB 3: BENCHMARK EVALUATION ---
with tab_eval:
    st.markdown("### 📈 Quantitative Benchmarks & Ablation Study")
    st.caption("Standardized evaluation across 15 domain test queries (factoid, numeric threshold, and out-of-domain refusals).")

    benchmarks_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "eval_benchmarks.json")
    results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_results.json")

    col_btn_eval, _ = st.columns([1, 3])
    if col_btn_eval.button("⚡ Run Full Ablation Benchmark", type="primary", use_container_width=True):
        with st.spinner("Running benchmark suite across all 4 pipeline configurations..."):
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
            st.success("Ablation benchmarks complete! Telemetry updated.")

    if os.path.exists(results_path):
        with open(results_path, "r", encoding="utf-8") as f:
            eval_data = json.load(f)

        # KPI Header Cards
        full_sys = next((item for item in eval_data if "Full System" in item["pipeline_name"]), eval_data[-1])
        
        st.markdown(f"""
        <div class="telemetry-grid" style="margin: 16px 0;">
            <div class="telemetry-chip">
                <div class="val" style="color: #10B981;">{full_sys['hit_rate_at_1'] * 100:.1f}%</div>
                <div class="lbl">Hit Rate@1</div>
            </div>
            <div class="telemetry-chip">
                <div class="val" style="color: #2563EB;">{full_sys['mrr']:.3f}</div>
                <div class="lbl">Mean Reciprocal Rank (MRR)</div>
            </div>
            <div class="telemetry-chip">
                <div class="val" style="color: #6366F1;">{full_sys['refusal_accuracy'] * 100:.1f}%</div>
                <div class="lbl">Refusal Accuracy (OOD)</div>
            </div>
            <div class="telemetry-chip">
                <div class="val" style="color: #0F172A;">{full_sys['avg_latency_ms']:.1f} ms</div>
                <div class="lbl">Avg Latency</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        df_metrics = pd.DataFrame([
            {
                "Pipeline Configuration": item["pipeline_name"],
                "Hit Rate@1": f"{item['hit_rate_at_1'] * 100:.1f}%",
                "Hit Rate@3": f"{item['hit_rate_at_3'] * 100:.1f}%",
                "MRR": f"{item['mrr']:.3f}",
                "Refusal Accuracy": f"{item['refusal_accuracy'] * 100:.1f}%",
                "Groundedness": f"{item['groundedness_score'] * 100:.1f}%",
                "Avg Latency": f"{item['avg_latency_ms']:.1f} ms"
            }
            for item in eval_data
        ])

        st.markdown("#### Comparative Ablation Matrix")
        st.dataframe(df_metrics, use_container_width=True)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("#### Retrieval Accuracy: Hit Rate@1 vs MRR")
            chart_data = pd.DataFrame([
                {"Configuration": item["pipeline_name"], "Hit@1 (%)": item["hit_rate_at_1"] * 100, "MRR": item["mrr"]}
                for item in eval_data
            ]).set_index("Configuration")
            st.bar_chart(chart_data)

        with col_c2:
            st.markdown("#### Latency vs Groundedness Trade-off")
            lat_data = pd.DataFrame([
                {"Configuration": item["pipeline_name"], "Latency (ms)": item["avg_latency_ms"], "Groundedness (%)": item["groundedness_score"] * 100}
                for item in eval_data
            ]).set_index("Configuration")
            st.line_chart(lat_data)

# --- TAB 4: ARCHITECTURE & METHODOLOGY ---
with tab_arch:
    st.markdown("### 🏛️ Multi-Stage RAG Pipeline Architecture")
    st.caption("How queries flow from user prompt to grounded, page-attributed response:")

    stages = [
        ("1. Document Ingestion & Page Tracking", "pypdfium2 / PyPDF2", 
         "Extracts raw text page-by-page while preserving exact page boundaries and document names. Sanitizes text using NFKC Unicode normalization."),
        ("2. Hierarchical Recursive Chunking", "RecursiveCharacterChunker", 
         "Splits hierarchically along paragraphs (\\n\\n), lines (\\n), sentences (. ! ?), and words with 450-char chunk size and 80-char overlap."),
        ("3. Dense Vector Embeddings", "sentence-transformers/all-MiniLM-L6-v2", 
         "Maps text chunks to 384-dimensional dense vectors with L2 normalization, indexed in FAISS IndexFlatIP for exact cosine similarity search."),
        ("4. Hybrid Retrieval & Score Fusion", "Reciprocal Rank Fusion (RRF)", 
         "Fuses dense semantic retrieval with sparse BM25 keyword matching (k=60): RRF(d) = sum(1 / (k + rank_m(d))), ensuring high recall and code precision."),
        ("5. Neural Cross-Encoder Reranking", "cross-encoder/ms-marco-MiniLM-L-6-v2", 
         "Joint query-chunk cross-attention reranks the top 12 candidate passages. Sigmoid calibration maps logits to [0, 1] confidence scores."),
        ("6. Hallucination Shield & Citations", "RAGGuardrails & Citation Synthesizer", 
         "Declines queries scoring below threshold (τ = 0.20) or missing key entity overlap. Synthesizes answers with explicit [Doc: X | Page: Y] references.")
    ]

    for title_s, tech_s, desc_s in stages:
        st.markdown(f"""
        <div class="step-card">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <span style="font-weight: 700; color: #0F172A; font-size: 1.05rem;">{title_s}</span>
                <span class="citation-tag">{tech_s}</span>
            </div>
            <p style="color: #475569; font-size: 0.92rem; margin: 0; line-height: 1.5;">{desc_s}</p>
        </div>
        """, unsafe_allow_html=True)
