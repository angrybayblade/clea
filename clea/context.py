"""Runtime context."""


import typing as t
from pathlib import Path


class Context:
    """Runtime context class."""

    _data: t.Dict[t.Any, t.Any]

    def __init__(self) -> None:
        """Initialize context."""
        self._data = {}
        self._cwd = Path.cwd()

    @property
    def cwd(self) -> Path:
        """Current working directory."""
        return self._cwd

    def set(self, key: t.Any, value: t.Any) -> None:
        """Set config value."""
        self._data[key] = value

    def get(self, key: t.Any, default: t.Any = None) -> t.Any:
        """Get config value."""
        return self._data.get(key, default)
