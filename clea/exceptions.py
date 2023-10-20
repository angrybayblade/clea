"""Exceptions"""


class CleaException(Exception):
    """Base clea exception."""

    def __init__(
        self,
        message: str,
        *args: object,
        exit_code: int = 1,
    ) -> None:
        """Initialize object."""
        super().__init__(message, *args)
        self.message = message
        self.exit_code = exit_code


class RuntimeException(CleaException):
    """Raised if the CLI runtime was inturrupted."""


class ParsingError(CleaException):
    """Raised if there was an error parsing an argument."""


class ArgumentsMissing(CleaException):
    """Raised if there was an error parsing an argument."""


class ExtraArgumentProvided(CleaException):
    """Raised if there was an error parsing an argument."""
