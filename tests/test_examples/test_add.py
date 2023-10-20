"""Test add.py"""

from examples.add import add as cli
from clea.runner import run


def test_missing_arguments() -> None:
    """Test add."""
    result = run(cli=cli, argv=[], isolated=True)
    assert result.exit_code == 1
    assert (
        "Missing argument for positional arguments <N1 type=int>, <N2 type=int>"
        in result.stderr
    )


def test_add() -> None:
    """Test add."""
    result = run(cli=cli, argv=["1", "2"], isolated=True)
    assert result.exit_code == 0
    assert "Total 3" in result.stdout
