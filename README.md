# Inductify

An AI-powered employee onboarding assistant that answers company policy questions with cited source excerpts. Built with FastAPI, LangChain, ChromaDB, and Next.js.

**Measured accuracy: 1.9% (LLM-only) → 83.3% (RAG) on a 54-question held-out eval set.**

---

## Quick Start (Docker)

**Prerequisites:** Docker Desktop, an OpenAI API key (or a local [Ollama](https://ollama.com) instance).

```bash
# 1. Clone the repo
git clone <repo-url>
cd Inductify

# 2. Set your API key
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...

# 3a. Empty database — upload your own documents via the UI
docker compose up --build

# 3b. Pre-loaded demo mode — 5,500 synthetic policy documents indexed automatically
docker compose --profile demo up --build
```

> **Demo mode** calls the OpenAI Embeddings API on first run (~$0.05 for the full corpus).  
> Watch the `indexer` container logs; once it prints `✓ Done`, all policy questions are answerable.  
> Subsequent `docker compose --profile demo up` runs reuse the persisted ChromaDB volume — no re-indexing.

| Service  | URL                       |
|----------|---------------------------|
| Frontend | http://localhost:3000     |
| Backend  | http://localhost:8000     |
| API docs | http://localhost:8000/docs |

---

## Features

- **RAG Q&A** — retrieves the top-k relevant chunks from ChromaDB, feeds them as context to the LLM, and returns an answer with numbered source citations
- **Conversation history** — multi-turn sessions tracked server-side; 8 pre-seeded demo conversations shown in the sidebar
- **Document upload** — drag-and-drop `.txt`, `.md`, `.pdf`, and `.xlsx` files; backend vectorizes and indexes asynchronously
- **ReAct agent** — optional tool-calling agent (`/agent/ask`) for multi-step reasoning
- **Dark / light mode** — toggle in the chat header
- **Ollama fallback** — runs fully offline when `OPENAI_API_KEY` is unset
- **Optional reranker** — CrossEncoder reranking available as an opt-in (adds ~2.5 GB to the image)

---

## Using a Local Model (No OpenAI Key)

Install [Ollama](https://ollama.com), pull a model, then leave `OPENAI_API_KEY` empty:

```bash
ollama pull llama3.2
```

```env
# .env
OPENAI_API_KEY=
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

---

## Uploading Your Own Documents

1. Open the chat UI at http://localhost:3000
2. Click the **paperclip icon** → select `.txt`, `.md`, `.pdf`, or `.xlsx` files
3. The backend vectorizes and stores them; a status badge shows indexing progress
4. Ask questions — answers include the source filename and a relevant excerpt

---

## Optional: CrossEncoder Reranker

The reranker re-scores retrieved chunks before generation, improving answer quality at the cost of ~2.5 GB of additional image size (PyTorch + sentence-transformers).

```bash
# Enable at build time
INSTALL_RERANKER=true docker compose up --build

# Or in .env:
INSTALL_RERANKER=true
DISABLE_RERANKER=       # leave empty to activate reranking at runtime
```

By default `DISABLE_RERANKER=1` so the backend works without the reranker installed.

---

## Project Structure

```
Inductify/
├── backend/
│   ├── llm/               # LLM factory (OpenAI / Ollama), RAG chain, ReAct agent
│   ├── embedding/         # OpenAI embeddings + optional CrossEncoder reranker
│   ├── database/          # ChromaDB manager, file loaders (txt/md/pdf/xlsx)
│   ├── scripts/           # index_demo_data.py — bulk indexer for demo profile
│   ├── auth.py            # API key auth + rate limiting
│   └── main.py            # FastAPI endpoints
├── frontend/              # Next.js 15 + HeroUI chat interface
│   └── components/        # Sidebar with history, message bubbles, file upload
├── eval/                  # Offline evaluation pipeline (not used in production)
│   ├── rag_eval.py        # 3-condition ablation: LLM-only / RAG / RAG+rerank
│   ├── build_policy_db.py # Builds policy-only ChromaDB for eval
│   └── rag_eval_builder/  # Synthetic corpus + Q&A pair generator
├── data/                  # Eval datasets, synthetic docs, results
├── docs/                  # Architecture notes
├── docker-compose.yml
└── .env.example
```

---

## API Endpoints

| Method   | Endpoint                  | Description                        |
|----------|---------------------------|------------------------------------|
| `POST`   | `/ask`                    | RAG Q&A with source citations      |
| `POST`   | `/agent/ask`              | ReAct agent (tool-calling)         |
| `POST`   | `/upload`                 | Upload documents                   |
| `POST`   | `/index`                  | Trigger vectorization of uploads   |
| `GET`    | `/index/status/{job_id}`  | Indexing progress                  |
| `DELETE` | `/session/{id}`           | Clear conversation history         |
| `GET`    | `/health`                 | Health check                       |

---

## Configuration

All options are set via environment variables. See [.env.example](.env.example) for the full list.

| Variable             | Default                       | Description                                              |
|----------------------|-------------------------------|----------------------------------------------------------|
| `OPENAI_API_KEY`     | —                             | OpenAI key; leave empty or `disabled` to use Ollama      |
| `LLM_MODEL`          | `gpt-4.1-mini`                | OpenAI model name                                        |
| `OLLAMA_MODEL`       | `llama3.2`                    | Ollama model (used when no OpenAI key)                   |
| `OLLAMA_BASE_URL`    | `http://localhost:11434`      | Ollama server address                                    |
| `INSTALL_RERANKER`   | `false`                       | Set `true` at **build time** to install CrossEncoder     |
| `DISABLE_RERANKER`   | `1`                           | Set empty to enable reranker at runtime (requires build) |
| `API_KEY`            | `disabled`                    | Backend API key (`disabled` = no auth)                   |
| `ALLOWED_ORIGINS`    | `*`                           | Comma-separated CORS origins                             |
| `POLICY_ONLY`        | `1`                           | Demo mode: `1` = policy docs only, `0` = full corpus     |

---

## Tech Stack

- **Backend:** Python · FastAPI · LangChain · LangGraph · ChromaDB · OpenAI / Ollama
- **Frontend:** Next.js 15 · React · TypeScript · HeroUI · Tailwind CSS
- **Infra:** Docker Compose (multi-service with health-check dependency chain)

## License

MIT
