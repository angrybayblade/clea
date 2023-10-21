"""Test calculator.py."""

from clea.runner import run
from examples.calculator import calculator as cli


def test_help() -> None:
    """Test help."""
    result = run(cli=cli, argv=["--help"], isolated=True)
    assert "CLI Calculator app." in result.stdout


def test_add() -> None:
    """Test add."""
    result = run(cli=cli, argv=["add", "1", "2"], isolated=True)
    assert result.exit_code == 0
    assert "Answer 3\n" in result.stdout


def test_subtract() -> None:
    """Test subtract."""
    result = run(cli=cli, argv=["subtract", "1", "2"], isolated=True)
    assert result.exit_code == 0
    assert "Answer -1\n" in result.stdout


def test_multiply() -> None:
    """Test multiply."""
    result = run(cli=cli, argv=["multiply", "1", "2"], isolated=True)
    assert result.exit_code == 0
    assert "Answer 2\n" in result.stdout


def test_devide() -> None:
    """Test devide."""
    result = run(cli=cli, argv=["devide", "1", "2"], isolated=True)
    assert result.exit_code == 0
    assert "Answer 0.5\n" in result.stdout


def test_devide_with_round() -> None:
    """Test devide."""
    result = run(cli=cli, argv=["devide", "1", "2", "--round"], isolated=True)
    assert result.exit_code == 0
    assert "Answer 0\n" in result.stdout
