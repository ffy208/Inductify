"""
CrossEncoder re-ranker for RAG pipeline.

Usage:
    reranker = Reranker()                  # lazy — model loads on first call
    top_docs = reranker.rerank(query, docs, top_k=3)

The CrossEncoder scores each (query, passage) pair and returns the top_k
documents sorted by relevance.  This runs after the initial ANN retrieval
(typically k=10) and before the LLM generation step.

Model: cross-encoder/ms-marco-MiniLM-L-6-v2
  - ~22 MB, CPU-friendly
  - Trained on MS MARCO passage ranking
  - Good general-purpose relevance signal
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from langchain_core.documents import Document


_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker:
    """Thin wrapper around a CrossEncoder with lazy model loading."""

    def __init__(self, model_name: str = _MODEL_NAME) -> None:
        self._model_name = model_name
        self._model: Any = None  # loaded on first use

    def _load(self) -> None:
        if self._model is None:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self._model_name)

    def rerank(
        self,
        query: str,
        docs: list[Document],
        top_k: int = 3,
    ) -> list[Document]:
        """
        Score each doc against *query* and return the top_k by relevance.

        Documents are returned with an added ``rerank_score`` metadata key
        so callers can surface the score in source citations.
        """
        if not docs:
            return docs

        self._load()

        pairs = [(query, doc.page_content) for doc in docs]
        scores: list[float] = self._model.predict(pairs).tolist()

        ranked = sorted(
            zip(scores, docs),
            key=lambda x: x[0],
            reverse=True,
        )

        result = []
        for score, doc in ranked[:top_k]:
            # attach score without mutating the original document's metadata dict
            new_meta = {**doc.metadata, "rerank_score": round(score, 4)}
            doc = doc.__class__(page_content=doc.page_content, metadata=new_meta)
            result.append(doc)

        return result
