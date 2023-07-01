"""Exceptions"""


class BasecleaException(Exception):
    """Base clea exception."""


class RuntimeException(BasecleaException):
    """Raised if the CLI runtime was inturrupted."""


class ParsingError(BasecleaException):
    """Raised if there was an error parsing an argument."""


class ArgumentsMissing(BasecleaException):
    """Raised if there was an error parsing an argument."""


class ExtraArgumentProvided(BasecleaException):
    """Raised if there was an error parsing an argument."""
