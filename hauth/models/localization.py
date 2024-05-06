"""Localization classes for HoYoLab Auth."""
import typing

import pydantic


__all__ = ["Localization"]


class Localization(pydantic.BaseModel):
    """Localization class for HoYoLab Auth."""

    default_error_title: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Something went wrong",
        "ru": "Что-то пошло не так"
    })
    """Default error title. Shown when server returns an error without details."""

    default_error_message: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Unexpected error occurred when requesting the server. Status - ||status||.",
        "ru": "При выполнение запроса произошла непредвиденная ошибка. Статус - ||status||."
    })
    """"Default error description. Shown when server returns an error without details."""

    login_page_title: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Login page",
        "ru": "Страница входа"
    })
    """Login page title."""

    close: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Close",
        "ru": "Закрыть"
    })
    """Close button text."""

    login_title: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Login with HoYoLab",
        "ru": "Вход через HoYoLab"
    })
    """Title for the login form."""

    login_description: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "<span>Note:</span> We are not affiliated with HoYoLab.",
        "ru": "<span>Обратите внимание:</span> Мы не связаны с HoYoLab."
    })
    """Hint for the login form."""

    email: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Email",
        "ru": "Почта"
    })
    """Email field label."""

    password: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Password",
        "ru": "Пароль"
    })
    """Password field label."""

    login: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Login",
        "ru": "Войти"
    })
    """Login button text."""

    email_verification_title: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Email verification",
        "ru": "Проверка почты"
    })
    """Email verification title. Shown on login page when email verification is triggered."""

    email_verification_description: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Enter the code sent to your email.",
        "ru": "Введите код, отправленный вам на почту."
    })
    """Email verification description. Shown on login page when email verification is triggered."""

    complete_title: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Authorized",
        "ru": "Авторизован"
    })
    """Title shown on login page when the user is authorized."""

    complete_description: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Redirecting you in ||seconds|| seconds...",
        "ru": "Перенаправление через ||seconds|| секунд..."
    })
    """Description shown on login page when the user is authorized."""

    complete_description_no_callback: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "You can now close this window.",
        "ru": "Вы можете закрыть это окно."
    })
    """Description shown on login page when the user is authorized and callback url is not set."""

    fields_empty: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Some fields are empty.",
        "ru": "Некоторые поля пустые."
    })
    """Error message shown on login page when some fields are empty."""

    invalid_request_body_title: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Invalid request body.",
        "ru": "Неверное тело запроса."
    })
    """Error title sent by API when request body is invalid."""

    invalid_request_body_message: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Request body is invalid. Please report this error to the developer or try again later.",
        "ru": "Некорректное тело запроса. Пожалуйста, сообщите об этой ошибке разработчику или попробуйте позже."
    })
    """Error message sent by API when request body is invalid."""

    login_failed_title: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Login failed.",
        "ru": "Вход не удался."
    })
    """Error title sent by API when login failed (Most likely because of invalid credentials)."""

    login_failed_message: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Could not login into your account. Please check your credentials and try again.",
        "ru": "Не удалось войти в аккаунт. Пожалуйста, проверьте ваши данные и попробуйте снова."
    })
    """Error message sent by API when login failed (Most likely because of invalid credentials)."""

    email_verification_failed_title: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Email verification failed.",
        "ru": "Проверка почты не удалась."
    })
    """Error title sent by API when email verification failed (Most likely because of invalid code)."""

    email_verification_failed_message: typing.Mapping[str, str] = pydantic.Field(default={
        "en": "Could not verify your email. Please check the code and try again.",
        "ru": "Не удалось проверить вашу почту. Пожалуйста, проверьте код и попробуйте снова."
    })
    """Error message sent by API when email verification failed (Most likely because of invalid code)."""

    model_config = pydantic.ConfigDict(extra="allow")
    """Allows to add any custom localization fields."""
