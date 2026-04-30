# Inductify — Status Snapshot

*Last updated: 2026-04-30*

## Backend

| Module | File | Status |
|--------|------|--------|
| FastAPI app + CORS | `backend/main.py` | ✅ Done — async, cited answers, session history |
| ChromaDB manager | `backend/database/db_manager.py` | ✅ Done — incremental `update_db` implemented |
| OpenAI embeddings | `backend/embedding/call_embedding.py` | ✅ Done |
| LLM provider factory | `backend/llm/llm_manager.py` | ✅ Done — pipenv bug fixed |
| LangChain RAG chain | `backend/llm/langchain_chain.py` | ✅ Done — LCEL, grounding prompt, session history |
| CrossEncoder re-ranker | `backend/embedding/reranker.py` | ✅ Done — k=10→top-3, `rerank_score` in metadata |
| SQLite LangChain cache | `.langchain.db` | ✅ Done |
| Document loaders | `db_manager._load_file` | ✅ Done — PDF/Excel/MD/TXT |
| `/ask` endpoint | `main.py` | ✅ Done — async, sources, session history |
| `/upload` endpoint | `main.py` | ✅ Done — multipart, ext validation, job_id |
| `/index` endpoint | `main.py` | ✅ Done — BackgroundTasks, 409/404 guards |
| `/index/status/{job_id}` | `main.py` | ✅ Done |
| `/session/{id}` DELETE | `main.py` | ✅ Done |
| `/health` | `main.py` | ✅ Done — reports reranker + agent status |
| LangChain agent | `backend/llm/agent.py` | ✅ Done — `POST /agent/ask`, tool-calling ReAct |
| API auth / rate limiting | `backend/auth.py` | ✅ Done — X-API-Key header, slowapi 30/min on /ask |

## Frontend

| Module | Status |
|--------|--------|
| Next.js ↔ backend integration | ✅ Done — `frontend/lib/api.ts` |
| Live chat with real API calls | ✅ Done — `app.tsx` rewritten |
| Source citation cards | ✅ Done — expandable, shows score |
| Document upload UI | ✅ Done — paperclip → upload → index → status chip |
| Loading / error states | ✅ Done |
| Session management (New Chat) | ✅ Done — clears backend history |

## Infrastructure

| Item | Status |
|------|--------|
| Backend Docker | ✅ Done — health check added |
| Frontend Docker | ✅ Done — `depends_on: backend healthy` |
| `.env.example` | ✅ Done |

## Evaluation

| Item | Status |
|------|--------|
| Synthetic corpus generator | ✅ Done — `rag_eval_builder/` |
| 10K documents generated | ✅ Done — `data/synthetic_docs/` |
| Eval Q&A set (54 pairs) | ✅ Done — `data/eval_qa.json` |
| Ground truth | ✅ Done — `data/ground_truth.json` |
| Ablation eval script | ✅ Done — `rag_eval.py`, 3-condition ablation with `--resume` and `--policy-corpus-only` flags |
| Policy-only vector DB | ✅ Done — `build_policy_db.py` extracts 4,172 policy chunks, zero API calls |
| Measured accuracy numbers | ✅ Done — LLM-only 1.9% → RAG (mixed corpus) 64.8% → RAG (policy-only corpus) **83.3%** |
| Root cause analysis | ✅ Done — distractor contamination + numeric-qualifier scoring bug identified and fixed |

## Test Coverage

| File | Tests |
|------|-------|
| `tests/test_main.py` | Basic /ask smoke test |
| `tests/test_db_manager.py` | Load + create DB |
| `tests/test_vector_db.py` | Similarity search |
| `tests/test_call_embedding.py` | Embedding call |
| `tests/test_llm_manager.py` | LLM factory |
| Integration tests | ❌ Missing |
| Re-ranker tests | ❌ Missing |
| Upload/index tests | ❌ Missing |
