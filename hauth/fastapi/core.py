"""HAuth wrapper for FastAPI application."""
import typing
import pathlib

from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

from ..models import ReqLogin, ReqMMTResult, ReqEmailVerification, Session
from .dependencies import session_dependency
from ..client import HAuth


__all__ = ["HAuthFastAPI"]


def HAuthFastAPI(
    app: FastAPI,
    client: HAuth
) -> FastAPI:
    """Initialize HoYoLab Auth for FastAPI app.

    This will attach the necessary routes and HAuth to the FastAPI app.

    Args:
        app (FastAPI): The FastAPI app.
        client (HAuth): The HAuth client.
    """
    setattr(app, "hauth", client)

    @app.get(f"{client.config.login_path}/" + "{session_id}")
    async def login(session: typing.Annotated[Session, Depends(session_dependency)]) -> HTMLResponse:
        """Login page route."""
        return HTMLResponse(app.hauth._get_login_page(session))

    @app.post(f"{client.config.api_login_path}/" + "{session_id}")
    async def api_login(
        session: typing.Annotated[Session, Depends(session_dependency)],
        data: typing.Union[None, ReqLogin, ReqMMTResult, ReqEmailVerification] = None
    ):
        """API login route."""
        rsp = await app.hauth._handle_request(session, data)
        return JSONResponse(rsp.content, status_code=rsp.status_code)

    if not client.config.use_custom_js:
        @app.get(f"{client.config.js_path}")
        async def geetest() -> FileResponse:
            """Geetest JS route."""
            return FileResponse(client.config.js_file_path or pathlib.Path(__file__).parent / "../assets/js.js")

    return app
