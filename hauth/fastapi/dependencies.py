"""Dependencies for FastAPI routes."""
from fastapi import Request, HTTPException

from ..models import Session


__all__ = ["session_dependency"]


async def session_dependency(request: Request, session_id: str) -> Session:
    """Dependency to get session by ID."""
    session = await request.app.state.hauth.storage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404)
    return session
