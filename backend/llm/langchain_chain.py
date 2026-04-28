"""
RAG chain using LangChain LCEL (1.x compatible).

build_rag_chain()  — creates the chain at startup, bound to vector_db
ask()              — async; routes one question, returns answer + sources
clear_session()    — drops one session's history

Re-ranking:
    Pass a Reranker instance to build_rag_chain().  When present the
    retriever fetches k_fetch candidates (default 10) and the reranker
    narrows them down to k_final (default 3) before the LLM sees them.
    Without a reranker, k_fetch documents go straight to the LLM.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from backend.llm.llm_manager import get_llm

if TYPE_CHECKING:
    from backend.embedding.reranker import Reranker

# ---------------------------------------------------------------------------
# Per-session chat history  {session_id: [(human, ai), ...]}
# ---------------------------------------------------------------------------
_session_histories: dict[str, list[tuple[str, str]]] = {}

# ---------------------------------------------------------------------------
# Grounding prompt
# ---------------------------------------------------------------------------
_QA_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful onboarding assistant. "
     "Answer the question using ONLY the information in the context below. "
     "If the answer is not present in the context, say \"I don't have that information.\"\n\n"
     "Context:\n{context}"),
    ("human", "{question}"),
])


def _format_docs(docs: list) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


class _RagChain:
    """Wraps retriever + optional reranker + generation chain."""

    def __init__(
        self,
        retriever: Any,
        chain: Any,
        reranker: Optional[Reranker] = None,
        k_final: int = 3,
    ) -> None:
        self._retriever = retriever
        self._chain = chain
        self._reranker = reranker
        self._k_final = k_final

    async def ainvoke(self, question: str) -> dict[str, Any]:
        docs = await self._retriever.ainvoke(question)

        if self._reranker is not None:
            # rerank is CPU-bound — run in executor to keep async loop free
            import asyncio
            loop = asyncio.get_event_loop()
            docs = await loop.run_in_executor(
                None,
                lambda: self._reranker.rerank(question, docs, top_k=self._k_final),
            )

        answer = await self._chain.ainvoke({
            "context": _format_docs(docs),
            "question": question,
        })
        return {"answer": answer, "source_documents": docs}


def build_rag_chain(
    vector_db: Any,
    model: str = "gpt-4.1-mini",
    temperature: float = 0.3,
    reranker: Optional[Reranker] = None,
    k_fetch: int = 10,
    k_final: int = 3,
) -> _RagChain:
    """
    Return a _RagChain bound to *vector_db*.

    Args:
        vector_db:   ChromaDB (or any LangChain vectorstore)
        model:       OpenAI model name
        temperature: LLM temperature
        reranker:    Optional Reranker; when provided retrieves k_fetch and
                     re-ranks to k_final.  When None retrieves k_final directly.
        k_fetch:     Candidates to retrieve before re-ranking (ignored without reranker)
        k_final:     Documents passed to the LLM as context
    """
    llm = get_llm(model=model, temperature=temperature)
    k = k_fetch if reranker is not None else k_final
    retriever = vector_db.as_retriever(search_kwargs={"k": k})
    chain = _QA_PROMPT | llm | StrOutputParser()
    return _RagChain(retriever, chain, reranker=reranker, k_final=k_final)


async def ask(
    session_id: str,
    question: str,
    chain: _RagChain,
) -> dict[str, Any]:
    """
    Run one question through the chain asynchronously.

    Returns::

        {
            "answer": str,
            "sources": [{"filename": str, "chunk_index": int,
                         "excerpt": str, "score": float | None}]
        }
    """
    result = await chain.ainvoke(question)

    history = _session_histories.get(session_id, [])
    _session_histories[session_id] = history + [(question, result["answer"])]

    sources = [
        {
            "filename": doc.metadata.get("source", ""),
            "chunk_index": i,
            "excerpt": doc.page_content[:200],
            "score": doc.metadata.get("rerank_score"),
        }
        for i, doc in enumerate(result.get("source_documents", []))
    ]

    return {"answer": result["answer"], "sources": sources}


def clear_session(session_id: str) -> bool:
    """Remove session history. Returns True if the session existed."""
    return _session_histories.pop(session_id, None) is not None
