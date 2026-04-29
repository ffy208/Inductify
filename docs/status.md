# Inductify — Status Snapshot

*Last updated: 2026-04-27*

## Backend

| Module | File | Status |
|--------|------|--------|
| FastAPI app + CORS | `backend/main.py` | Done — needs async + auth |
| ChromaDB manager | `backend/database/db_manager.py` | Done — `update_db` unimplemented |
| OpenAI embeddings | `backend/embedding/call_embedding.py` | Done |
| LLM provider factory | `backend/llm/llm_manager.py` | Partial — OpenAI only |
| SQLite LangChain cache | `.langchain.db` | Done |
| Document loaders | `db_manager._load_file` | Done — PDF/Excel/MD/TXT |
| `/ask` endpoint | `main.py` | Done — sync, no citation, no history |
| `/upload` endpoint | — | **Missing** |
| `/index` endpoint | — | **Missing** |
| Incremental DB update | `db_manager.update_db` | **NotImplementedError** |
| Re-ranker | — | **Missing** |
| LangChain RAG chain | — | **Missing** (raw OpenAI SDK used) |
| Conversation history | — | **Missing** |
| LangChain agent | — | **Missing** |
| API auth / rate limiting | — | **Missing** |

## Frontend

| Module | Status |
|--------|--------|
| Gradio demo (`app.py`) | Done — calls `/ask`, no citations shown |
| Next.js skeleton | Done — HeroUI components, no real API calls |
| Next.js ↔ backend integration | **Missing** |
| Source citation display | **Missing** |
| Document upload UI | **Missing** |

## Infrastructure

| Item | Status |
|------|--------|
| Backend Docker | Done |
| Frontend Docker | Commented out in docker-compose |
| Gradio Docker | Commented out in docker-compose |
| `.env.example` | **Missing** |

## Test Coverage

| File | Tests |
|------|-------|
| `tests/test_main.py` | Basic /ask smoke test |
| `tests/test_db_manager.py` | Load + create DB |
| `tests/test_vector_db.py` | Similarity search |
| `tests/test_call_embedding.py` | Embedding call |
| `tests/test_llm_manager.py` | LLM factory |
| Integration tests | **Missing** |
| Re-ranker tests | **Missing** |
| Upload/index tests | **Missing** |
