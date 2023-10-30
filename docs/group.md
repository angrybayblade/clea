## Define a group

<!-- {"file": "examples/calculator.py", "type": "example"} -->
```python
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


if __name__ == "__main__":
    run(cli=calculator)
```

<!-- {"type": "exec", "directory": "examples/", "read": "stdout"} -->
```bash
$ python calculator.py --help

Usage: calculator [OPTIONS] 

	CLI Calculator app.

Options:

    --help                        Show help and exit.

Commands:

    add                           Add two numbers.
    subtract                      Subtract two numbers.
    multiply                      Multiply two numbers.
    devide                        Devide two numbers.
```

Running the application

<!-- {"type": "exec", "directory": "examples/", "read": "stdout"} -->
```bash
$ python calculator.py add 2 3

Answer 5
```

## Next steps 

- [Parameters](/clea/parameters)
- [Context](/clea/context)
- [Testing](/clea/testing)
