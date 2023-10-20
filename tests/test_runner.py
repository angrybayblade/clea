"""Test application runner."""

import contextlib
import io
from unittest import mock

from clea.runner import run
from examples.add import add as cli


def test_runner() -> None:
    """Test runner."""
    with mock.patch("sys.exit"), contextlib.redirect_stdout(
        new_target=io.StringIO()
    ) as stdout:
        run(cli=cli, argv=["1", "2"])
        assert "Total 3" in stdout.getvalue()


def test_runner_isolated() -> None:
    """Test runner isolated."""
    result = run(cli=cli, argv=["1", "2"], isolated=True)
    assert "Total 3" in result.stdout


def test_runner_stderr_capture() -> None:
    """Test runner isolated."""
    result = run(cli=cli, argv=[], isolated=True)
    assert (
        "Missing argument for positional arguments <N1 type=int>, <N2 type=int>"
        in result.stderr
    )
