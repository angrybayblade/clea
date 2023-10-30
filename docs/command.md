## Define a command

```python
from typing_extensions import Annotated

from clea import Integer, command

@command
def add(
    n1: Annotated[int, Integer()],
    n2: Annotated[int, Integer()],
) -> None:
    """Add two numbers"""

    print(f"Total {n1 + n2}")
```

Invoke the command at runtime using

```python
from clea import run

if __name__ == "__main__":
    run(cli=add)
```

> The example is taken from [add.py](https://github.com/angrybayblade/clea/blob/main/examples/add.py) in the examples folder.

You can check the command definition using 

```bash
$ python add.py --help

Usage: add [OPTIONS] N1 N2

        Add two numbers

Options:

    --help                        Show help and exit.
```

Execute the command using

```bash
$ python add.py 2 3

Total 5
```

## With custom name

```python
(...)

@command(name="add-numbers")
def add(
    n1: Annotated[int, Integer()],
    n2: Annotated[int, Integer()],
) -> None:
    """Add two numbers"""
    print (f"Total: {n1+n2}")

(...)
```

The custom name will show up as the command name

```bash
$ python add.py --help

Usage: add-numbers [OPTIONS] N1 N2

        Add two numbers

Options:

    --help                        Show help and exit.
```

## Next steps 

- [Group](/clea/group)
- [Parameters](/clea/parameters)
