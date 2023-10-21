"""Test custom_context.py"""

from examples.custom_context import home as cli
from clea.runner import run


def test_get_home() -> None:
    """Test get home from config."""
    result = run(cli=cli, argv=[], isolated=True)
    assert "~/.app" in result.stdout
