"""Models that are used to represent the request data."""
import typing

import genshin
import pydantic


__all__ = ["ReqMMTResult", "ReqEmailVerification", "ReqLogin", "JSONResponse"]


class ReqMMTResult(pydantic.BaseModel):
    """Model containing solved geetest data."""

    mmt_result: genshin.models.SessionMMTResult
    """Solve geetest data."""


class ReqEmailVerification(pydantic.BaseModel):
    """Model containing email verification data."""

    code: str
    """Verification data."""


class ReqLogin(pydantic.BaseModel):
    """Model containing login data."""

    account: str
    """Encrypted user's account. Can be either email or username."""

    password: str
    """Encrypted user's password."""


class JSONResponse(pydantic.BaseModel):
    """Represents JSON response from HAuth."""

    status_code: int
    """Status code."""

    content: typing.Dict[str, typing.Any]
    """Response content, dictionary."""