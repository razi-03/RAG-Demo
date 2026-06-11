<<<<<<< HEAD
# RAG Demo — Backend

FastAPI backend for the RAG Demo project. Supports document ingestion (PDF, DOCX, TXT, MD), semantic search with ChromaDB, and LLM-powered answers via OpenAI or Anthropic.

---

## Project Structure

```
backend/
├── app/
│   ├── api/routes/
│   │   ├── documents.py    # Upload, list, delete documents
│   │   ├── query.py        # RAG query + SSE streaming
│   │   └── health.py       # Health check
│   ├── core/
│   │   ├── config.py       # All settings (env vars)
│   │   └── exceptions.py   # Custom HTTP exceptions
│   ├── db/
│   │   └── vector_store.py # ChromaDB CRUD
│   ├── schemas/
│   │   └── rag.py          # Pydantic request/response models
│   ├── services/
│   │   ├── document_service.py   # Text extraction + chunking
│   │   ├── embedding_service.py  # OpenAI or local embeddings
│   │   ├── llm_service.py        # OpenAI / Anthropic generation
│   │   └── rag_service.py        # RAG orchestration
│   └── main.py
├── tests/
│   └── test_api.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Prerequisites

- Python 3.11+
- A virtual environment tool (`venv` or `conda`)

### 2. Clone & navigate

```bash
git clone https://github.com/razi-03/RAG-Demo.git
cd RAG-Demo/backend
```

### 3. Create and activate virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your API key:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...       # get from platform.openai.com
```

**Want to use Anthropic instead?**
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-3-haiku-20240307
```

**No API key? Use the free local fallback:**  
Leave `OPENAI_API_KEY` blank — the backend automatically falls back to `sentence-transformers` for embeddings. Note: you still need an LLM key for generating answers.

---

## Start the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is now live at **http://localhost:8000**

Interactive docs: **http://localhost:8000/docs**

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Check server + vector DB status |
| POST | `/api/documents/upload` | Upload a document (multipart/form-data) |
| GET | `/api/documents/` | List all ingested documents |
| DELETE | `/api/documents/{doc_id}` | Delete a document by ID |
| POST | `/api/query/` | Ask a question (JSON body) |
| GET | `/api/query/stream` | SSE streaming query |

### Upload a document

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@yourfile.pdf"
```

### Ask a question

```bash
curl -X POST http://localhost:8000/api/query/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

### Streaming query (SSE)

```bash
curl "http://localhost:8000/api/query/stream?question=What+is+RAG"
```

---

## Connect to the Frontend

The frontend should point its API calls to `http://localhost:8000`.

If the frontend uses a base URL env var (common in Vite/React projects):

```env
# frontend/.env
VITE_API_BASE_URL=http://localhost:8000
```

CORS is pre-configured for:
- `http://localhost:3000` (React default)
- `http://localhost:5173` (Vite default)
- `http://localhost:8080` (Vue default)

Add other origins in `.env`:
```env
CORS_ORIGINS=["http://localhost:3000","http://your-custom-port"]
```

---

## Run tests

```bash
pytest tests/ -v
```

---

## Supported file types

| Format | Extension |
|--------|-----------|
| PDF | `.pdf` |
| Word | `.docx` |
| Text | `.txt` |
| Markdown | `.md` |
=======
# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
>>>>>>> origin/frontend-sujan
