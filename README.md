# Inductify

An AI-powered onboarding chatbot that answers company policy questions with cited sources. Built with FastAPI, LangChain, ChromaDB, and Next.js.

**Measured accuracy: 1.9% (LLM-only) → 83.3% (RAG) on a 54-question held-out eval set.**

---

## Quick Start (Docker)

**Prerequisites:** Docker Desktop, an OpenAI API key (or a local [Ollama](https://ollama.com) instance).

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd Inductify

# 2. Set your API key
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...

# 3. Start everything
docker compose up --build
```

| Service  | URL                    |
|----------|------------------------|
| Frontend | http://localhost:3000  |
| Backend  | http://localhost:8000  |
| API docs | http://localhost:8000/docs |

The backend starts first; the frontend waits for it to be healthy before coming up.

---

## Using a Local Model (No OpenAI Key)

Install [Ollama](https://ollama.com), pull a model, then leave `OPENAI_API_KEY` empty in `.env`:

```bash
ollama pull llama3.2

# .env
OPENAI_API_KEY=
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

---

## Uploading Documents

1. Open the chat UI at http://localhost:3000
2. Click the paperclip icon → select `.txt`, `.md`, `.pdf`, or `.xlsx` files
3. Click **Index** — the backend vectorizes and stores them in ChromaDB
4. Ask questions. Answers include cited source excerpts.

---

## Project Structure

```
Inductify/
├── backend/               # FastAPI + LangChain RAG
│   ├── llm/               # LLM factory, RAG chain, ReAct agent
│   ├── embedding/         # OpenAI embeddings + CrossEncoder reranker
│   ├── database/          # ChromaDB manager + file loaders
│   ├── auth.py            # API key auth + rate limiting
│   └── main.py            # API endpoints
├── frontend/              # Next.js + HeroUI chat interface
├── eval/                  # Evaluation pipeline (not used in production)
│   ├── rag_eval.py        # Ablation eval script
│   ├── build_policy_db.py # Policy-only vector DB builder
│   └── rag_eval_builder/  # Synthetic corpus generator
├── data/                  # Eval datasets and results
├── docs/                  # Architecture notes and interview story
├── docker-compose.yml
└── .env.example
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ask` | RAG Q&A with source citations |
| `POST` | `/agent/ask` | ReAct agent (tool-calling) |
| `POST` | `/upload` | Upload documents |
| `POST` | `/index` | Trigger vectorization |
| `GET`  | `/index/status/{job_id}` | Indexing progress |
| `DELETE` | `/session/{id}` | Clear conversation history |
| `GET`  | `/health` | Service health check |

---

## Configuration

All options are set via environment variables. See [.env.example](.env.example) for the full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | OpenAI key; leave empty to use Ollama |
| `LLM_MODEL` | `gpt-4.1-mini` | OpenAI model name |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model (when no OpenAI key) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server address |
| `API_KEY` | `disabled` | Backend API key (`disabled` = no auth) |

---

## Tech Stack

- **Backend:** Python · FastAPI · LangChain · ChromaDB · OpenAI / Ollama
- **Frontend:** Next.js 15 · React · TypeScript · HeroUI · Tailwind CSS
- **Infra:** Docker Compose

## License

MIT
