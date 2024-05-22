"""HAuth wrapper for FastAPI application."""
import typing
import pathlib

try:
    from fastapi import FastAPI, Depends
    from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
except ImportError:
    _fastapi_installed = False
else:
    _fastapi_installed = True

try:
    from discord.ext.ipc import Client
except ImportError:
    _discord_installed = False
else:
    _discord_installed = True

from ..models import ReqLogin, ReqMMTResult, ReqEmailVerification, Session
from .dependencies import session_dependency, discord_session_dependency
from ..client import HAuth


__all__ = ["HAuthFastAPI", "HAuthDiscord"]


def HAuthFastAPI(
    app: "FastAPI",
    client: HAuth
) -> FastAPI:
    """Initialize HoYoLab Auth for FastAPI app.

    This will attach the necessary routes and HAuth to the FastAPI app.

    Args:
        app (FastAPI): The FastAPI app.
        client (HAuth): The HAuth client.
    """
    if not _fastapi_installed:
        raise ImportError("HAuthFastAPI requires fastapi to be installed: `pip install fastapi`.")

    setattr(app, "hauth", client)

    @app.get(f"{client.config.login_path}/" + "{session_id}")
    async def login(session: typing.Annotated[Session, Depends(session_dependency)]) -> HTMLResponse:
        """Login page route."""
        return HTMLResponse(client._get_login_page(session))

    @app.post(f"{client.config.api_login_path}/" + "{session_id}")
    async def api_login(
        session: typing.Annotated[Session, Depends(session_dependency)],
        data: typing.Union[None, ReqLogin, ReqMMTResult, ReqEmailVerification] = None
    ):
        """API login route."""
        rsp = await client._handle_request(session, data)
        return JSONResponse(rsp.content, status_code=rsp.status_code)

    if not client.config.use_custom_js:
        @app.get(f"{client.config.js_path}")
        async def geetest() -> FileResponse:
            """Geetest JS route."""
            return FileResponse(client.config.js_file_path or pathlib.Path(__file__).parent / "../assets/js.js")

    return app


def HAuthDiscord(
    app: FastAPI,
    client: HAuth,
    secret_key: str
) -> FastAPI:
    """Initialize HoYoLab Auth for your Discord bot using FastAPI app.

    This will attach the necessary routes and HAuth to the FastAPI app.

    Args:
        app (FastAPI): The FastAPI app.
        client (HAuth): The HAuth client.
        secret_key (str): The secret key for the discord-ipc.
    """
    if not _fastapi_installed:
        raise ImportError("HAuthDiscord requires fastapi to be installed: `pip install fastapi`.")
    if not _discord_installed:
        raise ImportError("HAuthDiscord requires better-ipc to be installed: `pip install better-ipc`.")

    ipc = Client(secret_key=secret_key)

    setattr(app, "hauth", client)
    setattr(app, "ipc", ipc)

    @app.get(f"{client.config.login_path}/" + "{session_id}")
    async def login(session: typing.Annotated[Session, Depends(discord_session_dependency)]) -> HTMLResponse:
        """Login page route."""
        return HTMLResponse(client._get_login_page(session))

    @app.post(f"{client.config.api_login_path}/" + "{session_id}")
    async def api_login(
        session: typing.Annotated[Session, Depends(discord_session_dependency)],
        data: typing.Union[None, ReqLogin, ReqMMTResult, ReqEmailVerification] = None
    ):
        """API login route."""
        rsp = await ipc.request(
            "handle_request",
            session=session.model_dump(mode="json"),
            data=data.model_dump(mode="json") if data else None
        )
        return JSONResponse(rsp.response["content"], status_code=rsp.response["status_code"])

    if not client.config.use_custom_js:
        @app.get(f"{client.config.js_path}")
        async def geetest() -> FileResponse:
            """Geetest JS route."""
            return FileResponse(client.config.js_file_path or pathlib.Path(__file__).parent / "../assets/js.js")

    return app
