# HAuth

HAuth is a simple and user-friendly package for authenticating in HoYoLab API via web interface.

> [!WARNING]
> The library is in early development stage and may contain bugs and security vulnerabilities. Use it at your own risk.

## Installation

With PIP:
```bash
pip install git+https://github.com/JokelBaf/hauth.git
```

## Usage

Here are some examples of how you can use HAuth in your project.

### Simple FastAPI app

The app running on `http://localhost:8000` will redirect you to the login page when you visit the root URL. After logging in, cookies will be printed in the console.

<details>
<summary>Click to see the code</summary>
```python
import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

from hauth import Config, LoginPageStyle, Color, ThemeMode, HAuth, Session
from hauth.storages import MemorySessionsStorage
from hauth.fastapi import HAuthFastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Called when the application starts."""
    await app.hauth.initialize()
    yield

async def on_expire(session: Session) -> None:
    """Called when a session expires."""
    print(f"Session with id {session.id} expired!")

async def on_success(session: Session) -> None:
    """Called when a user logs in."""
    print("User logged in!", session)


app = FastAPI(lifespan=lifespan)

page_style = LoginPageStyle(
    color=Color.GREEN,
    theme_mode=ThemeMode.LIGHT
)
config = Config(on_success=on_success, login_page_style=page_style)

storage = MemorySessionsStorage(
    on_expire=on_expire,
    ttl=60*5,
    cleanup_interval=1
)

client = HAuth(storage=storage, config=config)

app = HAuthFastAPI(app, client)


@app.get("/")
async def root() -> RedirectResponse:
    """Redirects to the login page."""
    session = await app.hauth.create_session({})
    return RedirectResponse(url=f"/login/{session.id}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```
</details>

### Simple AIOHTTP app

Same as the FastAPI example, but with AIOHTTP and some small differences like `on_error` callback.

<details>
<summary>Click to see the code</summary>
```python
from aiohttp import web

from hauth import Config, LoginPageStyle, Color, ThemeMode, HAuth, Session
from hauth.storages import MemorySessionsStorage
from hauth.aiohttp import HAuthAiohttp


async def on_startup(app: web.Application) -> None:
    """Called when the application starts."""
    await app.hauth.initialize()


async def on_error(session: Session, e: Exception) -> None:
    """Called when an error occurs during login process."""
    print(f"There was an error during login process. Session: {session.id}, Error: {e}")

async def on_success(session: Session) -> None:
    """Called when a user logs in."""
    print("User logged in!", session)


app = web.Application()
app.on_startup.append(on_startup)

page_style = LoginPageStyle(
    color=Color.BLUE,
    theme_mode=ThemeMode.DARK
)
config = Config(
    on_success=on_success,
    on_error=on_error,
    login_page_style=page_style
)

storage = MemorySessionsStorage(
    ttl=None,  # Does not expire
    cleanup_interval=2
)

client = HAuth(storage=storage, config=config)
app = HAuthAiohttp(app, client)

async def root(request: web.Request) -> web.HTTPMovedPermanently:
    """Redirects to the login page."""
    session = await app.hauth.create_session({})
    return web.HTTPMovedPermanently(f"/login/{session.id}")

app.add_routes([web.get("/", root)])

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8000)
```
</details>

### Discord.py bot + FastAPI

It is recommended to use IPC for Discord bots, that's why HAuth provides built-in support for it. However, you will need to split the bot and the web server into two separate processes.
<details>
<summary>Bot</summary>
```python
import logging
import typing

import discord
from discord.ext import commands, ipc
from discord.ext.ipc.server import Server
from discord.ext.ipc.objects import ClientPayload
from hauth import Config, HAuth, Session
from hauth.storages import MemorySessionsStorage
from hauth.modules.utility import request_data_to_model


logger = logging.getLogger("discord")

# First let's configure HAuth client

async def on_expire(session: Session) -> None:
    """Called when a session expires."""
    logger.info(f"Session with id {session.id} expired!")

    channel = bot.get_channel(session.data["message"]["channel_id"])
    message = await channel.fetch_message(session.data["message"]["id"])
    await message.edit(content="Session expired!", view=None)

async def on_success(session: Session) -> None:
    """Called when a user logs in."""
    logger.info(f"User with ID {session.data["user"]["id"]} logged in!")

    channel = bot.get_channel(session.data["message"]["channel_id"])
    message = await channel.fetch_message(session.data["message"]["id"])
    await message.edit(content="Logged in successfully!", view=None)

config = Config(on_success=on_success)

storage = MemorySessionsStorage(
    on_expire=on_expire,
    ttl=20,
    cleanup_interval=1
)
client = HAuth(storage=storage, config=config)

# Now we setup and run the bot

class Bot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()

        super().__init__(
            command_prefix="!",
            intents=intents,
        )

        self.hauth = client
        self.ipc = ipc.Server(self, secret_key="secret_key")

    async def setup_hook(self) -> None:
        """Called when the bot is ready."""
        await self.hauth.initialize()
        await self.ipc.start()

    @Server.route()
    async def get_session(self, payload: ClientPayload) -> typing.Dict:
        """Deliver session data to the client."""
        session = await self.hauth.get_session(payload.session_id)
        return session.model_dump(mode="json") if session else None

    @Server.route()
    async def handle_request(self, payload: ClientPayload) -> typing.Dict:
        """Handle requests from the client."""
        model = request_data_to_model(payload.data["data"])
        rsp = await self.hauth._handle_request(Session(**payload.session), model)
        return rsp.model_dump(mode="json")

bot = Bot()

@bot.event
async def on_ready() -> None:
    """Called when the bot is ready."""
    logger.info(f"Logged in as {bot.user} ({bot.user.id})")
    await bot.tree.sync()

@bot.tree.command(name="login", description="Login with HoYoLab")
async def login(i: discord.Interaction) -> None:
    """HoYoLab login command."""
    session = await i.client.hauth.create_session({
        "user": {
            "id": i.user.id
        },
        "message": {
            "id": None,
            "channel_id": i.channel.id
        }
    })

    view = discord.ui.View()
    button = discord.ui.Button(
        style=discord.ButtonStyle.url,
        label="Login with HoYoLab",
        url=f"http://localhost:8000/login/{session.id}"
    )
    view.add_item(button)

    await i.response.send_message("Click the button below to login.", view=view)
    msg = await i.original_response()

    session.data["message"]["id"] = msg.id
    await i.client.hauth.update_session(session.id, session)

bot.run("TOKEN")
```
</details>
<details>
<summary>Web server</summary>
```python
import uvicorn
import fastapi
from hauth import Config, HAuth, LoginPageStyle, ThemeMode, Color
from hauth.storages import MemorySessionsStorage
from hauth.fastapi import HAuthDiscord

app = fastapi.FastAPI()

page_style = LoginPageStyle(
    color=Color.GREEN,
    theme_mode=ThemeMode.LIGHT
)
config = Config(page_style=page_style)
client = HAuth(
    storage=MemorySessionsStorage(),  # Won't be used here but still required
    config=config
)
app = HAuthDiscord(app, client, "secret_key")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```
</details>
