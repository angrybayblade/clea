"""CLI Runner."""

import contextlib
import io
import sys
import typing as t

from clea.exceptions import CleaException
from clea.parser import Argv
from clea.wrappers import BaseWrapper


class Result:  # pylint: disable=too-few-public-methods
    """Run result."""

    def __init__(
        self,
        exit_code: int,
        stderr: str,
        stdout: str,
    ) -> None:
        """Initialize object."""
        self.exit_code = exit_code
        self.stderr = stderr
        self.stdout = stdout


def _run(cli: BaseWrapper, argv: Argv) -> Result:
    """Run CLI application."""
    try:
        return Result(
            exit_code=cli.invoke(argv=argv, isolated=False),
            stderr="",
            stdout="",
        )
    except CleaException as e:
        return Result(
            exit_code=e.exit_code,
            stderr=e.message,
            stdout="",
        )


def _run_isolated(cli: BaseWrapper, argv: Argv) -> Result:
    """Run CLI application isolated."""
    stdout_ctx = contextlib.redirect_stdout(new_target=io.StringIO())
    stderr_ctx = contextlib.redirect_stderr(new_target=io.StringIO())
    with stderr_ctx as stderr, stdout_ctx as stdout:
        result = _run(cli=cli, argv=argv)
        return Result(
            exit_code=result.exit_code,
            stdout=stdout.getvalue(),
            stderr=(stderr.getvalue() + result.stderr),
        )


def run(
    cli: BaseWrapper,
    argv: t.Optional[Argv] = None,
    isolated: bool = False,
) -> Result:
    """Run the command line utility."""
    argv = argv if argv is not None else sys.argv[1:].copy()
    result = _run_isolated(cli=cli, argv=argv) if isolated else _run(cli=cli, argv=argv)
    if not isolated:
        if result.stderr != "":  # pragma: nocover
            sys.stderr.write(result.stderr + "\n")
        sys.exit(result.exit_code)
    return result
