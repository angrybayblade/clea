"""Runtime context."""


import typing as t


class Context:
    """Runtime context class."""

    _data: t.Dict[t.Any, t.Any]

    def __init__(self) -> None:
        """Initialize context."""
        self._data = {}

    def set(self, key: t.Any, value: t.Any) -> None:
        """Set config value."""
        self._data[key] = value

    def get(self, key: t.Any, default: t.Any = None) -> t.Any:
        """Get config value."""
        return self._data.get(key, default)
