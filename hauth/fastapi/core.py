"""HAuth wrapper for FastAPI application."""
import typing
import pathlib

from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

from ..models import ReqLogin, ReqMMTResult, ReqEmailVerification, Session, Config
from ..storages import MemorySessionsStorage
from .dependencies import session_dependency
from ..client import HAuth


__all__ = ["HAuthFastAPI"]


def HAuthFastAPI(
    app: FastAPI,
    session_storage: MemorySessionsStorage,
    config: typing.Optional[Config] = Config(),
) -> FastAPI:
    """Initialize HoYoLab Auth for FastAPI app.

    This will attach the necessary routes and HAuth to the FastAPI app.

    Args:
        app (FastAPI): The FastAPI app.
        session_storage (MemorySessionsStorage): The session storage.
        hauth_config (typing.Optional[Config], optional): The configuration for HoYoLab Auth.
    """
    app.state.hauth = HAuth(session_storage, config)

    @app.get(f"{config.login_path}/" + "{session_id}")
    async def login(session: typing.Annotated[Session, Depends(session_dependency)]) -> HTMLResponse:
        return HTMLResponse(app.state.hauth._get_login_page(session))

    @app.post(f"{config.api_login_path}/" + "{session_id}")
    async def api_login(
        session: typing.Annotated[Session, Depends(session_dependency)],
        data: typing.Union[None, ReqLogin, ReqMMTResult, ReqEmailVerification] = None
    ):
        rsp = await app.state.hauth._handle_request(session, data)
        return JSONResponse(rsp.content, status_code=rsp.status_code)

    if not config.use_custom_js:
        @app.get(f"{config.js_path}")
        async def geetest() -> FileResponse:
            return FileResponse(config.js_file_path or pathlib.Path(__file__).parent / "../assets/js.js")

    return app
