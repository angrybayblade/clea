"""Simple add program."""

from typing_extensions import Annotated

from clea import Integer, command, run


@command
def add(
    n1: Annotated[int, Integer()],
    n2: Annotated[int, Integer()],
) -> None:
    """Add two numbers"""

    print(f"Total {n1 + n2}")


if __name__ == "__main__":  # pragma: nocover
    run(cli=add)
