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

The app running on localhost:8000 will redirect you to the login page when you visit the root URL (`/`). After logging in, cookies will be printed in the console.

```python
import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

from hauth import Config, LoginPageStyle, Color, ThemeMode, HAuth
from hauth.storages import MemorySessionsStorage
from hauth.fastapi import HAuthFastAPI


@asynccontextmanager
async def lifespan(app: HAuthFastAPI):
    await app.hauth.initialize()
    yield

async def on_expire(session):
    print("Session expired!")

async def on_success(session):
    print("User logged in!", session)


app = FastAPI(lifespan=lifespan)

config = Config(on_success=on_success, login_page_style=LoginPageStyle(color=Color.GREEN, theme_mode=ThemeMode.LIGHT))
storage = MemorySessionsStorage(
    on_expire=on_expire,
    ttl=60*5,
    cleanup_interval=1
)
client = HAuth(storage=storage, config=config)

app = HAuthFastAPI(app, client)


@app.get("/")
async def root():
    session = await app.hauth.create_session({})
    return RedirectResponse(url=f"/login/{session.id}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```