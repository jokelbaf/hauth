"""Dependencies for FastAPI routes."""
try:
    from fastapi import Request, HTTPException
except ImportError:
    pass  # No need to check this since it is already checked in core.py

from ..models import Session


__all__ = ["session_dependency", "discord_session_dependency"]


async def session_dependency(request: Request, session_id: str) -> Session:
    """Dependency to get session by ID."""
    session = await request.app.hauth.storage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404)
    return session

async def discord_session_dependency(request: Request, session_id: str) -> Session:
    """Dependency to get session from discord Bot by ID."""
    rsp = await request.app.ipc.request("get_session", session_id=session_id)
    if not rsp.response:
        raise HTTPException(status_code=404)
    return Session(**rsp.response)
