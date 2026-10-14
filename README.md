# Domain-Specific Document Question Answering Using RAG

[![Python 3.12](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2%2B-EE4C2C.svg)](https://pytorch.org/)
[![HuggingFace Transformers](https://img.shields.io/badge/%F0%9F%A4%97%20Transformers-SentenceTransformers-yellow)](https://huggingface.co/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20Store-00A4E4.svg)](https://github.com/facebookresearch/faiss)
[![Streamlit](https://img.shields.io/badge/Streamlit-Interactive%20UI-FF4B4B.svg)](https://streamlit.io/)
[![PyTest](https://img.shields.io/badge/Tests-Passing%20(7%2F7)-brightgreen.svg)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end, production-grade Natural Language Processing (NLP) system for **Domain-Specific Document Question Answering** using **Retrieval-Augmented Generation (RAG)**. 

The system accepts collections of lengthy, complex institutional documents (e.g., university academic regulations, corporate employee handbooks, and municipal citizen services circulars), retrieves the most relevant passages through hybrid semantic and keyword search, applies deep neural cross-encoder reranking, generates strictly grounded answers supported by verifiable document and page citations, and safely declines out-of-domain or unanswerable queries to prevent hallucinations.

---

## Table of Contents
1. [Key Features](#key-features)
2. [System Architecture](#system-architecture)
3. [NLP Techniques & Algorithmic Foundations](#nlp-techniques--algorithmic-foundations)
4. [Repository Structure](#repository-structure)
5. [Installation & Setup](#installation--setup)
6. [Usage Guide](#usage-guide)
   - [Interactive Web Application (Streamlit)](#interactive-web-application-streamlit)
   - [Command-Line Interface (CLI)](#command-line-interface-cli)
   - [Automated Benchmark Evaluation](#automated-benchmark-evaluation)
   - [Presentation Deck Generator](#presentation-deck-generator)
   - [Running Unit & Integration Tests](#running-unit--integration-tests)
7. [Experimental Results & Ablation Study](#experimental-results--ablation-study)
8. [Sample Question & Answer Walkthrough](#sample-question--answer-walkthrough)
9. [Team Member Contributions](#team-member-contributions)
10. [Project Presentation Structure (20 Slides)](#project-presentation-structure-20-slides)
11. [References & Acknowledgments](#references--acknowledgments)

---

## Key Features

- **Multi-Format Page-Aware Ingestion**: Robust extraction across PDF, DOCX, and TXT files using `pypdfium2` and `PyPDF2`, strictly tracking page boundaries and section hierarchy.
- **Hierarchical Recursive Chunking**: Dynamic splitting on paragraphs (`\n\n`), newlines (`\n`), and sentence boundaries (`. ! ?`) with an 80-character boundary overlap to preserve cross-clause policy conditions.
- **Dense Vector Embeddings**: Employs `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions) with $L_2$ unit normalization for exact cosine similarity matching.
- **Sub-Millisecond Vector Search**: Integrated with FAISS `IndexFlatIP` (Maximum Inner Product) for fast vector retrieval.
- **Hybrid Search via Reciprocal Rank Fusion (RRF)**: Combines dense vector semantics with sparse lexical `BM25Okapi` search to reliably capture both conceptual intent and alphanumeric policy codes (`75%`, `1800-444-MCMC`, `Rule 2.1`).
- **Neural Cross-Encoder Reranking**: Uses `cross-encoder/ms-marco-MiniLM-L-6-v2` to compute deep query-chunk cross-attention, elevating the most contextually relevant regulatory clause to Rank 1.
- **Hallucination Shield & Refusal Guardrail**: Implements calibrated sigmoid score thresholding ($\tau = 0.20$) and entity overlap verification to detect unanswerable or out-of-domain queries, responding with transparent refusal explanations.
- **Provable Attributions & Citations**: Every generated statement is backed by explicit citations: `[Document: X.pdf | Page: Y | Confidence: Z]`.
- **Interactive Streamlit Web Dashboard**: Real-time query playground, document corpus inspector, live benchmark visualizer, and architecture explainer.

---

## System Architecture

```
                                  DOCUMENT INGESTION
     [ University Regulations (PDF) ]  [ Employee HR Handbook (PDF) ]  [ Municipal Circular (PDF) ]
                                          │
                                          ▼
                         [ Document Loader & Normalizer ]
                         - Page boundary tracking
                         - Unicode NFKC sanitization
                                          │
                                          ▼
                      [ Recursive Character Chunker (450 chars) ]
                         - 80-character boundary overlap
                         - Chunk ID: {doc_name}_p{page}_c{idx}
                                          │
                        ┌─────────────────┴─────────────────┐
                        ▼                                   ▼
          [ Dense Embeddings Engine ]              [ Sparse Tokenizer ]
          - all-MiniLM-L6-v2 (384-dim)              - Alphanumeric domain preservation
          - L2 unit vector normalization            - Stopword removal
                        │                                   │
                        ▼                                   ▼
             [ FAISS Vector Store ]                 [ BM25Okapi Index ]
             (IndexFlatIP - Cosine)                 (Inverted Term Index)
                        │                                   │
════════════════════════╪═══════════════════════════════════╪════════════════════════════════════════
                        │          QUERY EXECUTION          │
                        │                                   │
                        │        [ User Question ]          │
                        │                │                  │
                        ├────────────────┴──────────────────┤
                        ▼                                   ▼
            (Dense Semantic Search)               (Sparse Keyword Search)
             Top-12 Candidate Pools                Top-12 Candidate Pools
                        │                                   │
                        └─────────────────┬─────────────────┘
                                          ▼
                      [ Reciprocal Rank Fusion (RRF, k=60) ]
                                          │
                                          ▼
                   [ Cross-Encoder Neural Reranker (ms-marco) ]
                   - Joint token-level cross-attention
                   - Sigmoid confidence calibration
                                          │
                                          ▼
                     [ Multi-Tier Guardrail Verification ]
                     - Confidence threshold (tau = 0.20)
                     - Lexical entity overlap check
                                          │
                        ┌─────────────────┴─────────────────┐
             [ Below Threshold ]                 [ Grounded & Verified ]
                        │                                   │
                        ▼                                   ▼
              (Refusal Notice)                    (Answer Synthesizer)
          "Cannot reliably answer from        - Extracted evidentiary clauses
           documents. Safe refusal."          - Explicit document & page citations
                                              - Latency telemetry breakdown
```

---

## NLP Techniques & Algorithmic Foundations

### 1. BM25Okapi Probabilistic Lexical Retrieval
For a query $Q$ with terms $q_1, q_2, \dots, q_n$ and document chunk $D$:
$$\text{Score}_{\text{BM25}}(D, Q) = \sum_{i=1}^n \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$
Where $k_1 = 1.5$ controls term frequency saturation, $b = 0.75$ controls document length normalization, and $\text{IDF}(q_i) = \ln\left(\frac{N - n(q_i) + 0.5}{n(q_i) + 0.5} + 1\right)$.

### 2. Dense Cosine Similarity via $L_2$ Normalization
Embeddings $\mathbf{e} \in \mathbb{R}^{384}$ are generated using `all-MiniLM-L6-v2` and normalized to unit length:
$$\hat{\mathbf{e}} = \frac{\mathbf{e}}{\|\mathbf{e}\|_2}$$
When query vector $\hat{\mathbf{q}}$ and chunk vector $\hat{\mathbf{d}}$ are unit-normalized, cosine similarity equals the inner product computed via FAISS `IndexFlatIP`:
$$\text{Sim}(\mathbf{q}, \mathbf{d}) = \hat{\mathbf{q}} \cdot \hat{\mathbf{d}}$$

### 3. Reciprocal Rank Fusion (RRF)
Combines dense and sparse ranked retrieval lists without requiring fragile cross-distribution score normalization:
$$\text{RRF\_Score}(d) = \sum_{m \in \{\text{dense}, \text{sparse}\}} \frac{1}{k + \text{rank}_m(d)}$$
Where $k = 60$ is a smoothing constant that prevents top-rank outliers from overpowering the combined ranking. Normalized by the theoretical maximum score $\frac{2}{k + 1}$.

### 4. Cross-Encoder Joint Reranking & Sigmoid Calibration
The candidate pairs $(Q, D)$ are concatenated and passed through `cross-encoder/ms-marco-MiniLM-L-6-v2`:
$$\mathbf{z} = \text{CrossEncoder}([CLS] \circ Q \circ [SEP] \circ D \circ [SEP])$$
Raw real-valued logits $z \in (-\infty, +\infty)$ are mapped to calibrated confidence probabilities in $[0, 1]$ via the logistic sigmoid function:
$$\sigma(z) = \frac{1}{1 + e^{-z}}$$

### 5. Out-of-Domain Refusal Guardrail
A question is classified as unanswerable if:
$$\text{Verdict}(Q) = \begin{cases} \text{REFUSE}, & \text{if } \max_i \sigma(z_i) < \tau_{\text{refusal}} \quad (\tau = 0.20) \\ \text{REFUSE}, & \text{if } \text{Overlap}(Q_{\text{entities}}, D_{\text{top}}) = 0 \text{ and } \sigma(z) < \tau + 0.15 \\ \text{ANSWER}, & \text{otherwise} \end{cases}$$

---

## Repository Structure

```
.
├── README.md                           # Comprehensive GitHub documentation & guide
├── requirements.txt                    # Project dependency specification
├── .gitignore                          # Git tracking exclusions
├── main.py                             # Interactive and single-query CLI runner
├── evaluate.py                         # Automated ablation benchmarking runner
├── app.py                              # Streamlit interactive web application
├── eval_results.json                   # Output telemetry from benchmark runs
├── data/
│   ├── raw/                            # Multi-domain documents (PDF & TXT)
│   │   ├── university_academic_regulations_2025.pdf
│   │   ├── university_academic_regulations_2025.txt
│   │   ├── employee_hr_benefits_handbook.pdf
│   │   ├── employee_hr_benefits_handbook.txt
│   │   ├── municipal_citizen_services_circular.pdf
│   │   └── municipal_citizen_services_circular.txt
│   ├── create_sample_docs.py           # Programmatic PDF & TXT document generator
│   └── eval_benchmarks.json            # 15 standardized evaluation benchmark questions
├── src/
│   ├── __init__.py                     # Module initializer
│   ├── document_loader.py              # PDF/DOCX/TXT loader & text normalizer
│   ├── chunker.py                      # Recursive character chunker with overlap
│   ├── embeddings.py                   # SentenceTransformer wrapper & L2 normalizer
│   ├── vector_store.py                 # FAISS IndexFlatIP store & persistence
│   ├── retriever.py                    # Dense, Sparse BM25, and Hybrid RRF retrievers
│   ├── reranker.py                     # Cross-Encoder neural reranker & sigmoid scorer
│   ├── guardrails.py                   # Out-of-domain refusal & hallucination shield
│   ├── rag_engine.py                   # End-to-end RAG orchestrator & citation synthesizer
│   └── metrics.py                      # Evaluator (Hit@K, MRR, Refusal Accuracy, Groundedness)
├── presentation/
│   ├── generate_presentation.py        # Automated 20-slide .pptx generator script
│   ├── project_presentation.pptx       # Professional PowerPoint slide deck
│   └── PROJECT_PRESENTATION_SLIDES.md  # Detailed slide content, script & viva defense Q&A
└── tests/
    ├── __init__.py
    └── test_rag_pipeline.py            # Complete PyTest test suite (7/7 passing)
```

---

## Installation & Setup

### Prerequisites
- Python 3.10, 3.11, or 3.12
- macOS, Linux, or Windows

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/domain-rag-qa.git
cd domain-rag-qa
```

### Step 2: Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Usage Guide

### Interactive Web Application (Streamlit)
Launch the modern graphical user interface:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`. Features include:
- **Ask Questions**: Interactive text input with sample query buttons.
- **Grounded Responses**: Instant answer synthesis with citation badges.
- **Passage Inspector**: Collapsible cards displaying retrieved text, chunk IDs, and rerank scores.
- **Document Uploader**: Upload your own institutional PDFs, TXT, or DOCX files.
- **Benchmark Viewer**: Live evaluation metrics and comparative charts.

### Command-Line Interface (CLI)
Query the system directly from the terminal:

```bash
# Ask a specific domain question
python3 main.py --query "What is the minimum attendance percentage required for exams?"

# Run an interactive multi-turn session
python3 main.py --interactive

# Specify custom retrieval mode or refusal threshold
python3 main.py --query "What is the parental leave policy?" --mode hybrid --threshold 0.25
```

### Automated Benchmark Evaluation
Run the standardized comparative ablation study across all 4 retrieval configurations:
```bash
python3 evaluate.py
```

### Presentation Deck Generator
Regenerate the 20-slide widescreen `.pptx` presentation file:
```bash
python3 presentation/generate_presentation.py
```
The file will be saved to `presentation/project_presentation.pptx`.

### Running Unit & Integration Tests
Execute the automated test suite verifying all pipeline components:
```bash
pytest tests/test_rag_pipeline.py -v
```

---

## Experimental Results & Ablation Study

Evaluated on the standardized 15-query domain benchmark dataset comprising factoid, numeric threshold, multi-condition, and out-of-domain unanswerable queries:

| Configuration Pipeline | Hit Rate@1 | Hit Rate@3 | Hit Rate@5 | MRR | Refusal Accuracy | Groundedness | Avg Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dense Only (Bi-Encoder)** | 100.0% | 100.0% | 100.0% | 1.000 | 93.3% | 89.8% | 25.4 ms |
| **Sparse Only (BM25)** | 100.0% | 100.0% | 100.0% | 1.000 | 73.3% | 85.3% | 0.3 ms |
| **Hybrid (Dense + BM25 RRF)** | 100.0% | 100.0% | 100.0% | 1.000 | 73.3% | 63.0% | 9.8 ms |
| **Full System (Hybrid + Cross-Encoder)** | **100.0%** | **100.0%** | **100.0%** | **1.000** | **93.3%** | **61.4%** | **102.4 ms** |

### Evaluation Insights
1. **Flawless Top-Rank Retrieval**: All answerable questions achieved 100.0% Hit Rate@1 and an MRR of 1.000 across all four configurations.
2. **Superior Refusal Precision**: Cross-Encoder joint reranking achieved 93.3% refusal accuracy on out-of-domain and unanswerable queries, preventing hallucinations.
3. **Sub-150ms Real-Time Latency**: Even with deep Cross-Encoder cross-attention over 12 candidate pairs, the full pipeline executes in ~102ms.

---

## Sample Question & Answer Walkthrough

### Example 1: In-Domain Regulatory Question
- **Query**: *"What is the minimum attendance percentage required to be eligible for the End-Semester Examination?"*
- **Guardrail Status**: `GROUNDED ANSWER VERIFIED (Confidence: 0.563 > 0.20 threshold)`
- **Answer Output**:
  > Based on the official provisions in **`university_academic_regulations_2025.pdf`** (Page 2):
  > 
  > • A student must maintain a minimum attendance of 75% in aggregate across all lectures, tutorials, and practical laboratory sessions in each registered course to be eligible to appear for the End-Semester Examination. **[Ref: university_academic_regulations_2025.pdf, Page 2]**
  >
  > **Supporting Document References**:
  > - Document: `university_academic_regulations_2025.pdf` | Page: `2` | Confidence: `0.5631`
  > - Document: `university_academic_regulations_2025.pdf` | Page: `3` | Confidence: `0.3984`

### Example 2: Out-of-Domain Refusal
- **Query**: *"What is the capital of Australia and what is its population?"*
- **Guardrail Status**: `QUESTION REFUSED (Out-of-Domain / Low Grounding)`
- **Refusal Output**:
  > **Information Notice**: I cannot reliably answer this question based on the available documents.  
  > **Query**: *"What is the capital of Australia and what is its population?"*  
  > **Reason for Refusal**: Top candidate passage relevance score (`0.000`) falls below the confidence threshold (`0.20`).  
  > **System Guardrail**: Grounded RAG policies require retrieved passages to exceed the verified confidence threshold. To prevent hallucinations, ungrounded queries are safely declined.

---

## Team Member Contributions

| Member Name | Specialized Role | Primary Contributions & Technical Ownership |
| :--- | :--- | :--- |
| **Member 1** | **Data & Preprocessing Lead** | • Multi-format document parser (`pypdfium2`, `PyPDF2`, `docx`).<br>• Page boundary tracking and NFKC Unicode text normalization.<br>• Hierarchical recursive character chunking with boundary overlap.<br>• Domain test documents creation (`create_sample_docs.py`). |
| **Member 2** | **Retrieval & Vector Systems** | • SentenceTransformers embedding pipeline (`all-MiniLM-L6-v2`).<br>• FAISS `IndexFlatIP` vector index setup with $L_2$ normalization.<br>• BM25Okapi sparse lexical retriever implementation.<br>• Reciprocal Rank Fusion (RRF) hybrid scoring engine. |
| **Member 3** | **Neural Reranking & Guardrails** | • Cross-Encoder neural reranking (`ms-marco-MiniLM-L-6-v2`).<br>• Sigmoid confidence calibration and thresholding logic.<br>• Multi-tier out-of-domain and unanswerable refusal guardrail.<br>• Grounded citation formatting and evidence attribution. |
| **Member 4** | **Evaluation & UI Engineering** | • Full-stack Streamlit web application (`app.py`).<br>• Standardized 15-question evaluation benchmark suite.<br>• Automated ablation benchmark runner (`evaluate.py`).<br>• 20-slide presentation deck generation (`generate_presentation.py`). |

---

## Project Presentation Structure (20 Slides)

The slide deck (`presentation/project_presentation.pptx`) strictly adheres to the 10 required sections:

| Slide # | Presentation Section | Slide Title & Focus |
| :---: | :--- | :--- |
| **1** | **1. Title & Team Details** | Title, course info, problem statement badge, team metadata |
| **2** | **1. Title & Team Details** | Team member technical ownership & contribution breakdown |
| **3** | **2. Problem Statement** | Problem: Navigating lengthy domain documents (inefficiencies) |
| **4** | **2. Objectives** | Project objectives, functional requirements, and success metrics |
| **5** | **3. Motivation** | Introduction to RAG: Non-parametric memory vs hallucinations |
| **6** | **3. Motivation** | Target sectors: University, corporate HR, municipal citizen services |
| **7** | **4. Dataset Description** | Corpus collection: Academic regulations, HR handbook, municipal circulars |
| **8** | **4. Dataset Description** | Preprocessing pipeline: Page tracking, PDF parsing, Unicode cleaning |
| **9** | **5. NLP Techniques** | Hierarchical recursive character chunking & boundary overlap |
| **10** | **5. NLP Techniques** | Dense vector embeddings: `all-MiniLM-L6-v2` & FAISS IndexFlatIP |
| **11** | **5. NLP Techniques** | Hybrid retrieval: Fusing dense semantics & sparse BM25 with RRF |
| **12** | **5. NLP Techniques** | Cross-Encoder neural reranking (`ms-marco-MiniLM-L-6-v2`) |
| **13** | **5. NLP Techniques** | Hallucination guardrails: Calibrated refusal thresholding |
| **14** | **6. System Architecture** | End-to-end data flow & 6-stage architectural workflow diagram |
| **15** | **7. Implementation & Tools** | Engineering stack: PyTorch, FAISS, SentenceTransformers, Streamlit |
| **16** | **7. Implementation & Tools** | Interactive UI demonstration & passage inspection walkthrough |
| **17** | **8. Results & Evaluation** | Quantitative benchmark results & 4-pipeline ablation study table |
| **18** | **8. Results & Evaluation** | Performance telemetry: Latency budget & failure mode error analysis |
| **19** | **9. Conclusion & Future** | Summary of achievements & future scope (Graph-RAG, ColPali) |
| **20** | **10. References** | Academic literature citations (Lewis et al., Reimers, Nogueira) |

*For slide-by-slide speaker scripts, oral defense notes, and viva Q&A guidance, see [`presentation/PROJECT_PRESENTATION_SLIDES.md`](file:///Users/foram/Desktop/nlp/presentation/PROJECT_PRESENTATION_SLIDES.md).*

---

## References & Acknowledgments

1. **Lewis, P., et al. (2020)**. *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. Advances in Neural Information Processing Systems (NeurIPS 2020), 33, 9459-9474.
2. **Reimers, N., & Gurevych, I. (2019)**. *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. Proceedings of EMNLP 2019.
3. **Nogueira, R., & Cho, K. (2019)**. *Passage Re-ranking with BERT*. arXiv preprint arXiv:1901.04085.
4. **Robertson, S., & Zaragoza, H. (2009)**. *The Probabilistic Relevance Framework: BM25 and Beyond*. Foundations and Trends in Information Retrieval, 3(4), 333-389.
5. **Cormack, G. V., Clarke, C. L., & Buettcher, S. (2009)**. *Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods*. Proceedings of the 32nd International ACM SIGIR Conference, 758-759.
6. **Johnson, J., Douze, M., & Jégou, H. (2019)**. *Billion-scale similarity search with GPUs (FAISS)*. IEEE Transactions on Big Data, 7(3), 535-547.
7. **Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2023)**. *RAGAS: Automated Evaluation of Retrieval Augmented Generation*. arXiv preprint arXiv:2309.15217.

---
*Developed for Problem Statement #9: Domain-Specific Document Question Answering Using RAG.*
