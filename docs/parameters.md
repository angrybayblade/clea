## Parameters

Clea processes the method argument defintions in a pythonic way, which means argument without default values will be treated as required arguments and arguments with default values will be treated as keyword arguments. 

The default arguments don't need any explicit flags whereas the keyword arguments will require flag to be passed as an argument.

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

## Base types

Take an `integer/float/string` as an argument.

```python
(...)

from clea.params import Integer, String, Float
(...)


@command(name="print")
def _print(
    integer: Annotated[int, Integer(help="Number argument.")],
    string: Annotated[str, String(help="String argument.")],
    flt: Annotated[float, Float(help="Float argument.")],
) -> None:
    """Take arguments and print them on console."""

    print(f"{integer=}")
    print(f"{string=}")
    print(f"float={flt}")

(...)
```

Help output

```
$ python command.py --help

Usage: print [OPTIONS] INTEGER STRING FLT

        Take arguments and print them on console.

Options:

    --help                        Show help and exit.
```


## Boolean flags

The boolean flags do not require any input and they're considered as an `optional/keyword` argument with default value being `False` if not set to `True` explicitly. Providing the flag as an CLI argument will negate the default value and use it as the argument value when calling the function, which means if the default is set to `False` and you provide the flag when running the command the value will be set to `True` and vice versa.

```python
(...)

from clea.params import Boolean
(...)


@command(name="print")
def _print(
    flag: Annotated[bool, Boolean(help="Boolean flag.")],
) -> None:
    """Take arguments and print them on console."""

    print(f"{flag=}")

(...)
```

Runing without any argument

```
$ python command.py

flag=False
```

Running with flag

```
$ python command.py --flag

flag=True
```

## List of strings

To take a list of strings as an argument you can use `clea.params.StringList` parameter.

```python
from typing import List

(...)

from clea.params import StringList
(...)


@command(name="print")
def _print(
    strings: Annotated[List[str], StringList("-s", "--string", help="A list of strings.")],
) -> None:
    """Take arguments and print them on console."""

    print(f"{strings=}")

(...)
```

If you don't provide any argument for the parameter the list will be empty by default. 

```
$ python command.py

strings=[]
```

Provide however many arguments you want using

```
$ python command.py -s=Hello -s=World --string="Foo Bar"

strings=['Hello', 'World', 'Foo Bar']
```

## Choice

You can utilise `enum.Enum` and `clea.params.Choice` to create a choice paramters which will let the user choose from available enum values.


```python
from enum import Enum
from typing import List

(...)

from clea.params import Choice
(...)


class ConnectionType(Enum):
    """Connection type enum."""

    TCP = "tcp"
    UDP = "udp"

@command(name="print")
def _print(
    ctype: Annotated[List[str], Choice(enum=ConnectionType, help="A list of strings.")],
) -> None:
    """Take arguments and print them on console."""

    print(f"{ctype=}")

(...)
```

The input will be parsed as an enum

```
$ python command.py tcp

ctype=<ConnectionType.TCP: 'tcp'>
```

Providing input which is not defined as an enum value will raise an error

```
$ python command.py tc

Error parsing value for <CTYPE type=Enum>; Provided value=tc; Expected value from {'tcp', 'udp'}
```

## ChoiceByFlag

You can also define a `Choice` parameter which uses flags for each choice available to take the input using `clea.params.ChoiceByFlag` param.

```python
from enum import Enum
from typing import List

(...)

from clea.params import ChoiceByFlag
(...)


class ConnectionType(Enum):
    """Connection type enum."""

    TCP = "tcp"
    UDP = "udp"

@command(name="print")
def _print(
    ctype: Annotated[List[str], ChoiceByFlag(enum=ConnectionType, help="Choose connection type.")],
) -> None:
    """Take arguments and print them on console."""

    print(f"{ctype=}")

(...)
```

The help string will be different here since every value in the enum will be defined as an individual flag

```
$ python command.py --help

Usage: print [OPTIONS] 

        Take arguments and print them on console.

Options:

    --tcp, --udp                  Choose connection type.
    --help                        Show help and exit.
```

As before the input will be parsed as enum value

```
$ python command.py --tcp

ctype=<ConnectionType.TCP: 'tcp'>
```

## File

Use `clea.params.File` to take a file path as an argument. The path string will be parsed as `pathlib.Path` object.

```python
from pathlib import Path

(...)

from clea.params import File
(...)


@command(name="print")
def _print(
    certificate: Annotated[Path, File("-c", help="Path to certificate file.")],
) -> None:
    """Take arguments and print them on console."""

    print(f"{certificate=}")

(...)
```

Help output

```
$ python command.py --help

Usage: print [OPTIONS] 

        Take arguments and print them on console.

Options:

    -c                            Path to certificate file.
    --help                        Show help and exit.
```

Running the command

```
$ python command.py -c=cert.pem

certificate=PosixPath('cert.pem')
```

## Directory

Use `clea.params.Directory` to take a directory as an argument. The path string will be parsed as `pathlib.Path` object.

```python
from pathlib import Path

(...)

from clea.params import Directory
(...)


@command(name="print")
def _print(
    build_dir: Annotated[Path, Directory("-b", help="Path to build directory.")],
) -> None:
    """Take arguments and print them on console."""

    print(f"{build_dir=}")

(...)
```

Help output

```
$ python command.py --help

Usage: print [OPTIONS] 

        Take arguments and print them on console.

Options:

    -b                            Path to build directory.
    --help                        Show help and exit.
```

Running the command

```
$ python command.py -b=path/to/build

certificate=PosixPath('path/to/build')
```

## Next steps

- [Context](/clea/context)
- [Testing](/clea/testing)
