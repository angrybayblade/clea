## Define a group

Define you first command group using 

```python
from clea import run, group, Integer, Boolean

from typing_extensions import Annotated


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


if __name__ == "__main__":
    run(cli=calculator)
```

> The example is taken from [calculator.py](https://github.com/angrybayblade/clea/blob/main/examples/calculator.py) in the examples folder.

You can check the command definition using 

```bash
Usage: calculator [OPTIONS] 

        CLI Calculator app.

Options:

    --help                        Show help and exit.

Commands:

    add                           Add two numbers.
```

Execute the command using

```bash
$ python calculator.py add 2 3

Answer 5
```

## With custom name

```python
(...)

@group(name="calculator-app")
def calculator() -> None:
    """CLI Calculator app."""


@calculator.command
def add(
    n1: Annotated[int, Integer()],
    n2: Annotated[int, Integer()],
) -> None:
    """Add two numbers."""

(...)
```

The custom name will show up as the group name

```bash
$ python calculator.py --help

Usage: calculator-app [OPTIONS] 

        CLI Calculator app.

Options:

    --help                        Show help and exit.

Commands:

    add                           Add two numbers.
```

## Next steps 

- [Parameters](/clea/parameters)
- [Context](/clea/context)
- [Testing](/clea/testing)
