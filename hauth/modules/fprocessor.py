"""File processor module. Used to load files and insert data into them."""
from ..models import Localization


__all__ = ["process"]


def process(path: str, language: str, localization: Localization, **kwargs) -> str:
    """Process a file, insert localization and data into it."""
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()

    for key, value in localization.model_dump().items():
        content = content.replace("{{" + key + "}}", value.get(language, ""))
    for key, value in kwargs.items():
        content = content.replace("{{" + key + "}}", str(value))

    return content
