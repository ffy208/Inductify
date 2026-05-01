"""
ReAct agent for agentic onboarding Q&A.

Uses langgraph.prebuilt.create_react_agent (LangGraph tool-calling agent).
The agent decides per turn which tool to invoke:
  - vector_search:   semantic retrieval from the policy knowledge base
  - list_documents:  enumerate document categories available

Usage:
    executor = build_agent(vector_db, reranker=_reranker)
    result   = await ask_agent(session_id, question, executor)
"""
from __future__ import annotations

from typing import Any, Optional

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

from backend.llm.llm_manager import get_llm

# ---------------------------------------------------------------------------
# Document categories (static — no DB query needed)
# ---------------------------------------------------------------------------

_CATEGORIES = "\n".join(f"  • {c}" for c in (
    "Benefits (health, dental, vision, HSA, PTO)",
    "Code of Conduct (ethics, conflicts of interest, disciplinary process)",
    "Expense & Reimbursement (limits, approval thresholds, receipts)",
    "IT & Security (VPN, MFA, password policy, session timeouts, incident reporting)",
    "Onboarding & Offboarding (probation, equipment return, background checks)",
    "Performance Reviews (OKRs, self-review forms, bonus eligibility)",
    "Professional Development (training allowances, certification support)",
    "Remote Work (days per week, stipend, equipment budget)",
    "Rewards & Recognition (program codes, nomination process)",
    "Time Off & Leave (vacation accrual, sick leave, parental leave)",
))

_SYSTEM_PROMPT = (
    "You are a helpful onboarding assistant for company employees. "
    "Answer questions about company policies, benefits, IT procedures, and HR topics. "
    "Always use tools to look up accurate facts — never guess company-specific details "
    "such as dollar amounts, codes, IDs, or time limits."
)

# ---------------------------------------------------------------------------
# Tool factories (closures over vector_db / reranker)
# ---------------------------------------------------------------------------

def _make_tools(
    vector_db: Any,
    reranker: Optional[Any] = None,
    k_fetch: int = 10,
    k_final: int = 3,
) -> list:
    @tool
    def vector_search(query: str) -> str:
        """Search the company policy knowledge base for relevant information.
        Use this for questions about HR policies, benefits, IT procedures,
        onboarding steps, expense limits, VPN setup, and company-specific facts.
        Input: a clear search query string."""
        docs = vector_db.similarity_search(query, k=k_fetch)
        if reranker is not None:
            docs = reranker.rerank(query, docs, top_k=k_final)
        else:
            docs = docs[:k_final]
        if not docs:
            return "No relevant information found in the knowledge base."
        return "\n\n".join(
            f"[{doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
            for doc in docs
        )

    @tool
    def list_documents(query: str) -> str:  # noqa: ARG001
        """List all document categories available in the knowledge base.
        Use this when the user asks what topics you can help with."""
        return f"The knowledge base covers these onboarding topics:\n{_CATEGORIES}"

    return [vector_search, list_documents]


# ---------------------------------------------------------------------------
# Agent builder
# ---------------------------------------------------------------------------

def build_agent(
    vector_db: Any,
    model: str | None = None,
    temperature: float = 0.0,
    reranker: Optional[Any] = None,
    k_fetch: int = 10,
    k_final: int = 3,
) -> Any:
    """Return a compiled LangGraph agent wired to the given vector_db."""
    llm = get_llm(model=model, temperature=temperature)
    tools = _make_tools(vector_db, reranker, k_fetch, k_final)
    return create_react_agent(llm, tools, prompt=_SYSTEM_PROMPT)


# ---------------------------------------------------------------------------
# Ask helper + per-session history
# ---------------------------------------------------------------------------

_agent_histories: dict[str, list[tuple[str, str]]] = {}


async def ask_agent(
    session_id: str,
    question: str,
    executor: Any,
) -> dict[str, Any]:
    """Run one question through the agent asynchronously."""
    result = await executor.ainvoke({"messages": [HumanMessage(content=question)]})

    messages = result.get("messages", [])
    # Last message is the AI final answer
    answer = ""
    for msg in reversed(messages):
        if hasattr(msg, "content") and not isinstance(msg, ToolMessage):
            content = msg.content
            if isinstance(content, str) and content.strip():
                answer = content.strip()
                break
    if not answer:
        answer = "I could not determine an answer."

    # Extract source filenames from ToolMessage contents (vector_search calls)
    import re
    seen: set[str] = set()
    sources: list[dict] = []
    for msg in messages:
        if isinstance(msg, ToolMessage):
            for match in re.finditer(r"\[([^\]]+)\]", str(msg.content)):
                src = match.group(1)
                if src not in seen:
                    seen.add(src)
                    sources.append({
                        "filename": src,
                        "chunk_index": len(sources),
                        "excerpt": "",
                        "score": None,
                    })

    history = _agent_histories.get(session_id, [])
    _agent_histories[session_id] = history + [(question, answer)]

    return {"answer": answer, "sources": sources}


def clear_agent_session(session_id: str) -> bool:
    """Remove agent session history. Returns True if it existed."""
    return _agent_histories.pop(session_id, None) is not None
