"""Configuration for HoYoLab Auth."""
import typing
from enum import Enum

import pydantic

from .session import Session
from .localization import Localization


__all__ = ["Config", "Color", "ThemeMode", "LoginPageStyle"]


class Color(Enum):
    """Color for the login page."""

    RED = "red"
    PINK = "pink"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    PURPLE = "purple"
    ORANGE = "orange"


class ThemeMode(Enum):
    """Theme mode for the login page."""

    DARK = "dark"
    AUTO = "auto"
    LIGHT = "light"


class LoginPageStyle(pydantic.BaseModel):
    """Style for the login page."""

    color: typing.Optional[Color] = pydantic.Field(default=Color.BLUE)
    """Accent color for the login page."""

    theme_mode: typing.Optional[ThemeMode] = pydantic.Field(default=ThemeMode.AUTO)
    """Theme mode for the login page."""


class Config(pydantic.BaseModel):
    """Configuration for HoYoLab Auth."""

    on_success: typing.Optional[typing.Callable[[Session], typing.Awaitable[None]]] = None
    """A callback function that is called when user logs in."""

    on_error: typing.Optional[typing.Callable[[Session, Exception], typing.Awaitable[None]]] = None
    """A callback function that is called when unpredicted error occurs during login process.
    
    This function may be called more than once for a single session (if user tries to login multiple times).
    """

    ttl: typing.Optional[float] = 60 * 5
    """How long does a single session lasts."""

    login_path: typing.Optional[str] = "/login"
    """Path for login page. The structure of the url is `{login_path}/{session_id}`"""

    api_login_path: typing.Optional[str] = "/api/login"
    """Path for login API **websocket**. 

    The structure of the url is `ws(s):{host}:{port}/{api_login_path}/{session_id}`
    """

    js_path: typing.Optional[str] = "/js.js"
    """Path to file with JS code required for a login page."""

    js_file_path: typing.Optional[str] = None
    """Path to your file with JS code required for the login page. 
    If not provided, the default file will be used.

    Note that this file should contain JS for libs only.
    Any other JS code should be included in the login page itself.

    The default file contains these two libs:
    - Geetest - [CDN](https://static.geetest.com/static/js/gt.0.5.0.js)
    - JSEncrypt - [NPM](https://www.npmjs.com/package/jsencrypt) | 
                  [CDN](https://cdnjs.cloudflare.com/ajax/libs/jsencrypt/2.3.1/jsencrypt.min.js) | 
                  [GitHub](https://github.com/travist/jsencrypt)
    """

    use_custom_js: typing.Optional[bool] = False
    """Set this to `True` prevents HAuth from attaching `{js_path}` route to the web server.

    May be useful if you want to serve JS from a different server or CDN.
    """

    callback_url: typing.Optional[str] = None
    """Url the user is redirected to after successful login.

    `session_id` will be passed as a query parameter.
    """

    login_page_path: typing.Optional[str] = None
    """Path to the login HTML file. If not provided, the default login page will be used.

    Note that using this option will make HAuth ignore the `login_page_style`.
    """

    login_page_style: typing.Optional[LoginPageStyle] = pydantic.Field(
        default=LoginPageStyle(color=Color.BLUE, theme_mode=ThemeMode.AUTO)
    )
    """Style for the login page.

    Only used if `login_page_path` is not provided.
    """

    localization: typing.Optional[Localization] = pydantic.Field(default=Localization())
    """Custom localization for HoYoLab Auth.

    Example usage:
    ```python
    localization = Localization(
        invalid_credentials={
            "en": "The credentials you entered are invalid.",
            "ru": "Введенные вами учетные данные недействительны."
        }
    )
    ```

    Another example:
    ```python
    translations = {
        "invalid_credentials": {
            "en": "The credentials you entered are invalid.",
            "ru": "Введенные вами учетные данные недействительны."
        }
    }
    localization = Localization(**translations)
    ```
    """
