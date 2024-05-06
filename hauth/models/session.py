"""Session class."""
import typing
from enum import Enum

import genshin
import pydantic


__all__ = ["State", "PartialSession", "Session"]


class State(Enum):
    """Session state."""

    UNDEFINED = "undefined"
    """The session state is unknown."""

    LOGIN_REQUIRED = "login_required"
    """The user needs to provide their credentials."""

    LOGIN_GEETEST_TRIGGERED = "login_geetest_triggered"
    """Geetest verification is required (on login endpoint)."""

    EMAIL_VERIFICATION_TRIGGERED = "email_verification_triggered"
    """Email verification is required."""

    EMAIL_GEETEST_TRIGGERED = "email_geetest_triggered"
    """Geetest verification is required (on email verification endpoint)."""

    SUCCESS = "success"
    """The user has successfully logged in."""


class PartialSession(pydantic.BaseModel):
    """Partial session class. Used on login page to prevent 
    sensitive data from being exposed to the client.
    """

    id: str
    """ID of the session."""

    state: State
    """State of the session."""

    language: typing.Optional[str] = pydantic.Field(default="en")
    """User's language. Default to `en`."""

    mmt: typing.Optional[genshin.models.SessionMMT] = None
    """MMT required to solve geetest."""

    ticket: typing.Optional[genshin.models.ActionTicket] = None
    """Email verification data."""

    model_config = pydantic.ConfigDict(use_enum_values=True)


class Session(pydantic.BaseModel):
    """Session class."""

    id: str
    """ID of the session."""

    state: State = pydantic.Field(default=State.UNDEFINED)
    """State of the session."""

    arguments: typing.Optional[typing.List[typing.Any]] = None
    """Arguments for the session.

    These are not used by HAuth but you can use them in
    the following callback functions for your own purposes:
    - `on_success` (Config)
    - `on_error` (Config)
    - `on_expire` (Storage)
    """

    language: typing.Optional[str] = pydantic.Field(default="en")
    """User's language. Default to `en`."""

    login: typing.Optional[str] = None
    """User's login."""

    password: typing.Optional[str] = None
    """User's password."""

    mmt: typing.Optional[genshin.models.SessionMMT] = None
    """MMT required to solve geetest."""

    ticket: typing.Optional[genshin.models.ActionTicket] = None
    """Email verification data."""

    expiration_time: typing.Optional[float] = None
    """The expiration time of the session."""

    login_result: typing.Optional[genshin.models.AppLoginResult] = None
    """The login result added to session after successful login."""

    def get_partial(self) -> PartialSession:
        """Get a partial (safe) session."""
        return PartialSession(
            id=self.id,
            state=self.state,
            language=self.language,
            mmt=self.mmt,
            ticket=self.ticket
        )

    model_config = pydantic.ConfigDict(use_enum_values=True)
