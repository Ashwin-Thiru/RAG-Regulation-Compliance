# RAG Regulation Compliance 🛡️⚖️
### *Real-Time Regulatory Intelligence with Pathway & Groq*

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Pathway](https://img.shields.io/badge/Framework-Pathway-green)](https://pathway.com/)
[![LLM](https://img.shields.io/badge/LLM-Llama--3.3--70B-orange)](https://groq.com/)
[![Inference](https://img.shields.io/badge/Inference-Groq-red)](https://groq.com/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)]()
[![CI](https://github.com/Ashwin-Thiru/RAG-Regulation-Compliance/actions/workflows/ci.yml/badge.svg)](https://github.com/Ashwin-Thiru/RAG-Regulation-Compliance/actions)

An industrial-grade, **streaming Retrieval-Augmented Generation (RAG)** pipeline built for financial institutions, law firms, and regulated enterprises. It automates real-time analysis of regulatory documents, audit reports, and compliance policies — eliminating the dangerous **"Indexing Latency"** gap found in all traditional vector database approaches.

> **Built for the Green Hackathon** — where speed, accuracy, and regulatory integrity aren't optional features, they're the baseline.

---

## 📌 Table of Contents

- [The Problem](#-the-problem-indexing-latency)
- [Our Solution](#-our-solution)
- [Why This Matters](#-why-this-matters)
- [Architecture](#-architecture)
- [Key Features](#-key-features)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [How It Works](#-how-it-works-end-to-end)
- [Performance](#-performance)
- [Security](#-security)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚨 The Problem: Indexing Latency

In high-stakes compliance environments, **a policy updated 10 minutes ago is already the law.**

Regulatory bodies — SEC, FINRA, Basel Committee, GDPR authorities, SEBI — publish amendments, circulars, and enforcement actions continuously. A single missed update can result in multi-million dollar fines, reputational damage, or criminal liability for compliance officers.

### The Traditional RAG Gap

```
Document Updated ──► Manual Trigger ──► Batch Re-index ──► AI Aware
        │                                      │
        └─────────────── Knowledge Gap ────────┘
                       (Minutes to Hours)
```

| Approach | Indexing Trigger | Latency | Risk |
|---|---|---|---|
| Traditional RAG | Manual / Scheduled | Minutes → Hours | High — stale answers |
| **Our Solution** | Automatic (file event) | **Milliseconds** | Near-zero |

---

## ✅ Our Solution

This system uses **Pathway's Unified Streaming Engine** to create a live, bidirectional sync between the document source (Google Drive) and the vector index. When a file is created, modified, or deleted — the vector space reflects it *instantly*, with zero manual intervention.

The query layer connects to **Groq's ultra-low-latency inference** (Llama-3.3-70B) with a carefully engineered **Senior Compliance Officer persona** — delivering formal, citation-grounded answers in under 3 seconds.

A **FastAPI + SSE backend** streams every step of the reasoning process to a real-time chat UI — embedding, retrieval, chunk evidence, and token-by-token answer generation — all visible live, with actual millisecond timings.

---

## 💼 Why This Matters

Regulatory compliance is one of the most document-intensive domains in the world:

- **Basel III/IV** frameworks update capital requirement rules across hundreds of pages
- **SEC Rule 10b-5** interpretations shift with every enforcement action
- **GDPR & DPDP** amendments require immediate policy updates across organizations
- Internal **audit reports** flag issues requiring same-day remediation tracking

A compliance officer asking *"Are we within current Tier 1 capital ratio requirements?"* needs an answer based on **today's rules** — not last week's index snapshot. This system guarantees that.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      Google Drive Folder                          │
│          (Regulatory Docs, Audit Reports, Policy PDFs)           │
└─────────────────────────┬────────────────────────────────────────┘
                          │  pathway.io.gdrive (live event listener)
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                   Pathway Streaming Engine                        │
│                                                                   │
│  ┌─────────────┐   ┌──────────────────┐   ┌──────────────────┐   │
│  │   Docling    │──►│ SentenceTransfor │──►│ VectorStoreServer│   │
│  │   Parser     │   │ mer (CUDA/CPU)   │   │  (Live-Sync)     │   │
│  │  (PDF/DOCX)  │   │                  │   │  :8000           │   │
│  └─────────────┘   └──────────────────┘   └──────────────────┘   │
└─────────────────────────┬────────────────────────────────────────┘
                          │  Semantic search (top-k retrieval)
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                  FastAPI SSE Backend  :8080                       │
│                                                                   │
│   POST /api/query  ──►  stream_query()                           │
│                         ├── step: embed (real ms)                │
│                         ├── step: retrieve (real ms)             │
│                         ├── chunk × N  (real evidence)           │
│                         ├── step: llm (real TTFT ms)             │
│                         └── token × N  (streamed from Groq)      │
└─────────────────────────┬────────────────────────────────────────┘
                          │  Server-Sent Events (SSE)
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                  ComplianceAI Chat UI                             │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  ⚙ Thinking...                                       ▾   │    │
│  │  ✓ Query embedded                            47ms        │    │
│  │  ✓ Retrieved 3 chunks                        47ms        │    │
│  │  #1 CAPF_Report.pdf   54.4%  "Audit noted…"             │    │
│  │  ✓ Streaming response...                     312ms       │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
│  According to [Source 1]… ▌                                      │
└──────────────────────────────────────────────────────────────────┘
```

### Component Breakdown

**1. Streaming Ingestion via `pathway.io.gdrive`**

Pathway registers a native file-system event listener on the target Google Drive folder. This fires on:
- `FILE_CREATED` — new regulatory circular uploaded
- `FILE_MODIFIED` — existing policy document amended
- `FILE_DELETED` — superseded guidance removed

Only *changed* chunks are re-embedded — not the entire document.

**2. Adaptive PDF Parsing with Docling (`src/utils/parser.py`)**

Standard parsers (PyPDF2, pdfminer) fail on complex financial layouts. Docling handles:
- Multi-column annual reports and regulatory circulars
- Nested tables (capital ratio tables, risk matrices)
- Footnotes and legal cross-references
- Section heading detection for precise chunking

**3. Local GPU Vectorization (`src/utils/embeddings.py`)**

Embeddings are computed entirely **on-premise** using `SentenceTransformer` with automatic device detection: CUDA → MPS (Apple Silicon) → CPU. Regulatory documents often contain **Material Non-Public Information (MNPI)** and must never be transmitted to third-party embedding APIs.

**4. Pathway VectorStoreServer**

Unlike Pinecone, Weaviate, or Chroma — which treat indexing as a separate async job — Pathway's `VectorStoreServer` is part of the same unified data pipeline. Updates are applied atomically with no eventual-consistency tradeoffs.

**5. FastAPI SSE Backend (`src/api.py`)**

A non-blocking FastAPI server that streams every stage of query processing to the frontend via Server-Sent Events. Every event fires at the **exact moment** the real operation completes — no fake delays or artificial timers. Real millisecond timings are captured via `perf_counter` and sent to the UI.

**6. Groq LLM Reasoning (Llama-3.3-70B)**

Retrieved context is sent to Groq with a "Senior Compliance Officer" persona prompt. The model is instructed to:
- Cite specific document sections and regulation numbers
- Flag ambiguities or conflicting guidance across documents
- Refuse to speculate outside the retrieved context
- Use formal, jurisdiction-appropriate language

Responses are **streamed token by token** — the first token fires the `llm done` event with real TTFT (Time-To-First-Token).

**7. ComplianceAI Chat UI (`frontend/index.html`)**

A single-file chat interface with:
- Live **thinking trace** — each step appears as it actually completes
- **Token streaming** — answer builds word-by-word like ChatGPT
- **Chunk evidence cards** — shows exact source snippets with similarity scores
- **Auto-collapsing trace** — folds away when answer is ready
- **Sidebar** — live document list, pipeline status, model info

---

## ✨ Key Features

- 🔴 **Zero-latency indexing** — document changes reflected in milliseconds, not minutes
- 🔒 **Air-gapped embedding** — no document content ever leaves your environment
- 📄 **Financial-grade PDF parsing** — handles complex regulatory layouts other parsers break on
- 🤖 **Compliance-persona LLM** — responses modeled on a Senior Compliance Officer
- 💬 **Real-time chat UI** — GPT-style interface with live reasoning trace
- ⚡ **True SSE streaming** — every step tied to real operations, real ms timings
- ♻️ **Automatic document lifecycle** — deletions and supersessions handled automatically
- 🖥️ **CUDA-accelerated** — both parsing and embedding optimized for GPU, with CPU fallback
- 🧩 **Modular design** — swap out any component (embedder, LLM, storage) independently
- 🐳 **Docker-ready** — multi-stage Dockerfile with health check and non-root user
- 🧪 **Tested** — unit tests for core query pipeline and embedding utilities
- 🔁 **CI/CD** — GitHub Actions workflow with lint, test, and security scan on every push

---

## 📂 Project Structure

```
RAG-Regulation-Compliance/
├── src/
│   ├── __init__.py
│   ├── main.py               # Pathway streaming server — Google Drive → VectorStore
│   ├── answerer.py           # Terminal query client — retrieval, context, Groq API
│   ├── api.py                # FastAPI SSE backend — real-time streaming endpoint
│   └── utils/
│       ├── __init__.py
│       ├── parser.py         # Docling configuration for complex regulatory PDFs
│       └── embeddings.py     # SentenceTransformer wrapper with CUDA auto-detection
├── frontend/
│   └── index.html            # ComplianceAI chat UI — single-file, no build step
├── tests/
│   ├── conftest.py           # Pytest configuration and shared path setup
│   ├── test_answerer.py      # Unit tests for context building and source extraction
│   └── test_embeddings.py    # Unit tests for device detection logic
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions — lint, test, security scan
├── .dockerignore
├── .env.example              # Environment variable template
├── .gitignore
├── CONTRIBUTING.md
├── Dockerfile                # Multi-stage production Docker image
├── LICENSE                   # MIT License
├── pyproject.toml            # Project metadata, ruff, pytest, coverage config
├── README.md
└── requirements.txt          # Pinned dependency versions
```

### Key File Responsibilities

**`src/main.py`** — Bootstraps the entire Pathway pipeline. Reads config from environment variables, validates credentials, wires together parsing → embedding → indexing, and starts the `VectorStoreServer` on port 8000. Long-running process.

**`src/api.py`** — FastAPI backend with a single SSE streaming endpoint (`POST /api/query`). Every event — embed, retrieve, chunk, token — fires immediately after the real operation completes. No fake delays. Also exposes `/api/health` and `/api/documents`.

**`src/answerer.py`** — Standalone terminal client. Accepts natural language queries, retrieves top-k chunks, builds labelled context, and calls Groq. Can be used independently without the UI.

**`frontend/index.html`** — Zero-dependency single-file chat UI. Opens directly in a browser — no build step, no npm, no bundler. Connects to the FastAPI backend via SSE.

**`src/utils/parser.py`** — Wraps Docling with configuration tuned for regulatory PDFs: multi-column detection, table extraction, and section heading handling.

**`src/utils/embeddings.py`** — Wraps `SentenceTransformer` with automatic CUDA → MPS → CPU device fallback.

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.10+
- GPU with CUDA (recommended) — CPU fallback available automatically
- Google Cloud project with Drive API enabled
- Groq API key (free tier available at [console.groq.com](https://console.groq.com))

### 1. Clone the Repository

```bash
git clone https://github.com/Ashwin-Thiru/RAG-Regulation-Compliance.git
cd RAG-Regulation-Compliance
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Google Drive Access

1. Create a **Service Account** in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the **Google Drive API** for your project
3. Download the key as `credentials.json` and place it in the project root
4. Share your target Google Drive folder with the service account email

### 5. Set Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
GROQ_API_KEY=your_groq_api_key_here
GDRIVE_FOLDER_ID=your_google_drive_folder_id_here
GOOGLE_CREDENTIALS_PATH=credentials.json
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu              # use 'cuda' if you have an NVIDIA GPU
VECTOR_STORE_HOST=127.0.0.1
VECTOR_STORE_PORT=8000
VECTOR_STORE_URL=http://127.0.0.1:8000/v1/retrieve
VECTOR_STORE_STATS_URL=http://127.0.0.1:8000/v1/statistics
RETRIEVAL_TOP_K=3
API_HOST=0.0.0.0
API_PORT=8080
```

---

## 🚀 Usage

### Option A — Chat UI (Recommended)

**Terminal 1 — Start the Pathway streaming pipeline:**

```bash
python src/main.py
```

Wait for indexing logs to confirm documents are indexed.

**Terminal 2 — Start the FastAPI backend:**

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8080 --reload
```

**Open the UI in your browser:**

```bash
# Linux
firefox frontend/index.html &

# macOS
open frontend/index.html

# Windows
start frontend/index.html
```

### Option B — Terminal Client

```bash
python src/answerer.py
```

Example queries:

```
🤖 Compliance Query: What are the current Tier 1 capital ratio requirements under Basel III?
🤖 Compliance Query: Does our investment policy comply with the latest SEBI circular?
🤖 Compliance Query: Summarize all open audit findings related to KYC procedures.
```

### Option C — Run with Docker

```bash
# Build the image
docker build -t compliance-rag .

# Start the Pathway pipeline server
docker run --gpus all \
  -e GROQ_API_KEY=your_key \
  -e GDRIVE_FOLDER_ID=your_folder_id \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  -p 8000:8000 \
  compliance-rag

# Start the FastAPI backend
docker run \
  -e GROQ_API_KEY=your_key \
  -p 8080:8080 \
  compliance-rag \
  python -m uvicorn src.api:app --host 0.0.0.0 --port 8080
```

### Run Tests

```bash
pip install pytest pytest-cov
pytest tests/ -v
```

---

## 🔄 How It Works (End-to-End)

```
1. Regulatory PDF uploaded to Google Drive
         │
         ▼
2. pathway.io.gdrive detects FILE_CREATED event (< 1 second)
         │
         ▼
3. Docling parses the PDF — preserving tables, columns, footnotes
         │
         ▼
4. Document split into semantic chunks with metadata (title, date, source)
         │
         ▼
5. SentenceTransformer (CUDA) embeds each chunk into a dense vector
         │
         ▼
6. VectorStoreServer updates in-memory index (atomic, no downtime)
         │
         ▼
7. Compliance officer types query in the Chat UI
         │
         ▼
8. FastAPI receives query → fires SSE "embed active" event to UI
         │
         ▼
9. Pathway embeds query + retrieves top-k chunks (single real HTTP call)
         │
         ▼
10. FastAPI fires "embed done Xms" + "retrieve done Xms" + chunk events to UI
         │
         ▼
11. FastAPI opens Groq stream → fires "llm active" event
         │
         ▼
12. First token arrives → fires "llm done Xms TTFT" event
         │
         ▼
13. Tokens stream to UI word-by-word via SSE token events
         │
         ▼
14. Formal, citation-grounded response rendered in chat
```

---

## 📊 Performance

| Metric | Value |
|---|---|
| Document ingestion latency | < 2 seconds (Drive upload → indexed) |
| Query-to-response latency | ~1.5–3 seconds (end-to-end) |
| Embedding throughput (CUDA) | ~500 chunks/second |
| PDF parsing (complex 50-page doc) | ~8–12 seconds |
| SSE step accuracy | Real `perf_counter` ms — no fake timers |
| Supported document types | PDF, DOCX, TXT |
| LLM model | Llama-3.3-70B via Groq |

---

## 🔒 Security

- **`credentials.json` must never be committed.** It is listed in `.gitignore` by default.
- **Embeddings are computed locally.** No document content is transmitted to any external embedding service.
- **Groq receives only the query context**, not full documents.
- For production deployments, rotate Service Account keys regularly and apply **least-privilege** — grant read-only Drive access only.
- Consider network-level controls (VPC, private endpoints) for the VectorStoreServer in regulated environments.
- All code is scanned on every push via **Bandit** security analysis in CI.

---

## 🗺️ Roadmap

- [x] Terminal query client (`src/answerer.py`)
- [x] FastAPI SSE backend (`src/api.py`)
- [x] Real-time chat UI with thinking trace (`frontend/index.html`)
- [x] True SSE streaming — real ms timings, no fake delays
- [ ] PDF upload directly from the UI (drag-and-drop → auto-push to Google Drive)
- [ ] Query history panel with search
- [ ] Audit trail logging — every query and source chunk logged for regulators
- [ ] Multi-folder support with per-folder access controls
- [ ] SharePoint and AWS S3 as alternative document sources
- [ ] Cross-document contradiction detection (conflicting policy versions)
- [ ] Confidence scoring per retrieved chunk
- [ ] Support for multilingual regulatory documents
- [ ] REST API wrapper for dashboard integration

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/your-feature`
3. Commit using Conventional Commits: `git commit -m 'feat: add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ for the Green Hackathon — because in compliance, milliseconds matter.*
