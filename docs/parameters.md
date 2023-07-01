# Parameters

Clea processes the method argument defintions in a pythonic way, which means argument without default values will be treated as required arguments and arguments with default values will be treated as keyword arguments. The default arguments don't need any explicit flags whereas the keyword arguments will require flag to be passed as an argument.

For example

```python
from typing_extensions import Annotated

from clea.params import Integer
from clea.runner import run
from clea.wrappers import command


@command
def add(
    n1: Annotated[int, Integer(help="First number")],
    n2: Annotated[int, Integer(help="Second number")] = 0,
) -> None:
    """Add two numbers"""

    print(f"Total {n1 + n2}")


if __name__ == "__main__":
    run(cli=add)
```

If you run with `--help` you'll see that `n2` is defined as a flag parameter

```bash
$ python add.py --help

Usage: add [OPTIONS] N1

        Add two numbers

Options:

    --n2                          Second number
    --help                        Show help and exit.
```

If you execute this as

```bash
$ python add.py
```

You'll get an error saying

```
Missing argument for positional arguments <N1 type=int>
```

As you can see the CLI only complains about one positional argument. So if you execute this command as

```bash
$ python add.py 10
```

The result will be shown as 

```bash
Total 10
```

Now you can provide the second value as

```bash
$ python add.py 10 --n2=20

Total 30
```

