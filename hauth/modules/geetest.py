"""Functions for Geetest captcha."""


__all__ = ["get_lang_from_language"]


def get_lang_from_language(language: str) -> str:
    """Get geetest lang from language."""
    if language in [
        "zh-cn",
        "zh-hk",
        "zh-tw",
        "en",
        "ja",
        "ko",
        "id",
        "ru",
        "ar",
        "es",
        "pt-pt",
        "fr",
        "de",
        "th",
        "tr",
        "vi",
        "ta",
        "it",
        "bn",
        "mr"
    ]:
        return language
    return "en"
