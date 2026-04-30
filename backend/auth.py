"""
API key authentication and rate limiting for the Inductify backend.

Auth:
  Every request must include the header  X-API-Key: <value>
  matching the API_KEY environment variable.  Set API_KEY=disabled
  (or leave it unset) to skip auth entirely — useful for local dev.

Rate limiting (slowapi):
  /ask and /agent/ask are capped at 30 requests/minute per IP.
  All other endpoints: 60 requests/minute per IP.
"""
import os

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address

# ---------------------------------------------------------------------------
# Rate limiter (shared singleton — imported by main.py)
# ---------------------------------------------------------------------------

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

# ---------------------------------------------------------------------------
# API key auth
# ---------------------------------------------------------------------------

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

_API_KEY = os.getenv("API_KEY", "")


def verify_api_key(key: str = Security(_api_key_header)) -> None:
    """FastAPI dependency: raises 401 if the API key is wrong.

    Auth is skipped entirely when API_KEY env var is empty or "disabled" —
    this lets local dev and the eval script work without headers.
    """
    if not _API_KEY or _API_KEY.lower() == "disabled":
        return
    if key != _API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header.",
        )
