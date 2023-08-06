"""CLI Runner."""

import sys
import typing as t

from clea.exceptions import BasecleaException
from clea.parser import Argv
from clea.wrappers import BaseWrapper


def run(
    cli: BaseWrapper,
    argv: t.Optional[Argv] = None,
) -> int:
    """Run the command line utility."""
    argv = argv or sys.argv[1:].copy()
    try:
        return_code = cli.invoke(argv=argv)
        sys.exit(return_code)
    except BasecleaException as e:
        print(e)
        sys.exit(1)
