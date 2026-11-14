"""Public package interface for Catbox Uploader Plus.

Import the main client and public exception classes directly from ``catbox``.
"""

from .catbox import CatboxUploader
from .exceptions import (
    CatboxError,
    FileNotFoundError,
    TimeoutError,
    ConnectionError,
    HTTPError,
)

__all__ = [
    "CatboxUploader",
    "CatboxError",
    "FileNotFoundError",
    "TimeoutError",
    "ConnectionError",
    "HTTPError",
]
