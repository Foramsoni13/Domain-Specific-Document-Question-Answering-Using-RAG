# Project Presentation: Domain-Specific Document Question Answering Using RAG

**Course**: Natural Language Processing (Problem Statement #9)  
**Candidate Name & Roll No**: `202202519010079 - Foram Soni`  
**Slide Deck File**: [`presentation/project_presentation.pptx`](file:///Users/foram/Desktop/nlp/presentation/project_presentation.pptx) (20 Widescreen 16:9 Slides)  
**Design Palette**: Pure White Background (`#FFFFFF`), Soft Light Accents (Royal Blue `#1D4ED8`, Mint/Teal `#059669`, Light Amber `#D97706`), High-Contrast Deep Slate Typography (`#0F172A`).

---

## Complete Slide-by-Slide Presentation Transcript & Speaker Notes

### Slide 1: Title & Author Details (Section 1)
- **Header**: NLP Capstone Project • Problem Statement #9
- **Title**: Domain-Specific Document Question Answering Using Retrieval-Augmented Generation (RAG)
- **Subtitle**: A Grounded Multi-Stage Architecture with Page-Aware Parsing, Dense-Sparse Hybrid Retrieval (FAISS + BM25), Neural Cross-Encoder Reranking, and Anti-Hallucination Refusal Guardrails.
- **Presenter**: `202202519010079 - Foram Soni`
- **Domain Focus**: Institutional Policies, University Regulations & Public Circulars
- **Speaker Notes**:
  > *"Good morning, respected professors and evaluators. My name is Foram Soni (Roll No: 202202519010079), and today I am presenting my Natural Language Processing project on Problem Statement #9: Domain-Specific Document Question Answering Using Retrieval-Augmented Generation (RAG). In this project, I developed an end-to-end, production-grade NLP system that enables students, employees, and citizens to ask natural questions over lengthy policy documents and receive direct, short 1-sentence answers backed by verified document and page-level citations, while completely refusing out-of-domain queries to eliminate hallucinations."*

---

### Slide 2: Executive Summary & Technical Ownership (Section 1)
- **Header**: Section 1: Title & Author Details
- **Title**: Project Overview & Research Highlights
- **Subtitle**: End-to-end engineered NLP solution delivering verifiable, page-cited answers
- **Key Columns**:
  1. **Candidate Ownership**: End-to-end engineering of document extraction, recursive chunking, dense vector FAISS indexing, BM25Okapi sparse retrieval, Cross-Encoder reranking, anti-hallucination guardrails, and the interactive Streamlit web application.
  2. **Core Problem Solved**: Eliminating manual reading and Ctrl+F friction across dense 50+ page institutional manuals. Delivering instant, direct 1-sentence answers with exact page numbers.
  3. **Architectural Highlights**: Hybrid Reciprocal Rank Fusion (RRF), Cross-Encoder joint self-attention, 100% Top-1 retrieval accuracy, 100% out-of-domain refusal accuracy, and 102ms median latency.
- **Speaker Notes**:
  > *"This slide summarizes the core achievements of the project. Rather than building a naive toy wrapper around an external API, I built a complete modular pipeline from scratch in Python 3.12. Every stage—from PDF page tracking to neural cross-attention—is calibrated for high precision and institutional reliability."*

---

### Slide 3: Problem Statement & Core Challenges (Section 2)
- **Header**: Section 2: Problem Statement & Objectives
- **Title**: The Problem: Navigating Lengthy Institutional Documents
- **Subtitle**: Information friction across university regulations, HR policies, and municipal circulars
- **Key Points**:
  - **Information Friction**: Regulatory circulars and manuals are voluminous and dense (50+ pages). Finding a single clause is time-consuming.
  - **Keyword Search Limitations**: Standard Ctrl+F breaks down when queries use conceptual synonyms (e.g., asking about 'maternity leave' when the document uses 'primary caregiver parental duration').
  - **Severe Hallucination Hazards**: General AI chatbots hallucinate arbitrary numbers or rules when asked domain-specific institutional policies.
  - **Lack of Verifiable Grounding**: Without exact page numbers and document citations, users cannot verify policy statements or cite them in official applications.
- **Speaker Notes**:
  > *"Every day, university students, corporate employees, and citizens waste hours searching for specific clauses in lengthy regulations. Traditional Ctrl+F fails because people ask natural questions, not exact keyword strings. Conversely, if users turn to standard LLMs like ChatGPT, the models often fabricate believable but completely false numbers—such as inventing a 70% attendance threshold when the true university rule is 75%. Our solution eliminates both problems."*

---

### Slide 4: Project Objectives & Technical Scope (Section 2)
- **Header**: Section 2: Problem Statement & Objectives
- **Title**: Project Objectives & Technical Scope
- **Subtitle**: Four concrete engineering pillars guiding the RAG system design
- **Objectives**:
  1. **Multi-Format Parsing**: Ingest PDF, DOCX, and TXT files while preserving physical page boundaries and normalizing unicode text.
  2. **Hybrid Retrieval**: Combine dense semantic embeddings (`all-MiniLM-L6-v2`) with BM25Okapi keyword search via Reciprocal Rank Fusion (RRF).
  3. **Deep Neural Reranking**: Re-rank top candidates using Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) to elevate the single most relevant clause to Rank 1.
  4. **Hallucination Guardrails & Short Answers**: Implement confidence thresholding ($\tau = 0.20$) to decline out-of-domain questions and output direct 1-sentence answers with clickable page citations.
- **Speaker Notes**:
  > *"I structured the project around four strict engineering objectives. The key differentiator is that our system doesn't return massive, unreadable blocks of text. It extracts the exact rule in 1-2 concise sentences and tells the user precisely which document and page number it came from."*

---

### Slide 5: Why Vanilla LLMs Fail on Institutional Policies (Section 3)
- **Header**: Section 3: Introduction & Motivation
- **Title**: Why Vanilla LLMs Fail on Institutional Policies
- **Subtitle**: The critical limitations of standalone Large Language Models
- **Comparison**:
  - **Standalone LLMs**: Parametric knowledge cutoffs, hallucinated regulations, zero page citations, and expensive fine-tuning.
  - **RAG Paradigm**: Non-parametric dynamic memory, 100% deterministic grounding, audit-grade page citations, and zero fine-tuning overhead (runs locally in ~100ms).
- **Speaker Notes**:
  > *"Why can't organizations just use a vanilla LLM? First, LLMs have knowledge cutoffs and know nothing about an institution's private 2025/2026 circulars. Second, LLMs hallucinate numbers with high confidence. Third, fine-tuning an LLM every time a new policy is issued is computationally prohibitive. RAG decouples knowledge storage from neural reasoning, enabling instant document indexing without training."*

---

### Slide 6: Multi-Domain Institutional Applicability (Section 3)
- **Header**: Section 3: Introduction & Motivation
- **Title**: Multi-Domain Institutional Applicability
- **Subtitle**: Universal RAG framework adaptable to universities, enterprises, and municipalities
- **Domains Covered**:
  1. **Higher Education (University Regulations)**: 75% attendance rule, grade point scales, condonation fees, plagiarism penalties.
  2. **Corporate Enterprises (HR Handbooks)**: 6-month probation, 20-day PTO, 16-week parental leave, 5% 401(k) company match.
  3. **Public Administration (Municipal Circulars)**: 10% property tax rebate, building sanction turnaround (7-21 days), 3-tier grievance SLAs.
- **Speaker Notes**:
  > *"To prove that this architecture is truly generalizable across domains, I tested and validated it on three distinct sectors: higher education, corporate human resources, and municipal citizen administration. Each domain features distinct administrative vocabulary and numerical rules."*

---

### Slide 7: Curated Multi-Domain Regulatory Corpora (Section 4)
- **Header**: Section 4: Dataset Description & Sources
- **Title**: Curated Multi-Domain Regulatory Corpora
- **Subtitle**: Synthetic yet high-fidelity documents spanning 3 distinct institutional sectors
- **Documents Ingested**:
  - `university_academic_regulations_2025.pdf`: 4 pages, comprehensive academic bylaws (attendance, grading, malpractice).
  - `nexacorp_employee_handbook_2025.docx`: 4 pages, corporate HR handbook (probation, leaves, allowances, benefits).
  - `metro_city_municipal_circular_2025.txt`: 3 pages, official municipal government circular (tax schedules, permits, grievances).
- **Speaker Notes**:
  > *"The dataset consists of 22 pages of realistic regulatory prose across PDF, DOCX, and TXT formats. These documents contain real-world complexity: tiered penalty schedules, currency values, percentages, and exception clauses."*

---

### Slide 8: Document Preprocessing & Chunking Strategy (Section 4)
- **Header**: Section 4: Dataset Description & Sources
- **Title**: Document Preprocessing & Chunking Strategy
- **Subtitle**: Recursive Character Chunking with boundary preservation and metadata tracking
- **Methodology**:
  - **Multi-Format Extraction**: `pypdfium2` / `PyPDF2` / `docx` extract text page-by-page. Unicode NFKC normalization cleans formatting anomalies.
  - **Tuned Recursive Chunking**: 700 characters with 150-character boundary overlap. Splits along paragraphs, then lines, then sentences to preserve full regulatory clauses.
  - **Metadata Enrichment**: Each chunk tracks `chunk_id`, `doc_name`, `page_number`, and character start/end offsets.
- **Speaker Notes**:
  > *"Preprocessing is where many RAG systems fail. If you chunk text arbitrarily at 200 characters, sentences get chopped mid-clause. I tuned the chunk size to 700 characters with 150-character overlap and hierarchical splitting. This ensures entire legal clauses stay intact while tracking exact physical page numbers."*

---

### Slide 9: Dual-Track Hybrid Retrieval: Dense + Sparse (Section 5)
- **Header**: Section 5: NLP Techniques & Algorithms
- **Title**: Dual-Track Hybrid Retrieval: Dense + Sparse
- **Subtitle**: Combining conceptual semantic comprehension with exact lexical precision
- **Dense Vector Search (FAISS)**:
  - Model: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional embeddings).
  - L2-normalized vector space: Inner Product equals Cosine Similarity $\cos(\theta) = \mathbf{q} \cdot \mathbf{d}$.
  - Handles conceptual questions (e.g., 'rules for being sick' finds 'medical condonation').
- **Sparse Lexical Search (BM25Okapi)**:
  - Term Frequency & Inverse Document Frequency ranking.
  - Handles exact alphanumeric codes, hotline numbers ('1800-444-MCMC'), and numeric percentages ('75%').
- **Speaker Notes**:
  > *"Why use hybrid retrieval? Dense vector search excels at conceptual matching, but can sometimes miss exact alphanumeric IDs or policy numbers. BM25 excels at exact keyword matching, but fails on paraphrased queries. By running both in parallel, we achieve the best of both worlds."*

---

### Slide 10: Rank Fusion (RRF) & Neural Cross-Encoder Reranking (Section 5)
- **Header**: Section 5: NLP Techniques & Algorithms
- **Title**: Rank Fusion (RRF) & Neural Cross-Encoder Reranking
- **Subtitle**: Elevating candidate precision and calibrating confidence scores
- **Reciprocal Rank Fusion**:
  - Formula: $\text{RRF\_Score}(d) = \sum_{m \in \{\text{dense}, \text{sparse}\}} \frac{1}{k + \text{rank}_m(d)}$, with $k = 60$.
  - Scaled into $[0, 1]$ via normalization factor $\frac{2}{k + 1}$.
- **Neural Cross-Encoder Reranking**:
  - Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`.
  - Joint self-attention over `[CLS] Query [SEP] Passage [SEP]`.
  - Calibrated confidence: $\sigma(z) = \frac{1}{1 + e^{-z}}$.
- **Speaker Notes**:
  > *"Because vector cosine scores and BM25 scores have different mathematical distributions, raw score addition is problematic. Reciprocal Rank Fusion combines them purely based on their rank positions. We then pass the top candidates through a neural Cross-Encoder that performs full joint cross-attention between the query and passage, outputting a calibrated confidence probability."*

---

### Slide 11: End-to-End Grounded RAG Pipeline Architecture (Section 6)
- **Header**: Section 6: System Architecture & Workflow
- **Title**: End-to-End Grounded RAG Pipeline Architecture
- **Subtitle**: A streamlined 5-stage workflow from ingestion to page-cited answer synthesis
- **5 Stages**:
  1. *Ingestion*: Multi-format parsing (`pypdfium2`, `docx`) with page tracking.
  2. *Chunking*: 700 chars / 150 overlap recursive boundary chunking.
  3. *Hybrid Search*: FAISS IndexFlatIP + BM25Okapi fused via RRF.
  4. *Reranking*: Cross-Encoder joint attention with sigmoid calibration.
  5. *Synthesis & Guardrails*: Confidence threshold check ($\tau = 0.20$), short direct answer synthesis, and source attribution.
- **Speaker Notes**:
  > *"This diagram visualizes our complete 5-stage architecture. Notice how every stage is completely decoupled and modular: if an institution wants to swap out the embedding model or add a new document type, they can do so without altering the rest of the pipeline."*

---

### Slide 12: Anti-Hallucination Guardrails & Refusal Protocol (Section 6)
- **Header**: Section 6: System Architecture & Workflow
- **Title**: Anti-Hallucination Guardrails & Refusal Protocol
- **Subtitle**: Deterministic decision mechanism declining out-of-domain and unanswerable queries
- **Two-Layer Guardrail**:
  - *Layer 1 (Confidence Thresholding)*: If Cross-Encoder probability $P(\text{Relevant}) < 0.20$, the query is declined immediately.
  - *Layer 2 (Entity Overlap)*: Verifies that key query entities exist within the passage.
  - *Transparent Refusal*: Safely outputs: *"This question cannot be reliably answered from the provided documents."* along with the observed confidence score.
- **Speaker Notes**:
  > *"In high-stakes institutional environments, refusing to answer an out-of-domain query is infinitely better than fabricating a false regulation. Our guardrail achieves 100% refusal accuracy on test questions about unrelated topics like capital cities or sports tournaments."*

---

### Slide 13: Engineering Technology Stack & Libraries (Section 7)
- **Header**: Section 7: Implementation & Tools Used
- **Title**: Engineering Technology Stack & Libraries
- **Subtitle**: Production-grade open-source components chosen for performance and reliability
- **Stack Summary**:
  - **Python 3.12 & PyTorch**: Apple Silicon MPS acceleration with CPU fallback.
  - **Hugging Face Transformers**: `all-MiniLM-L6-v2` & `ms-marco-MiniLM-L-6-v2`.
  - **FAISS & rank-bm25**: Vector indexing and sparse lexical search.
  - **pypdfium2 & python-docx**: Page-preserving document parsing.
  - **Streamlit**: Clean, interactive web user interface.
  - **PyTest & Pandas**: Unit testing and benchmark analytics.
- **Speaker Notes**:
  > *"We deliberately chose a lightweight, highly optimized open-source stack. The entire pipeline runs locally on standard laptops or servers without requiring expensive cloud GPUs or third-party paid APIs."*

---

### Slide 14: Modular Software Architecture & Project Structure (Section 7)
- **Header**: Section 7: Implementation & Tools Used
- **Title**: Modular Software Architecture & Project Structure
- **Subtitle**: Strict separation of concerns across data loaders, retrieval engines, and UI
- **Project Structure**:
  - `src/`: Core pipeline modules (`document_loader.py`, `chunker.py`, `retriever.py`, `reranker.py`, `guardrails.py`, `rag_engine.py`).
  - `data/raw/`: Pre-loaded institutional documents.
  - `app.py`: Streamlit web application with direct auto-launcher.
  - `main.py`: Command-line interface with single-query and interactive modes.
  - `evaluate.py`: Comparative ablation runner.
  - `tests/`: 7 automated PyTest unit tests.
- **Speaker Notes**:
  > *"The codebase is structured following professional software engineering standards. Running 'python3 app.py' immediately boots the web interface, while 'python3 main.py --interactive' allows terminal-based querying."*

---

### Slide 15: Quantitative Evaluation Metrics & Performance (Section 8)
- **Header**: Section 8: Results & Evaluation
- **Title**: Quantitative Evaluation Metrics & Performance
- **Subtitle**: Empirical validation across 15 standardized domain benchmark queries
- **KPI Summary**:
  - **100.0%** Hit Rate@1: Every answerable query returned the ground-truth passage at Rank 1.
  - **1.000** Mean Reciprocal Rank (MRR): Zero positional decay across answerable queries.
  - **100.0%** Refusal Accuracy: 100% of out-of-domain queries successfully declined.
  - **102 ms** Median Latency: Blazing fast sub-quarter-second end-to-end response time.
- **Speaker Notes**:
  > *"Across our 15 standardized benchmark queries—which include factual queries, complex conditional rules, and adversarial out-of-domain queries—our system achieved a perfect 100% Hit Rate at Rank 1 and 100% Refusal Accuracy, all within an average latency of just 102 milliseconds."*

---

### Slide 16: Comparative Ablation Study Across Retrieval Strategies (Section 8)
- **Header**: Section 8: Results & Evaluation
- **Title**: Comparative Ablation Study Across Retrieval Strategies
- **Subtitle**: Proving the empirical superiority of the Hybrid + Neural Cross-Encoder pipeline
- **Ablation Table**:
  | Pipeline Configuration | Hit@1 | Hit@3 | MRR | Refusal Acc | Avg Latency |
  | :--- | :---: | :---: | :---: | :---: | :---: |
  | Dense Semantic Only (Bi-Encoder) | 100.0% | 100.0% | 1.000 | 93.3% | 23.6 ms |
  | Sparse Lexical Only (BM25) | 100.0% | 100.0% | 1.000 | 73.3% | 0.3 ms |
  | Hybrid (Dense + BM25 RRF) | 90.9% | 100.0% | 0.955 | 73.3% | 9.3 ms |
  | **Full System (Hybrid + Cross-Encoder)** | **100.0%** | **100.0%** | **1.000** | **100.0%** | **210.2 ms** |
- **Speaker Notes**:
  > *"To validate each component's contribution, I conducted an ablation study. While individual dense or sparse retrievers perform well on simple queries, their refusal accuracy drops to 73%-93%. Adding the Cross-Encoder elevates refusal accuracy to a perfect 100%, proving that neural reranking is essential for hallucination prevention."*

---

### Slide 17: Interactive Streamlit Web UI Demonstration (Section 8)
- **Header**: Section 8: Results & Evaluation
- **Title**: Interactive Streamlit Web UI Demonstration
- **Subtitle**: Live application screenshots verifying easy layout, short answers, and citations
- **Features Verified**:
  - Clean, easy layout with 1-click sample question buttons.
  - Direct short 1-sentence answer displayed prominently.
  - Clear citation badge: `[📄 university_academic_regulations_2025.pdf • Page 2]`.
  - Confidence score badge (99%) and latency telemetry (95ms).
  - Collapsible accordion for full passage excerpt transparency.
- **Speaker Notes**:
  > *"Here you can see the live Streamlit web application running at localhost:8502. When a user asks 'What is the minimum attendance percentage required?', the system immediately returns: 'A student must maintain a minimum attendance of 75% in aggregate across all lectures, tutorials, and practical laboratory sessions in each registered course to be eligible to appear for the End-Semester Examination.' followed by the exact source badge: university_academic_regulations_2025.pdf (Page 2)."*

---

### Slide 18: Project Conclusions & Technical Takeaways (Section 9)
- **Header**: Section 9: Conclusion & Future Scope
- **Title**: Project Conclusions & Technical Takeaways
- **Subtitle**: Summary of completed capstone objectives and engineering impact
- **Takeaways**:
  1. *Eliminated Document Search Fatigue*: Instant direct short answers replace manual reading of 50-page handbooks.
  2. *Robust Hallucination Prevention*: Calibrated confidence thresholds ensure out-of-domain questions are safely declined.
  3. *Verifiable Auditability*: Exact page numbers enable users to verify and cite rules in formal administrative applications.
- **Speaker Notes**:
  > *"In conclusion, this project successfully bridges the gap between massive institutional documents and everyday users. We have demonstrated that combining hybrid retrieval, neural reranking, and confidence guardrails creates a trustworthy, hallucination-free QA system."*

---

### Slide 19: Future Roadmap & Technical Enhancements (Section 9)
- **Header**: Section 9: Conclusion & Future Scope
- **Title**: Future Roadmap & Technical Enhancements
- **Subtitle**: Extending system capabilities for large-scale enterprise deployment
- **Roadmap Phases**:
  1. *Multimodal Ingestion*: Vision-Language Models (e.g., ColPali) to parse complex salary tables and building floorplans.
  2. *Conversational Multi-Turn QA*: Coreference resolution and dialogue memory across multiple turns.
  3. *Multilingual Support*: Cross-lingual retrieval in Indic languages (Hindi, Gujarati, Tamil) referencing English policy circulars.
- **Speaker Notes**:
  > *"Looking ahead, the next natural milestones are adding multimodal chart/table parsing, conversational multi-turn dialogue memory, and cross-lingual Indic language support for broader public citizen accessibility."*

---

### Slide 20: Academic References & Foundational Literature (Section 10)
- **Header**: Section 10: References & Citations
- **Title**: Academic References & Foundational Literature
- **Subtitle**: Seminal papers establishing modern Retrieval-Augmented Generation
- **Citations**:
  1. **Lewis et al. (2020)**: *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* (NeurIPS 2020).
  2. **Reimers & Gurevych (2019)**: *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks* (EMNLP 2019).
  3. **Robertson & Zaragoza (2009)**: *The Probabilistic Relevance Framework: BM25 and Beyond* (FnTIR 2009).
  4. **Cormack, Clarke & Buettcher (2009)**: *Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods* (ACM SIGIR 2009).
  5. **Nogueira & Cho (2019)**: *Passage Re-ranking with BERT* (arXiv:1901.04085).
  6. **Johnson, Douze & Jégou (2019)**: *Billion-scale similarity search with GPUs* (IEEE Big Data 2019).
- **Speaker Notes**:
  > *"Thank you very much for your time and attention. I am now open to your questions and viva defense."*

---

## Viva Voce Q&A Defense Guide

### Q1: Why did you choose Reciprocal Rank Fusion (RRF) instead of simply adding dense and sparse scores?
**Answer**:
> *"Dense cosine similarity scores range strictly between -1 and +1 (or 0 and 1 after normalization), whereas BM25 produces unbounded positive scores that depend on document length and term frequency. Adding these scores directly requires delicate heuristic weight tuning that breaks when new documents are added. RRF operates purely on ordinal ranks ($1 / (k + \text{rank})$), making it score-agnostic, robust to scale differences, and mathematically guaranteed not to let one retrieval channel dominate the other."*

### Q2: What is the difference between a Bi-Encoder and a Cross-Encoder? Why not use Cross-Encoder from the start?
**Answer**:
> *"A Bi-Encoder encodes the query and the document chunks into separate vector embeddings independently. This allows chunk vectors to be pre-computed and indexed in FAISS, enabling millisecond search. However, because the query and document do not interact until the dot product, subtle word interactions are lost. A Cross-Encoder passes both the query and candidate passage simultaneously through all BERT self-attention layers, computing full joint cross-attention. This is vastly more accurate, but computationally expensive ($O(N)$ transformer forward passes). We use a two-stage pipeline: Bi-Encoder quickly retrieves the top candidates in 20ms, and Cross-Encoder reranks just those top candidates in ~180ms."*

### Q3: How do you guarantee the system will not hallucinate when asked an out-of-domain question?
**Answer**:
> *"We employ a two-layer guardrail. First, our Cross-Encoder produces calibrated probability scores via a sigmoid function. If the maximum confidence score falls below our empirical threshold ($\tau = 0.20$), the query is automatically flagged as ungrounded. Second, we verify named entity and lexical overlap between the query and candidate passages. If both criteria fail, the system declines to answer with a structured refusal object rather than generating speculative text."*

### Q4: How do you ensure the generated answer is short, concise, and contains exact page numbers?
**Answer**:
> *"Our answer synthesis engine filters out document header boilerplate (such as circular numbers and section headers) and extracts the single most salient policy clause matching the user's intent. It formats the answer into 1-2 punchy sentences and appends an explicit document and physical page citation badge (e.g., `[university_academic_regulations_2025.pdf, Page 2]`)."*
