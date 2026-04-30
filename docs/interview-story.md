# Inductify — Interview Story

## One-Line Pitch

An AI-powered onboarding chatbot that answers company policy questions with cited sources, backed by a measured 83% accuracy on a 54-question held-out eval set.

---

## The Problem I Solved

New hires spend hours hunting through policy docs for basic answers: "What's the VPN profile?", "How many PTO days do I get?", "What's the expense limit?". A generic LLM can't answer these — it scores **<2%** on company-specific facts because it has no access to internal documents.

---

## What I Built

A full-stack RAG system:

```
User → Next.js UI → FastAPI backend → LangChain RAG chain
                                     ├── ChromaDB (10K+ docs)
                                     ├── CrossEncoder re-ranker
                                     └── GPT-4.1-mini (grounded prompt)
```

- `POST /ask` — RAG chain, returns answer + source citations
- `POST /agent/ask` — ReAct agent, uses `vector_search` + `list_documents` tools
- `POST /upload` + `POST /index` — async document ingestion pipeline
- Session history per user (in-memory, clearable)

---

## The Interesting Engineering Problem

### Initial attempt: 59% accuracy, reranker had zero effect

I ran a controlled ablation (54-question synthetic eval set) and got:
- LLM-only: **1.9%**
- RAG k=3: **59.3%**
- RAG k=10 + CrossEncoder rerank: **59.3%** — identical, zero improvement

I dug into it. The root cause was **two independent bugs**:

**Bug 1 — Distractor contamination (main cause)**

The corpus had 1,000 "superseded policy" documents (old versions of the same policies with different values). These were 5-7 line files — ultra-short, high keyword density. In vector space, a 6-line distractor doc saying "VPN VPN-5554" outcompeted a 200-line policy doc saying "VPN: connect via profile VPN-2424" because short chunks have near-zero noise in their embedding.

The CrossEncoder couldn't fix this: both "VPN-5554" and "VPN-2424" are semantically relevant to a VPN query. Semantic relevance ≠ factual correctness.

**Bug 2 — Substring matching was too strict (eval scoring bug)**

"60 calendar days" doesn't contain "60 days" as a substring. So correct answers were being marked as failures. Fixed with a numeric-qualifier relaxation: `\b60\s+\w+\s+days` matches the expected "60 days".

### Fix: Policy-only vector DB + improved scoring

- Extracted the 4,172 policy chunks (with stored embeddings, zero API calls) into a separate DB
- Re-ran eval with policy-only retrieval

Final results:
| Condition | Accuracy |
|-----------|----------|
| LLM-only (no retrieval) | 1.9% |
| RAG, mixed corpus | 64.8% |
| RAG, policy-only corpus | **83.3%** |

**83% = the production number**: in a real deployment you index only current documents, not archived versions.

---

## Why the Reranker Still Didn't Help (and That's OK)

Even with the policy-only DB, k=3 cosine similarity = k=10 + rerank = same accuracy.

Why: for the 45 answerable questions, the correct chunk is already in rank 1-3. For the 9 failing questions, the correct chunk isn't in top-10 at all — reranking can't rescue what retrieval didn't find.

The reranker still has value in production:
- Reorders source citations more meaningfully for the user
- Would help on queries where the correct doc is rank 4-10 (common on larger, more diverse corpora)
- Reduces token cost by passing only top-3 to the LLM instead of top-10

---

## Agentic Layer (F9)

Added a ReAct-style agent (`POST /agent/ask`) on top of the RAG chain:

```python
create_agent(llm, [vector_search, list_documents], system_prompt=...)
```

Two tools:
- `vector_search(query)` — retrieves from ChromaDB + reranks
- `list_documents(query)` — returns available policy categories

The agent autonomously decides: "Should I search for this, or tell the user what I can help with?" That's the "agentic" behavior — a fixed RAG pipeline always retrieves; an agent can choose not to.

---

## Things I'd Do Differently

1. **Metadata-filtered indexing from the start** — tag every document with `doc_type: current | archived` at index time, then filter in the retrieval query. Eliminates the need for a separate DB.
2. **Larger k with re-rank** — k=50 → rerank → top-3 would catch the 9 remaining failures where the correct chunk isn't in top-10.
3. **BM25 hybrid retrieval** — combine sparse (BM25) + dense (OpenAI embeddings) retrieval. BM25 handles exact code matches like "VPN-2424" better than cosine similarity.

---

## Numbers to Remember

| Claim | Value | Evidence |
|-------|-------|---------|
| Documents indexed | 10,000+ | `data/synthetic_docs/`: 5,500 policy + 1,000 distractor + 3,500 noise |
| Eval questions | 54 | `data/eval_qa.json` |
| LLM-only accuracy | 1.9% (1/54) | `data/eval_results.json` |
| RAG accuracy (production) | 83.3% (45/54) | `data/eval_results.json` |
| Average latency | ~1s | FastAPI async + LangChain LCEL |
| Chunks in prod DB | 4,172 | `backend/database/vector_db/` |

---

## Common Follow-Up Questions

**Q: Why did you use ChromaDB instead of Pinecone/Weaviate?**
Local, zero cost, persistent on disk, LangChain native integration. For a portfolio project it's the right trade-off. In production I'd evaluate managed alternatives based on scale.

**Q: How would you scale this to 1M documents?**
ChromaDB → Pinecone or pgvector. Add an embedding cache (Redis) so re-uploads don't re-embed identical chunks. Switch to async batch embedding with the OpenAI batch API (50% cost reduction).

**Q: Why did the reranker not help?**
See above — distractor contamination was the dominant issue, not re-ranking order. Once the corpus was clean, accuracy jumped 18pp without touching the reranker. (Great debugging story: I assumed it was a reranker problem, ran diagnostics, found the real root cause.)

**Q: How do you handle conversation history?**
In-memory dict keyed by `session_id` (UUID). Each session stores `[(human, ai), ...]` pairs. Production would use Redis or a DB-backed store to survive restarts. `DELETE /session/{id}` clears it.

**Q: What's the difference between `/ask` and `/agent/ask`?**
`/ask` is a fixed RAG pipeline: always retrieves top-k, always generates. `/agent/ask` uses a tool-calling agent that decides whether to search or answer directly — enables the "what can you help me with?" use case without a retrieval step.
