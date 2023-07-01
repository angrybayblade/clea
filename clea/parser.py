"""Command line parser."""

from queue import Queue
from typing import Any, Dict, List, Optional, Tuple

from clea.context import Context
from clea.exceptions import ArgumentsMissing, ExtraArgumentProvided
from clea.params import ChoiceByFlag, Parameter


Argv = List[str]
Args = List[Any]
Kwargs = Dict[str, Any]

ParsedCommandArgs = Tuple[Args, Kwargs, bool]
ParsedGroupArgs = Tuple[Args, Kwargs, bool, Any, Args]


class BaseParser:
    """Argument parser."""

    _args: Queue[Parameter]
    _kwargs: Dict[str, Parameter]

    def __init__(self) -> None:
        """Initialize object."""

        self._kwargs = {}
        self._args = Queue()

    def get_arg_vars(self) -> List[str]:
        """Get a list of metavars."""
        missing = []
        while not self._args.empty():
            missing.append(self._args.get().var)
        return missing

    def _raise_missing_args(self) -> None:
        """Raise if `args` list has parameter defintions"""
        missing = []
        while not self._args.empty():
            missing.append(self._args.get().metavar)
        raise ArgumentsMissing(
            "Missing argument for positional arguments " + ", ".join(missing)
        )

    def add(self, defintion: Parameter) -> None:
        """Add parameter."""

        if isinstance(defintion, ChoiceByFlag):
            for long_flag in defintion.flag_to_value:
                self._kwargs[long_flag] = defintion
            return

        if defintion.default is not None:
            self._kwargs[defintion.long_flag] = defintion

        if defintion.short_flag is not None:
            self._kwargs[defintion.short_flag] = defintion
            return

        if defintion.default is None:
            self._args.put(defintion)

    def parse(self, argv: Argv, commands: Optional[Dict[str, Any]] = None) -> Tuple:
        """Parse and return kwargs."""
        return NotImplemented


class CommandParser(BaseParser):
    """Argument parser for command."""

    def parse(
        self, argv: Argv, commands: Optional[Dict[str, Any]] = None
    ) -> ParsedCommandArgs:
        """Parse and return kwargs."""
        args: Args = []
        kwargs: Kwargs = {}
        for arg in argv:
            if arg == "--help":
                return args, kwargs, True
            if arg.startswith("-"):
                if "=" in arg:
                    flag, value = arg.split("=")
                else:
                    flag, value = arg, arg
                definition = self._kwargs.pop(flag, None)
                if definition is None:
                    raise ExtraArgumentProvided(
                        f"Extra argument provided with flag `{flag}`"
                    )
                kwargs[definition.name] = definition.parse(value=value)
                if definition.is_container:
                    self._kwargs[flag] = definition
            else:
                if self._args.empty():
                    raise ExtraArgumentProvided(f"Extra argument provided `{arg}`")
                definition = self._args.get()
                args.append(definition.parse(arg))

        if not self._args.empty():
            self._raise_missing_args()

        if len(self._kwargs) > 0:
            for kwarg in self._kwargs.values():
                if kwarg.is_container:
                    kwargs[kwarg.name] = kwarg.container
                else:
                    kwargs[kwarg.name] = kwarg.default
        return args, kwargs, False


class GroupParser(BaseParser):
    """Argument parser."""

    def parse(
        self, argv: Argv, commands: Optional[Dict[str, Any]] = None
    ) -> Tuple[Args, Kwargs, bool, Any, Args]:
        """Parse and return kwargs."""
        commands = commands or {}
        args: Args = []
        kwargs: Kwargs = {}
        sub_argv: Args = []
        sub_command: Any = None
        for i, arg in enumerate(argv):
            sub_command = commands.get(arg)
            if sub_command is not None:
                sub_argv = argv[i + 1 :]
                break
            if arg == "--help":
                return args, kwargs, True, None, argv
            if arg.startswith("-"):
                if "=" in arg:
                    flag, value = arg.split("=")
                else:
                    flag, value = arg, arg
                definition = self._kwargs.pop(flag, None)
                if definition is None:
                    raise ExtraArgumentProvided(
                        f"Extra argument provided with flag `{flag}`"
                    )
                kwargs[definition.name] = definition.parse(value=value)
                if definition.is_container:
                    self._kwargs[flag] = definition
            else:
                if self._args.empty():
                    raise ExtraArgumentProvided(f"Extra argument provided `{arg}`")
                definition = self._args.get()
                args.append(definition.parse(arg))

        if not self._args.empty():
            self._raise_missing_args()

        if len(self._kwargs) > 0:
            for kwarg in self._kwargs.values():
                if kwarg.is_container:
                    kwargs[kwarg.name] = kwarg.container
                else:
                    kwargs[kwarg.name] = kwarg.default
        return args, kwargs, False, sub_command, sub_argv
