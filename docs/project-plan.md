# Inductify — Project Plan

## What the Resume Claims

| Claim | Tech |
|-------|------|
| Agentic AI onboarding chatbot | LangChain, RAG |
| Query 10K+ internal docs | ChromaDB, OpenAI Embeddings |
| Cited answers under 5s | Source attribution, async |
| Real-time Q&A + document indexing endpoints | FastAPI RESTful |
| Sub-5s latency, async processing | Async FastAPI |
| Top-3 accuracy 56% → 88% | Chunk-level re-ranking |
| Hallucination reduction 35% | Re-ranker, grounded prompts |
| Modular containerized | Docker, docker-compose |

---

## Current State (as of 2026-04-27)

### What exists
- FastAPI backend with single `/ask` endpoint (synchronous)
- ChromaDB vector store + OpenAI embeddings via LangChain
- Document loaders: PDF, Excel, Markdown, TXT
- SQLite LangChain cache
- Gradio demo frontend (`app.py`)
- Next.js frontend skeleton (HeroUI components, **not connected to backend**)
- Docker for backend only (frontend + gradio commented out)

### Critical gaps vs. resume
| Feature | Status |
|---------|--------|
| Cited answers (source attribution) | Missing |
| Async `/ask` endpoint | Missing |
| Document upload/indexing API | Missing (`update_db` is `NotImplementedError`) |
| Chunk-level re-ranking | Missing |
| LangChain agent / chain (not raw OpenAI call) | Missing |
| Conversation history per session | Missing |
| Frontend ↔ backend integration | Missing |
| Full Docker (all services) | Missing |
| API auth / rate limiting | Missing |

---

## Feature Roadmap

### F1 — Cited Answers (Source Attribution)
**Why:** Resume explicitly claims "cited answers". Currently the `/ask` response returns only plain text.

**What to build:**
- Return `sources` list in `/ask` response: `{filename, page/chunk_index, excerpt}`
- Modify `similarity_search` to return `Document` metadata alongside answer
- Update Gradio + Next.js frontend to display source cards

**Files:** `backend/main.py`, `TSfrontend/components/messaging-chat-message.tsx`

---

### F2 — Async Pipeline
**Why:** Resume claims sub-5s latency and async processing. Current endpoint is synchronous.

**What to build:**
- Convert `/ask` to `async def` using `await`
- Use LangChain async methods (`ainvoke`, `asimilarity_search`)
- Parallel embedding + retrieval where possible

**Files:** `backend/main.py`, `backend/embedding/call_embedding.py`

---

### F3 — Document Upload & Indexing API
**Why:** Resume claims "document indexing" endpoint. `update_db` currently raises `NotImplementedError`.

**What to build:**
- `POST /upload` — accept multipart file(s), store to `input_db/`, return job_id
- `POST /index` — trigger incremental vectorization of uploaded files
- `GET /index/status/{job_id}` — check indexing progress
- Implement `update_db` in `DatabaseManager`: chunk new docs, upsert into existing Chroma collection (don't rebuild from scratch)

**Files:** `backend/main.py`, `backend/database/db_manager.py`

---

### F4 — Chunk-Level Re-Ranking
**Why:** Resume specifically claims accuracy improvement from 56% → 88% via re-ranking.

**What to build:**
- Retrieve top-10 candidates from ChromaDB via `similarity_search(k=10)`
- Re-rank with a CrossEncoder (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2` from `sentence-transformers`)
- Pass top-3 re-ranked chunks as context to LLM
- Add `reranker.py` in `backend/embedding/`

**Files:** `backend/embedding/reranker.py` (new), `backend/main.py`

---

### F5 — Proper LangChain RAG Chain
**Why:** Resume claims "LangChain" and "agentic AI". Current code bypasses LangChain for generation (calls OpenAI SDK directly).

**What to build:**
- Replace raw `OpenAI()` call in `call_embedding.py` with a `RetrievalQA` or `ConversationalRetrievalChain`
- Add `PromptTemplate` with grounding instruction (reduces hallucination)
- Wire in `ChatMessageHistory` for multi-turn sessions
- Add a `langchain_chain.py` module

**Files:** `backend/llm/langchain_chain.py` (new), `backend/main.py`

---

### F6 — Session / Conversation History
**Why:** Resume's chatbot must support multi-turn conversation, not one-shot Q&A.

**What to build:**
- In-memory or Redis-backed `ChatMessageHistory` keyed by `session_id`
- `/ask` reads history → appends user message → calls chain → appends assistant reply
- `DELETE /session/{session_id}` to reset history

**Files:** `backend/main.py`, `backend/llm/langchain_chain.py`

---

### F7 — Full Docker Deployment
**Why:** Resume claims "containerized" system with all services.

**What to build:**
- Uncomment `frontend` and `gradio` services in `docker-compose.yml`
- Add health-check for backend before frontend starts
- Add `.env.example` with required vars (`OPENAI_API_KEY`, `NEXT_PUBLIC_API_URL`)
- Verify `Dockerfile.gradio` and `TSfrontend/Dockerfile`

**Files:** `docker-compose.yml`, `Dockerfile.gradio`, `TSfrontend/Dockerfile`

---

### F8 — Next.js Frontend ↔ Backend Integration
**Why:** The Next.js UI is a static template with no real API calls. It must actually query the backend.

**What to build:**
- Replace hardcoded mock data in `components/data.ts` with API client
- `lib/api.ts`: typed fetch wrapper for `/ask`, `/upload`, `/index`
- Wire `PromptInputWithEnclosedActions` send button → `POST /ask` → append message to chat
- Display source citations below each AI message
- Upload button triggers `POST /upload` + `POST /index`

**Files:** `TSfrontend/lib/api.ts` (new), `TSfrontend/components/app.tsx`, `TSfrontend/components/prompt-input-with-enclosed-actions.tsx`

---

### F9 — LangChain Agent (Agentic Behavior)
**Why:** Resume specifically says "agentic AI". This means the system should be able to decide which tool to use (vector search vs. metadata lookup vs. direct answer).

**What to build:**
- Define tools: `VectorSearchTool`, `DocumentListTool`
- Create a `ReAct` agent using `langchain.agents.create_react_agent`
- Agent decides whether to retrieve docs or answer from context
- Fallback to direct LLM if retrieval confidence is low

**Files:** `backend/llm/agent.py` (new), `backend/main.py`

---

### F10 — API Security (Auth + Rate Limiting)
**Why:** Resume claims "secure RESTful endpoints".

**What to build:**
- API key header auth via FastAPI `Security` dependency (`X-API-Key`)
- Rate limiting middleware (e.g., `slowapi`)
- CORS locked to specific origins in production (currently `allow_origins=["*"]`)

**Files:** `backend/main.py`, `backend/auth.py` (new)

---

## Implementation Order

```
F1  (cited answers)     ✅ DONE
F2  (async pipeline)    ✅ DONE
F3  (upload/index API)  ✅ DONE
F4  (re-ranking)        ✅ DONE
F5  (LangChain chain)   ✅ DONE
F6  (session history)   ✅ DONE
F8  (frontend wiring)   ✅ DONE

A   (ablation eval)     ← NEXT — validate 56%→88% claim with real data
F7  (full Docker)       ← after ablation — complete deployment story
F9  (agent)             ← supports "agentic AI" resume claim
F10 (auth)              ← final hardening
```

---

## Task A — Ablation Evaluation

**Why:** The core resume claim is "56% → 88% accuracy via chunk-level re-ranking."
This number is currently an estimate. Running the ablation produces real, defensible data.

**What to build:**

`rag_eval.py` — evaluation script with three conditions:

| Condition | Setup | Expected |
|-----------|-------|----------|
| LLM-only | No retrieval, raw GPT-4.1-mini | ~10–20% |
| RAG, no re-rank | top-3 cosine similarity | ~60–75% |
| RAG + re-rank | top-10 → CrossEncoder → top-3 | ~85–92% |

**Inputs already available:**
- `data/eval_qa.json` — 54 Q&A pairs (synthetic unique facts)
- `data/synthetic_docs/` — 10K indexed documents
- `data/ground_truth.json` — canonical answers

**Output:**
- `data/eval_results.json` — per-condition accuracy + per-question detail
- Console table with accuracy, latency, and pass/fail per category

**Files:** `rag_eval.py` (new), `data/eval_results.json` (generated)

---

## Backend Module Structure (Target)

```
backend/
├── main.py                  # FastAPI app, routes
├── auth.py                  # API key auth, rate limiting
├── database/
│   └── db_manager.py        # ChromaDB: load, create, update (incremental)
├── embedding/
│   ├── call_embedding.py    # OpenAI embeddings
│   └── reranker.py          # CrossEncoder re-ranker (NEW)
└── llm/
    ├── llm_manager.py       # LLM provider factory
    ├── langchain_chain.py   # RAG chain + session history (NEW)
    └── agent.py             # ReAct agent with tools (NEW)
```

---

## API Contract (Target)

```
POST /ask
  Body: { session_id, message }
  Response: { answer, sources: [{filename, chunk_index, excerpt, score}] }

POST /upload
  Body: multipart/form-data files[]
  Response: { job_id, filenames }

POST /index
  Body: { job_id }
  Response: { status, chunks_added }

GET  /index/status/{job_id}
  Response: { status, progress }

DELETE /session/{session_id}
  Response: { cleared }
```
