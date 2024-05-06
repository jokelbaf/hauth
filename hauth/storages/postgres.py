import asyncio
import asyncpg
import datetime
import json
import random
import string
import typing

import genshin

from ..models import Session, State
from . import SessionsStorage


__all__ = ["PostgresSessionsStorage"]


class PostgresSessionsStorage(SessionsStorage):
    """PostgreSQL sessions storage."""

    def __init__(
        self,
        dns: str,
        on_expire: typing.Optional[typing.Callable[[Session], typing.Awaitable[None]]] = None,
        *,
        ttl: typing.Optional[float] = 60 * 5,
        session_id_length: typing.Optional[int] = 10,
        cleanup_interval: typing.Optional[float] = 0.5
    ) -> None:
        """Initialize PostgresSessionsStorage with the following parameters.

        Args:
            dns (str): Connection arguments specified using as a single string in the libpq connection URI format.
            on_expire (typing.Optional[typing.Callable[[Session], typing.Awaitable[None]]]): A callback function that is called when session expires.
            ttl (typing.Optional[float]): The TTL for sessions in seconds.
            session_id_length (typing.Optional[int]): The length of randomly generated ID of each session.
            cleanup_interval (typing.Optional[float]): The interval in seconds to clean up expired sessions.
        """
        self.ttl = ttl
        self.on_expire = on_expire
        self.session_id_length = session_id_length
        self.cleanup_interval = cleanup_interval

        self.dns = dns
        """PostgreSQL connection string."""

    async def _cleanup_expired_sessions(self) -> None:
        while True:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    expired_sessions = await conn.fetch(
                        "DELETE FROM sessions WHERE expiration_time < NOW() RETURNING *"
                    )
                    for session in expired_sessions:
                        if self.on_expire:
                            await self.on_expire(Session(**session))
            await asyncio.sleep(self.cleanup_interval)

    async def initialize(self) -> None:
        self.pool = await asyncpg.create_pool(self.dns)
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    state TEXT,
                    data JSONB,
                    language TEXT,
                    login TEXT,
                    password TEXT,
                    mmt JSONB,
                    ticket JSONB,
                    expiration_time TIMESTAMP,
                    login_result JSONB
                )
            """)
        asyncio.create_task(self._cleanup_expired_sessions())
        self.initialized = True

    async def get_session(self, id: str) -> typing.Union[Session, None]:
        async with self.pool.acquire() as conn:
            session = await conn.fetchrow("SELECT * FROM sessions WHERE id = $1", id)
            if session:
                return Session(**session)
            else:
                return None

    async def _generate_id(self) -> str:
        chars = string.ascii_letters + string.digits
        async with self.pool.acquire() as conn:
            while True:
                new_id = "".join(random.choices(chars, k=self.session_id_length))
                session = await conn.fetchrow("SELECT * FROM sessions WHERE id = $1", new_id)
                if not session:
                    return new_id

    async def create_session(
        self,
        data: typing.Optional[typing.Dict[typing.Any, typing.Any]] = None,
        language: typing.Optional[str] = "en",
        login: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        mmt: typing.Optional[genshin.models.SessionMMT] = None,
        ticket: typing.Optional[genshin.models.ActionTicket] = None,
        login_result: typing.Optional[genshin.models.AppLoginResult] = None
    ) -> Session:
        sid = await self._generate_id()
        async with self.pool.acquire() as conn:
            created_session = await conn.fetchrow(
                """INSERT INTO sessions (
                    id, state, data, language, login, password, mmt, ticket, expiration_time, login_result
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, NOW() + INTERVAL '1 second' * $9, $10
                ) RETURNING *""",
                sid,
                State.UNDEFINED.value,
                json.dumps(data) if data else None,
                language,
                login,
                password,
                mmt.model_dump_json() if mmt else None,
                ticket.model_dump_json() if ticket else None,
                self.ttl,
                login_result.model_dump_json() if login_result else None,
            )
            return Session(**created_session)

    async def update_session(self, id: str, session: Session) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """UPDATE sessions SET
                    state = $1,
                    data = $2,
                    language = $3,
                    login = $4,
                    password = $5,
                    mmt = $6,
                    ticket = $7,
                    expiration_time = $8,
                    login_result = $9
                WHERE id = $10""",
                session.state.value,
                json.dumps(session.data) if session.data else None,
                session.language,
                session.login,
                session.password,
                session.mmt.model_dump_json() if session.mmt else None,
                session.ticket.model_dump_json() if session.ticket else None,
                datetime.datetime.fromtimestamp(session.expiration_time) if session.expiration_time else None,
                session.login_result.model_dump_json() if session.login_result else None,
                id,
            )

    async def delete_session(self, id: str) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM sessions WHERE id = $1", id)
