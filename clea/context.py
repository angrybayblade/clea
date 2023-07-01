"""Runtime context."""


from typing import Any, Dict


class Context:
    """Runtime context class."""

    _data: Dict[Any, Any]

    def __init__(self) -> None:
        self._data = {}

    def set(self, key: Any, value: Any) -> None:
        self._data[key] = value

    def get(self, key: Any, default: Any = None) -> Any:
        return self._data.get(key, default)
