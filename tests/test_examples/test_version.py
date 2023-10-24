"""Test version.py."""

from examples.version import example as cli
from clea.runner import run


def test_version_flag() -> None:
    """Test version flag."""
    result = run(cli=cli, argv=["--version"], isolated=True)
    assert "0.1.0.rc0" in result.stdout
