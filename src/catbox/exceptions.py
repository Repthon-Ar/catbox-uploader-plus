"""Custom exceptions used by Catbox Uploader Plus."""


class CatboxError(Exception):
    """Base exception for all Catbox Uploader Plus errors."""


class FileNotFoundError(CatboxError):
    """Raised when the requested upload file does not exist."""


class TimeoutError(CatboxError):
    """Raised when a Catbox request exceeds its configured timeout."""


class ConnectionError(CatboxError):
    """Raised when a connection to Catbox or Litterbox fails."""


class HTTPError(CatboxError):
    """Raised when the remote service returns an unsuccessful HTTP response."""


__all__ = [
    "CatboxError",
    "FileNotFoundError",
    "TimeoutError",
    "ConnectionError",
    "HTTPError",
]
