"""clea helpers."""

import inspect
import itertools
import typing as t

from typing_extensions import Annotated

from clea.params import Parameter


def get_function_metadata(
    f: t.Callable,
) -> t.Tuple[t.Dict[str, t.Any], t.Dict[str, Annotated[t.Any, Parameter]]]:
    """
    Get argument mappings for a given function.

    :param f: The function to get argument mappings for.
    :type f: callable
    :return: A dictionary mapping argument names to their default values and annotations.
    :rtype: dict
    """
    specs = inspect.getfullargspec(f)
    args = specs.args.copy()
    defaults = itertools.chain(
        [None for _ in range(len(args) - len(specs.defaults or []))],
        (specs.defaults or []),
    )
    return dict(zip(specs.args, defaults)), specs.annotations
