import pathlib

from aiohttp import web
from aiohttp.web_exceptions import HTTPUnprocessableEntity

try:
    from discord.ext.ipc import Client
except ImportError:
    _discord_installed = False
else:
    _discord_installed = True

from ..modules.utility import request_data_to_model
from .dependencies import session_dependency, discord_session_dependency
from ..client import HAuth


__all__ = ["HAuthAiohttp", "HAuthDiscord"]


def HAuthAiohttp(
    app: web.Application,
    client: HAuth
) -> web.Application:
    """Initialize HoYoLab Auth for aiohttp app.

    This will attach the necessary routes and HAuth to the aiohttp app.

    Args:
        app (web.Application): The aiohttp app.
        client (HAuth): The HAuth client.
    """
    setattr(app, "hauth", client)
    routes = web.RouteTableDef()

    @routes.get(f"{client.config.login_path}/{{session_id}}")
    async def login(request: web.Request) -> web.Response:
        """Login page route."""
        session = await session_dependency(request)
        return web.Response(text=client._get_login_page(session), content_type="text/html")

    @routes.post(f"{client.config.api_login_path}/{{session_id}}")
    async def api_login(request: web.Request) -> web.Response:
        """API login route."""
        session = await session_dependency(request)

        data = await request.json() if request.can_read_body else None
        try:
            data = request_data_to_model(data)
        except Exception:
            raise HTTPUnprocessableEntity()

        rsp = await client._handle_request(session, data)
        return web.json_response(rsp.content, status=rsp.status_code)

    if not client.config.use_custom_js:
        @routes.get(f"{client.config.js_path}")
        async def geetest(request: web.Request) -> web.FileResponse:
            """Geetest JS route."""
            return web.FileResponse(client.config.js_file_path or pathlib.Path(__file__).parent / "../assets/js.js")

    app.add_routes(routes)
    return app


def HAuthDiscord(
    app: web.Application,
    client: HAuth,
    secret_key: str
) -> web.Application:
    """Initialize HoYoLab Auth for aiohttp app with Discord.

    This will attach the necessary routes and HAuth to the aiohttp app.

    Args:
        app (web.Application): The aiohttp app.
        client (HAuth): The HAuth client.
        secret_key (str): The secret key for the discord-ipc.
    """
    if not _discord_installed:
        raise ImportError("HAuthDiscord requires better-ipc to be installed: `pip install better-ipc`.")

    ipc = Client(secret_key=secret_key)

    setattr(app, "hauth", client)
    setattr(app, "ipc", ipc)

    routes = web.RouteTableDef()

    @routes.get(f"{client.config.login_path}/{{session_id}}")
    async def login(request: web.Request) -> web.Response:
        """Login page route."""
        session = await discord_session_dependency(request)
        return web.Response(text=client._get_login_page(session), content_type="text/html")

    @routes.post(f"{client.config.api_login_path}/{{session_id}}")
    async def api_login(request: web.Request) -> web.Response:
        """API login route."""
        session = await discord_session_dependency(request)

        data = await request.json() if request.can_read_body else None
        try:
            data = request_data_to_model(data)
        except Exception:
            raise HTTPUnprocessableEntity()

        rsp = await ipc.request(
            "handle_request",
            session=session.model_dump(mode="json"),
            data=data.model_dump(mode="json") if data else None
        )
        return web.json_response(rsp.response["content"], status=rsp.response["status_code"])

    if not client.config.use_custom_js:
        @routes.get(f"{client.config.js_path}")
        async def geetest(request: web.Request) -> web.FileResponse:
            """Geetest JS route."""
            return web.FileResponse(client.config.js_file_path or pathlib.Path(__file__).parent / "../assets/js.js")

    app.add_routes(routes)
    return app
