"""Simple add program."""

from typing_extensions import Annotated

from clea.params import Integer
from clea.runner import run
from clea.wrappers import command


@command
def add(
    n1: Annotated[int, Integer()],
    n2: Annotated[int, Integer()],
) -> None:
    """Add two numbers"""

    print(f"Total {n1 + n2}")


if __name__ == "__main__":  # pragma: nocover
    run(cli=add)
