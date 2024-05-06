"""In-memory sessions storage."""
import abc
import typing

import genshin

from ..models import Session


class SessionsStorage(abc.ABC):
    """Sessions storage."""

    ttl: float
    """The TTL for sessions in seconds."""
    
    on_expire: typing.Optional[typing.Callable[[Session], typing.Awaitable[None]]]
    """A callback function that is called when session expires."""
    
    session_id_length: int
    """The length of randomly generated ID of each session."""
    
    cleanup_interval: float
    """The interval in seconds to clean up expired sessions."""
    
    initialized: bool = False
    """Whether the storage is initialized."""

    @abc.abstractmethod
    async def _cleanup_expired_sessions(self) -> None:
        """Coroutine function to clean up expired items."""

    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initialize the storage.
        
        The function must be called before or after app startup.
        """

    @abc.abstractmethod
    async def get_session(self, id: str) -> typing.Union[Session, None]:
        """Get session from the storage.
        
        Args:
            id (str): The ID of the session.
        """

    @abc.abstractmethod
    async def _generate_id(self) -> str:
        """Generate a new random session ID."""

    @abc.abstractmethod
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
        """Create a new session in the storage.

        Args:
            data (typing.Optional[typing.Dict[typing.Any, typing.Any]]): Dict containing unique data for this session.
            language (typing.Optional[str]): User's language.
            login (typing.Optional[str]): User's login.
            password (typing.Optional[str]): User's password.
            mmt (typing.Optional[genshin.models.SessionMMT]): Geetest data.
            ticket (typing.Optional[genshin.models.ActionTicket]): Email verification data.
            login_result (typing.Optional[genshin.models.AppLoginResult]): The login result added to session after successful login.
        """

    @abc.abstractmethod
    async def update_session(self, id: str, session: Session) -> None:
        """Update a session in the storage.
        
        Args:
            id (str): The ID of the session.
            session (Session): The new session object.
        """

    @abc.abstractmethod
    async def delete_session(self, id: str) -> None:
        """Delete a session from the storage.
        
        Args:
            id (str): The ID of the session.
        """
