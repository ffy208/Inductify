import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.auth import limiter, verify_api_key
from backend.database.db_manager import DatabaseManager
from backend.embedding.reranker import Reranker
from backend.llm import langchain_chain
from backend.llm import agent as llm_agent

EMBEDDING_PROVIDER = "openai"

# Uploaded files are stored here before indexing
_default_upload = Path(__file__).parent / "database" / "input_db" / "uploads"
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(_default_upload)))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".xlsx"}

_ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]

app = FastAPI(title="Inductify Onboarding API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-API-Key"],
)

db_manager = DatabaseManager(embedding=EMBEDDING_PROVIDER)
vector_db = db_manager.get_db()

_reranker: Optional[Reranker] = None if os.getenv("DISABLE_RERANKER") else Reranker()

_chain = langchain_chain.build_rag_chain(
    vector_db,
    reranker=_reranker,
    k_fetch=10,
    k_final=3,
)

_agent_executor = llm_agent.build_agent(
    vector_db,
    reranker=_reranker,
    k_fetch=10,
    k_final=3,
)


# ---------------------------------------------------------------------------
# In-memory job store
# ---------------------------------------------------------------------------

JobStatus = Literal["uploaded", "indexing", "done", "error"]


@dataclass
class _Job:
    job_id: str
    filenames: list[str]
    paths: list[str]
    status: JobStatus = "uploaded"
    chunks_added: int = 0
    error: str = ""


_jobs: dict[str, _Job] = {}


def _run_indexing(job_id: str) -> None:
    """Background task: index files and update job status."""
    job = _jobs[job_id]
    job.status = "indexing"
    try:
        job.chunks_added = db_manager.update_db(job.paths)
        job.status = "done"
    except Exception as exc:
        job.status = "error"
        job.error = str(exc)


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


class UploadResponse(BaseModel):
    job_id: str
    filenames: list[str]


class IndexRequest(BaseModel):
    job_id: str


class IndexResponse(BaseModel):
    job_id: str
    status: str


class IndexStatusResponse(BaseModel):
    job_id: str
    status: str
    chunks_added: int
    error: str


# ---------------------------------------------------------------------------
# Chat endpoints
# ---------------------------------------------------------------------------

@app.post("/ask", response_model=ChatResponse, dependencies=[Depends(verify_api_key)])
@limiter.limit("30/minute")
async def ask_question(request: Request, query: ChatRequest) -> ChatResponse:
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


@app.post("/agent/ask", response_model=ChatResponse, dependencies=[Depends(verify_api_key)])
@limiter.limit("30/minute")
async def agent_ask(request: Request, query: ChatRequest) -> ChatResponse:
    """Answer using a ReAct agent that decides whether to search or introspect."""
    result = await llm_agent.ask_agent(
        session_id=query.session_id,
        question=query.message,
        executor=_agent_executor,
    )
    return ChatResponse(
        answer=result["answer"],
        sources=[SourceItem(**s) for s in result["sources"]],
    )


@app.delete("/session/{session_id}", status_code=204)
async def delete_session(session_id: str) -> None:
    """Clear conversation history for a session (RAG chain + agent)."""
    langchain_chain.clear_session(session_id)
    llm_agent.clear_agent_session(session_id)


# ---------------------------------------------------------------------------
# Upload & indexing endpoints
# ---------------------------------------------------------------------------

@app.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_files(files: list[UploadFile]) -> UploadResponse:
    """
    Upload one or more documents (txt / md / pdf / xlsx).

    Returns a job_id that can be used with POST /index to trigger vectorization.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    job_id = str(uuid.uuid4())
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    saved_names: list[str] = []
    saved_paths: list[str] = []

    for upload in files:
        suffix = Path(upload.filename or "").suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type '{suffix}'. Allowed: {ALLOWED_EXTENSIONS}",
            )
        dest = job_dir / (upload.filename or f"file{suffix}")
        dest.write_bytes(await upload.read())
        saved_names.append(upload.filename or dest.name)
        saved_paths.append(str(dest))

    _jobs[job_id] = _Job(job_id=job_id, filenames=saved_names, paths=saved_paths)
    return UploadResponse(job_id=job_id, filenames=saved_names)


@app.post("/index", response_model=IndexResponse)
async def index_documents(
    body: IndexRequest,
    background_tasks: BackgroundTasks,
) -> IndexResponse:
    """
    Trigger incremental vectorization for a previously uploaded job.

    The indexing runs in the background; poll GET /index/status/{job_id}
    to track progress.
    """
    job = _jobs.get(body.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job_id not found.")
    if job.status not in ("uploaded", "error"):
        raise HTTPException(
            status_code=409,
            detail=f"Job is already in state '{job.status}'.",
        )
    background_tasks.add_task(_run_indexing, body.job_id)
    return IndexResponse(job_id=body.job_id, status="indexing")


@app.get("/index/status/{job_id}", response_model=IndexStatusResponse)
async def index_status(job_id: str) -> IndexStatusResponse:
    """Return the current indexing status for a job."""
    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job_id not found.")
    return IndexStatusResponse(
        job_id=job.job_id,
        status=job.status,
        chunks_added=job.chunks_added,
        error=job.error,
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "reranker": "disabled" if _reranker is None else "enabled",
        "agent": "enabled",
    }
