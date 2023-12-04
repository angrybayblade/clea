"""Command line parser."""

import typing as t
from collections import deque

from clea.context import Context
from clea.exceptions import ArgumentsMissing, ExtraArgumentProvided
from clea.params import ChoiceByFlag, ContextParameter, Parameter


Argv = t.List[str]
Args = t.List[t.Any]
Kwargs = t.Dict[str, t.Any]

HelpOnly = bool
VersionOnly = bool
ParsedCommandArgs = t.Tuple[Args, Kwargs, HelpOnly, VersionOnly]
ParsedGroupArgs = t.Tuple[Args, Kwargs, HelpOnly, VersionOnly, t.Any, Args]


class BaseParser:
    """Argument parser."""

    _args: t.Deque[Parameter]
    _kwargs: t.Dict[str, Parameter]

    def __init__(self) -> None:
        """Initialize object."""

        self._kwargs = {}
        self._args = deque()

    def set_context(self, context: Context) -> None:
        """Set context."""
        if "--context" in self._kwargs:
            t.cast(ContextParameter, self._kwargs["--context"]).set(context=context)

    def get_arg_vars(self) -> t.List[str]:
        """Get a t.list of metavars."""
        return list(map(lambda x: x.var, self._args))

    def raise_missing_args(self) -> None:
        """Raise if `args` t.list has parameter defintions"""
        missing = list(map(lambda x: x.metavar, self._args))
        raise ArgumentsMissing(
            message="Missing argument for positional arguments " + ", ".join(missing),
            exit_code=1,
        )

    def add(self, defintion: Parameter) -> None:
        """Add parameter."""

        if isinstance(defintion, ChoiceByFlag):
            for long_flag in defintion.flag_to_value:
                self._kwargs[long_flag] = defintion
            return

        if (
            defintion.default is None
            and defintion.short_flag is None
            and defintion.long_flag is None
        ):
            self._args.append(defintion)
            return

        if defintion.default is not None and defintion.long_flag is None:
            self._kwargs[defintion.create_long_flag()] = defintion

        if defintion.long_flag is not None:
            self._kwargs[defintion.long_flag] = defintion

        if defintion.short_flag is not None:
            self._kwargs[defintion.short_flag] = defintion

    def parse(  # pylint: disable=unused-argument
        self, argv: Argv, commands: t.Optional[t.Dict[str, t.Any]] = None
    ) -> t.Tuple:
        """Parse and return kwargs."""
        return NotImplemented  # pragma: nocover


class CommandParser(BaseParser):
    """Argument parser for command."""

    def parse(  # pylint: disable=too-many-branches
        self, argv: Argv, commands: t.Optional[t.Dict[str, t.Any]] = None
    ) -> ParsedCommandArgs:
        """Parse and return kwargs."""
        args: Args = []
        kwargs: Kwargs = {}
        for arg in argv:
            if arg == "--help":
                return args, kwargs, True, False
            if arg == "--version":
                return args, kwargs, False, True
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
                    self._kwargs.pop(definition.short_flag or "", None)
                    self._kwargs.pop(definition.long_flag or "", None)
            else:
                if len(self._args) == 0:
                    raise ExtraArgumentProvided(f"Extra argument provided `{arg}`")
                definition = self._args.popleft()
                args.append(definition.parse(arg))

        if len(self._args) > 0:
            self.raise_missing_args()

        if len(self._kwargs) > 0:
            for kwarg in self._kwargs.values():
                if kwarg.name == "version":
                    continue  # pragma: nocover
                if kwarg.is_container:
                    kwargs[kwarg.name] = kwarg.container
                else:
                    kwargs[kwarg.name] = kwarg.default
        return args, kwargs, False, False

    def copy(self) -> "CommandParser":
        """Create a copy of the object."""
        parser = CommandParser()
        parser._args = deque(self._args)  # pylint: disable=protected-access
        parser._kwargs = self._kwargs.copy()  # pylint: disable=protected-access
        return parser


class GroupParser(BaseParser):
    """Argument parser."""

    def parse(  # pylint: disable=too-many-branches
        self, argv: Argv, commands: t.Optional[t.Dict[str, t.Any]] = None
    ) -> ParsedGroupArgs:
        """Parse and return kwargs."""
        commands = commands or {}
        args: Args = []
        kwargs: Kwargs = {}
        sub_argv: Args = []
        sub_command: t.Any = None
        for i, arg in enumerate(argv):
            sub_command = commands.get(arg)
            if sub_command is not None:
                _i = i + 1
                sub_argv = argv[_i:]
                break
            if arg == "--help":
                return args, kwargs, True, False, None, argv
            if arg == "--version":
                return args, kwargs, False, True, None, argv
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
                    self._kwargs.pop(definition.short_flag or "", None)
                    self._kwargs.pop(definition.long_flag or "", None)
            else:
                if len(self._args) == 0:
                    raise ExtraArgumentProvided(f"Extra argument provided `{arg}`")
                definition = self._args.popleft()
                args.append(definition.parse(arg))

        if len(self._args) > 0:
            self.raise_missing_args()

        if len(self._kwargs) > 0:
            for kwarg in self._kwargs.values():
                if kwarg.name == "version":
                    continue  # pragma: nocover
                if kwarg.is_container:
                    kwargs[kwarg.name] = kwarg.container
                else:
                    kwargs[kwarg.name] = kwarg.default
        return args, kwargs, False, False, sub_command, sub_argv

    def copy(self) -> "GroupParser":
        """Create a copy of the object."""
        parser = GroupParser()
        parser._args = deque(self._args)  # pylint: disable=protected-access
        parser._kwargs = self._kwargs.copy()  # pylint: disable=protected-access
        return parser
