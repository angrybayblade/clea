"""Test context.py"""

from examples.context import admin as cli
from clea.runner import run


def test_data_store() -> None:
    """Test context data store."""
    result = run(cli=cli, argv=["manage", "student"], isolated=True)
    assert "bar\nworld\n" == result.stdout
