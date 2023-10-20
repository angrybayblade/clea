# Clea - A lightweight framework for creating CLI applications in python

Clea is uses type annotations to generate the command/group defintions and parse the arguments at the runtime. To start with clea run

```
pip3 install clea
```

Define you first command using 

```python
from typing_extensions import Annotated

from clea.params import Integer
from clea.wrappers import command

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
from clea.runner import run

if __name__ == "__main__":
    run(cli=add)
```

> The example is taken from [add.py](examples/add.py) in the examples folder.

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

Read more about the usage of clea in the [docs](https://angrybayblade.github.io/clea/)
