import os
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from pydantic import BaseModel

from backend.database.db_manager import DatabaseManager
from backend.embedding.reranker import Reranker
from backend.llm import langchain_chain

EMBEDDING_PROVIDER = "openai"

app = FastAPI(title="Inductify Onboarding API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

set_llm_cache(SQLiteCache(database_path=".langchain.db"))

db_manager = DatabaseManager(embedding=EMBEDDING_PROVIDER)
vector_db = db_manager.get_db()

# Re-ranker: lazy-loads the CrossEncoder model on first request.
# Set DISABLE_RERANKER=1 to run without re-ranking (ablation baseline).
_reranker: Optional[Reranker] = None if os.getenv("DISABLE_RERANKER") else Reranker()

_chain = langchain_chain.build_rag_chain(
    vector_db,
    reranker=_reranker,
    k_fetch=10,
    k_final=3,
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str
    message: str


class SourceItem(BaseModel):
    filename: str
    chunk_index: int
    excerpt: str
    score: Optional[float] = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceItem]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/ask", response_model=ChatResponse)
async def ask_question(query: ChatRequest) -> ChatResponse:
    """Answer a question using RAG + re-ranking. Returns answer and source citations."""
    result = await langchain_chain.ask(
        session_id=query.session_id,
        question=query.message,
        chain=_chain,
    )
    return ChatResponse(
        answer=result["answer"],
        sources=[SourceItem(**s) for s in result["sources"]],
    )


@app.delete("/session/{session_id}", status_code=204)
async def delete_session(session_id: str) -> None:
    """Clear conversation history for a session."""
    langchain_chain.clear_session(session_id)


@app.get("/health")
async def health() -> dict:
    reranker_status = "disabled" if _reranker is None else "enabled"
    return {"status": "ok", "reranker": reranker_status}
