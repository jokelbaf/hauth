"""Run setuptools."""
from setuptools import find_packages, setup

setup(
    name = "hauth",
    version = "0.1.0",
    author = "jokelbaf",
    author_email = "jokelbaf@gmail.com",
    description = "A simple and user-friendly package for authenticating in HoYoLab API via web interface.",
    keywords = "genshin hoyolab honkai auth".split(),
    url = "https://github.com/jokelbaf/hauth",
    project_urls = {
        "Documentation": "https://jokelbaf.github.io/hauth",
        "Issue tracker": "https://github.com/jokelbaf/hauth/issues",
    },
    packages = find_packages(exclude=["tests.*"]),
    python_requires = ">=3.8",
    install_requires = ["aiohttp"],
    include_package_data = True,
    package_data = {"hauth": ["py.typed"]},
    long_description = open("README.md", encoding="utf-8").read(),
    long_description_content_type = "text/markdown",
    license = "MIT",
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)