"""Test context."""

from pathlib import Path

from clea.context import Context


def test_cwd() -> None:
    """Test current working directory."""
    ctx = Context()
    assert ctx.cwd == Path.cwd()


def test_data_store() -> None:
    """Test data store."""
    ctx = Context()
    ctx.set("hello", "world")
    assert ctx.get("hello") == "world"
