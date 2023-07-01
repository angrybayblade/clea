"""clea helpers."""

import inspect
import itertools
from typing import Any, Callable, Dict, Tuple

from typing_extensions import Annotated

from clea.params import Parameter


def get_function_metadata(
    f: Callable,
) -> Tuple[Dict[str, Any], Dict[str, Annotated[Any, Parameter]]]:
    """
    Get argument mappings for a given function.

    :param f: The function to get argument mappings for.
    :type f: callable
    :return: A dictionary mapping argument names to their default values and annotations.
    :rtype: dict
    """
    # TODO: Optimise
    specs = inspect.getfullargspec(f)
    args = specs.args.copy()
    defaults = itertools.chain(
        [None for _ in range(len(args) - len(specs.defaults or []))],
        (specs.defaults or []),
    )
    return dict(zip(specs.args, defaults)), specs.annotations
