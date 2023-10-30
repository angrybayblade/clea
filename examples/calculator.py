"""Calculator example."""


from typing_extensions import Annotated

from clea import Boolean, Integer, group, run


@group
def calculator() -> None:
    """CLI Calculator app."""


@calculator.command
def add(
    n1: Annotated[int, Integer()],
    n2: Annotated[int, Integer()],
) -> None:
    """Add two numbers."""

    print(f"Answer {n1+n2}")


@calculator.command
def subtract(
    n1: Annotated[int, Integer()],
    n2: Annotated[int, Integer()],
) -> None:
    """Subtract two numbers."""

    print(f"Answer {n1-n2}")


@calculator.command
def multiply(
    n1: Annotated[int, Integer()],
    n2: Annotated[int, Integer()],
) -> None:
    """Multiply two numbers."""

    print(f"Answer {n1*n2}")


@calculator.command
def devide(
    n1: Annotated[int, Integer()],
    n2: Annotated[int, Integer()],
    round: Annotated[  # pylint: disable=redefined-builtin
        bool, Boolean(help="Round up the answer")
    ],
) -> None:
    """Devide two numbers."""

    if round:
        print(f"Answer {n1//n2}")
    else:
        print(f"Answer {n1/n2}")


if __name__ == "__main__":  # pragma: nocover
    run(cli=calculator)
