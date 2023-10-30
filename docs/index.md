## Introduction

Clea is a framework for creating CLI applications in python very quickly. Clea uses type annotations for defining arguments. To start with clea run

## Install

```
pip3 install clea
```

## Quickstart

Define your first application 

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

Execute the command using

<!-- {"type": "exec", "directory": "examples/", "read": "stdout"} -->
```bash
$ python add.py 2 3

Total 5
```

## Next steps 

- [Command](/clea/command)
- [Group](/clea/group)
- [Parameters](/clea/parameters)
