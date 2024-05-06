"""HoYoLab Auth main class."""
import asyncio
import typing
from pathlib import Path

import genshin

from .models.request import JSONResponse, ReqLogin, ReqMMTResult, ReqEmailVerification
from .storages.memory import MemorySessionsStorage
from .modules.geetest import get_lang_from_language
from .models.session import Session, State
from .modules.fprocessor import process
from .models.config import Config


__all__ = ["HAuth"]


class HAuth:
    """HoYoLab Auth main class."""

    def __init__(
        self, 
        storage: typing.Union[MemorySessionsStorage],
        config: Config
    ) -> None:
        self.config = config
        """Configuration for HoYoLab Auth."""
        self.storage = storage
        """Session storage."""

    def _get_login_page(self, session: Session) -> str:
        """Process HTML with HoYoLab Auth."""
        partial_session = session.get_partial()
        return process(
            self.config.login_page_path or Path(__file__).parent.joinpath("assets/login.html"),
            session.language,
            self.config.localization,
            js_path=self.config.js_path,
            api_login_path=self.config.api_login_path,
            callback_url=self.config.callback_url or "",
            session=partial_session.model_dump_json(),
            color=self.config.login_page_style.color.value,
            theme_mode=self.config.login_page_style.theme_mode.value,
            geetest_lang=get_lang_from_language(session.language),
        )

    async def _define_session_state(self, session: Session) -> None:
        """Define the state of the session.

        Args:
            session (Session): The session to define the state for.
        """
        if session.state == State.UNDEFINED:
            if session.login and session.password:
                await self._login_session(session)
            else:
                session.state = State.LOGIN_REQUIRED

    async def _login_session(
        self,
        session: Session,
        *,
        mmt_result: typing.Optional[genshin.models.SessionMMTResult] = None,
        ticket: typing.Optional[genshin.models.ActionTicket] = None
    ) -> None:
        """Try to login the user."""
        try:
            client = genshin.Client()
            result = await client._app_login(session.login, session.password, encrypted=True, mmt_result=mmt_result, ticket=ticket)

            if isinstance(result, genshin.models.SessionMMT):
                session.state = State.LOGIN_GEETEST_TRIGGERED
                session.mmt = result
            elif isinstance(result, genshin.models.ActionTicket):
                session.state = State.EMAIL_VERIFICATION_TRIGGERED
                session.ticket = result
            else:
                session.login_result = result
                session.state = State.SUCCESS
        except genshin.GenshinException:
            session.state = State.LOGIN_REQUIRED

    async def _email_verify_session(
        self,
        session: Session,
        *,
        code: str,
        ticket: genshin.models.ActionTicket
    ) -> bool:
        """Try to verify the email. Returns `True` on success, `False` otherwise."""
        try:
            client = genshin.Client()
            await client._verify_email(code, ticket)
            return True
        except genshin.GenshinException:
            session.state = State.EMAIL_VERIFICATION_TRIGGERED
            return False

    async def _handle_request(
        self,
        session: Session,
        data: typing.Union[None, ReqLogin, ReqMMTResult, ReqEmailVerification] = None
    ) -> JSONResponse:
        """Handle the request. This can be used to process the request from any framework."""
        try:
            if session.state == State.UNDEFINED:
                await self._define_session_state(session)

                if session.state == State.SUCCESS and self.config.on_success:
                    asyncio.create_task(self.config.on_success(session))
                    await self.delete_session(session.id)

            if not data:
                # Client does not know the state of the session
                return JSONResponse(status_code=200, content=session.get_partial().model_dump())

            if session.state == State.LOGIN_REQUIRED:
                if not isinstance(data, ReqLogin):
                    return JSONResponse(
                        status_code=422, 
                        content={
                            "error": {
                                "title": self.config.localization.invalid_request_body_title[session.language],
                                "message": self.config.localization.invalid_request_body_message[session.language]
                            }
                        }
                    )
                session.login = data.login
                session.password = data.password

                await self._login_session(session)

                if session.state == State.LOGIN_REQUIRED:
                    # Login failed
                    return JSONResponse(
                        status_code=200, 
                        content={
                            "error": {
                                "title": self.config.localization.login_failed_title[session.language],
                                "message": self.config.localization.login_failed_message[session.language]
                            }
                        }
                    )

            elif session.state == State.LOGIN_GEETEST_TRIGGERED:
                if not isinstance(data, ReqMMTResult):
                    return JSONResponse(
                        status_code=422, 
                        content={
                            "error": {
                                "title": self.config.localization.invalid_request_body_title[session.language],
                                "message": self.config.localization.invalid_request_body_message[session.language]
                            }
                        }
                    )
                await self._login_session(session, mmt_result=data.mmt_result)

                if session.state == State.LOGIN_REQUIRED:
                    # Login failed
                    return JSONResponse(
                        status_code=200, 
                        content={
                            "error": {
                                "title": self.config.localization.login_failed_title[session.language],
                                "message": self.config.localization.login_failed_message[session.language]
                            }
                        }
                    )

            elif session.state == State.EMAIL_VERIFICATION_TRIGGERED:
                if not isinstance(data, ReqEmailVerification):
                    return JSONResponse(
                        status_code=422, 
                        content={
                            "error": {
                                "title": self.config.localization.invalid_request_body_title[session.language],
                                "message": self.config.localization.invalid_request_body_message[session.language]
                            }
                        }
                    )
                email_verified = await self._email_verify_session(
                    session, 
                    code=data.code, 
                    ticket=session.ticket
                )
                if not email_verified:
                    # Verification failed
                    return JSONResponse(
                        status_code=200, 
                        content={
                            "error": {
                                "title": self.config.localization.email_verification_failed_title[session.language],
                                "message": self.config.localization.email_verification_failed_message[session.language]
                            }
                        }
                    )
                await self._login_session(session, ticket=session.ticket)

            elif session.state == State.EMAIL_GEETEST_TRIGGERED:
                if not isinstance(data, ReqMMTResult):
                    return JSONResponse(
                        status_code=422, 
                        content={
                            "error": {
                                "title": self.config.localization.invalid_request_body_title[session.language],
                                "message": self.config.localization.invalid_request_body_message[session.language]
                            }
                        }
                    )
                email_verified = await self._email_verify_session(
                    session,
                    mmt_result=data.mmt_result,
                    ticket=session.ticket
                )
                if not email_verified:
                    # Verification failed
                    return JSONResponse(
                        status_code=200, 
                        content={
                            "error": {
                                "title": self.config.localization.email_verification_failed_title[session.language],
                                "message": self.config.localization.email_verification_failed_message[session.language]
                            }
                        }
                    )

            if session.state == State.SUCCESS and self.config.on_success:
                asyncio.create_task(self.config.on_success(session))
                await self.delete_session(session.id)

            return JSONResponse(status_code=200, content=session.get_partial().model_dump())

        except Exception as e:
            if self.config.on_error:
                asyncio.create_task(self.config.on_error(session, e))
            raise e

    async def initialize(self) -> None:
        """Initialize HoYoLab Auth."""
        await self.storage.initialize()

    async def create_session(
        self,
        arguments: typing.Optional[typing.List[typing.Any]],
        language: typing.Optional[str] = "en",
        login: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        mmt: typing.Optional[genshin.models.SessionMMT] = None,
        ticket: typing.Optional[genshin.models.ActionTicket] = None
    ) -> Session:
        """Create a new session.

        Args:
            arguments (typing.Optional[typing.List[typing.Any]]): Arguments for the session.
            login (typing.Optional[str]): User's login.
            password (typing.Optional[str]): User's password.
            mmt (typing.Optional[genshin.models.SessionMMT]): Geetest data.
            ticket (typing.Optional[genshin.models.ActionTicket]): Email verification data.
        """
        return await self.storage.create_session(arguments, language, login, password, mmt, ticket)

    async def update_session(self, id: str, session: Session) -> None:
        """Update a session.
        
        Args:
            id (str): The ID of the session.
            session (Session): The new session object.
        """
        await self.storage.update_session(id, session)

    async def delete_session(self, id: str) -> None:
        """Delete a session.
        
        Args:
            id (str): The ID of the session.
        """
        await self.storage.delete_session(id)
