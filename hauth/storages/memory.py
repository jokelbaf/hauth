"""In-memory sessions storage."""
import asyncio
import random
import string
import time
import typing

import genshin

from ..models import Session


class MemorySessionsStorage:
    """In-memory sessions storage."""

    def __init__(
        self, 
        on_expire: typing.Optional[typing.Callable[[Session], typing.Awaitable[None]]] = None,
        *,
        ttl: typing.Optional[float] = 60 * 5,
        session_id_length: typing.Optional[int] = 10,
        cleanup_interval: typing.Optional[float] = 0.5
    ) -> None:
        """
        Initialize SessionStorage with the following parameters.

        Args:
            on_expire (typing.Optional[typing.Callable[[Session], typing.Awaitable[None]]]): A callback function that is called when session expires.
            ttl (typing.Optional[float]): The TTL for sessions in seconds.
            session_id_length (typing.Optional[int]): The length of randomly generated ID of each session.
            cleanup_interval (typing.Optional[float]): The interval in seconds to clean up expired sessions.
        """
        self.ttl = ttl
        """The TTL for sessions in seconds."""
        self.on_expire = on_expire
        """A callback function that is called when session expires."""
        self.session_id_length = session_id_length
        """The length of randomly generated ID of each session."""
        self.cleanup_interval = cleanup_interval
        """The interval in seconds to clean up expired sessions."""
        self._storage: typing.Mapping[str, Session] = {}
        """The in-memory storage for the sessions."""

    async def _cleanup_expired_sessions(self) -> None:
        """Coroutine function to clean up expired items."""
        while True:
            expired_keys = [
                key for key, session in self._storage.items() 
                if session.expiration_time is not None and time.time() > session.expiration_time
            ]
            for key in expired_keys:
                session = self._storage.pop(key)
                if self.on_expire:
                    await self.on_expire(session)
            await asyncio.sleep(self.cleanup_interval)

    async def initialize(self) -> None:
        """Initialize the storage.
        
        The function must be called before or after app startup.
        """
        asyncio.create_task(self._cleanup_expired_sessions())

    async def get_session(self, id: str) -> typing.Union[Session, None]:
        """Get session from the storage.
        
        Args:
            id (str): The ID of the session.
        """
        return self._storage.get(id, None)

    async def _generate_id(self) -> str:
        """Generate a new random session ID."""
        chars = string.ascii_letters + string.digits
        existing_ids = set(self._storage.keys())

        while True:
            new_id = "".join(random.choices(chars, k=self.session_id_length))
            if new_id not in existing_ids:
                return new_id

    async def create_session(
        self, 
        arguments: typing.Optional[typing.List[typing.Any]] = None,
        language: typing.Optional[str] = "en",
        login: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        mmt: typing.Optional[genshin.models.SessionMMT] = None,
        ticket: typing.Optional[genshin.models.ActionTicket] = None
    ) -> Session:
        """Create a new session in the storage.

        Args:
            arguments (typing.Optional[typing.List[typing.Any]]): Arguments for the session.
            login (typing.Optional[str]): User's login.
            password (typing.Optional[str]): User's password.
            mmt (typing.Optional[genshin.models.SessionMMT]): Geetest data.
            ticket (typing.Optional[genshin.models.ActionTicket]): Email verification data.
        """
        sid = await self._generate_id()
        session = Session(
            id=sid,
            arguments=arguments,
            language=language,
            login=login,
            password=password,
            mmt=mmt,
            ticket=ticket,
            expiration_time=(time.time() + self.ttl) if self.ttl else None,
        )
        self._storage[sid] = session
        return session

    async def update_session(self, id: str, session: Session) -> None:
        """Update a session in the storage.
        
        Args:
            id (str): The ID of the session.
            session (Session): The new session object.
        """
        self._storage[id] = session

    async def delete_session(self, id: str) -> None:
        """Delete a session from the storage.
        
        Args:
            id (str): The ID of the session.
        """
        if id in self._storage:
            del self._storage[id]
