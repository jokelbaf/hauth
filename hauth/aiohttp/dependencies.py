from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound

from ..models import Session


__all__ = ["session_dependency"]


async def session_dependency(request: web.Request) -> Session:
    """Dependency to get session by ID."""
    session_id = request.match_info["session_id"]
    session = await request.app.hauth.storage.get_session(session_id)
    if not session:
        raise HTTPNotFound()
    return session
