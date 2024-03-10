## Define a command

<!-- {"file": "examples/add.py", "type": "example"} -->
```python
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


if __name__ == "__main__":
    run(cli=add)
```

*The example is taken from [add.py](https://github.com/angrybayblade/clea/blob/main/examples/add.py) in the examples folder.*

<!-- {"type": "exec", "directory": "examples/", "read": "stdout"} -->
```bash
$ python add.py --help

Usage: add [OPTIONS] N1 N2

	Add two numbers

Options:

    --help                        Show help and exit.
```

Running the application

<!-- {"type": "exec", "directory": "examples/", "read": "stdout"} -->
```bash
$ python add.py 2 3

Total 5
```

## With custom name

<!-- {"file": "examples/add_numbers.py", "type": "example", "start": 7, "end": 15} -->
```python
@command(name="add-numbers")
def add(
    n1: Annotated[int, Integer()],
    n2: Annotated[int, Integer()],
) -> None:
    """Add two numbers"""

    print(f"Total {n1 + n2}")
```

## Next steps 

- [Group](/group)
- [Parameters](/parameters)
