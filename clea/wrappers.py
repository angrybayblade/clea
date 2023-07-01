"""
Single command implementation.

This module provides a Command class that represents a single command implementation.
"""


from functools import partial
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union, cast, overload

from clea.context import Context
from clea.helpers import get_function_metadata
from clea.params import ContextParameter, HELP_COL_LENGTH, Parameter
from clea.parser import (
    Args,
    Argv,
    BaseParser,
    CommandParser,
    GroupParser,
    Kwargs,
    ParsedCommandArgs,
    ParsedGroupArgs,
)


Annotations = Dict[str, Parameter]


class BaseWrapper:
    """Base command wrapper."""

    _f: Callable
    _parser: Any

    name: str

    def __init__(
        self,
        f: Callable,
        context: Optional[Context] = None,
        name: Optional[str] = None,
    ) -> None:
        """Initialize Command object.

        :param f: The base function to be called.
        :type f: Callable
        :param parser: The parser object that handles the command line arguments.
        :type parser: Parser
        :return: None
        """
        self._f = f
        self.context = context
        self.name = name or f.__name__

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """Call the base function.

        :param *args: Positional arguments.
        :type *args: Any
        :param **kwds: Keyword arguments.
        :type **kwds: Any
        :return: The return value of the base function.
        :rtype: Any
        """
        return self._f(*args, **kwds)

    def _invoke(
        self,
        args: Args,
        kwargs: Kwargs,
        isolated: bool = False,
        help_only: bool = False,
    ) -> int:
        """Command for command function."""
        if help_only:
            return self.help()
        try:
            self(*args, **kwargs)
            return 0
        except Exception:
            if isolated:
                return 1
            raise

    def help(self) -> int:
        """
        Print help string.

        :return: None
        """
        args = " ".join(self._parser.get_arg_vars())
        print(f"Usage: {self.name} [OPTIONS] {args}")
        print(f"\n\t{self.doc_full()}\n")
        print(f"Options:\n")
        for parameter in set(self._parser._kwargs.values()):
            print(f"    {parameter.help()}")
        print(f"    --help                        Show help and exit.")
        return 0

    def doc_one(self) -> str:
        """Returns the one line represenstion of the documentation."""
        doc, *_ = self.doc_full().splitlines()
        return doc

    def doc_full(self) -> str:
        """Returns the one line represenstion of the documentation."""
        return str(self._f.__doc__).lstrip().rstrip()

    def invoke(self, argv: Argv, isolated: bool = False) -> int:
        """Run the command."""
        return NotImplemented


class Command(BaseWrapper):
    """Command."""

    _parser: CommandParser

    def __init__(
        self,
        f: Callable,
        parser: CommandParser,
        context: Optional[Context] = None,
        name: Optional[str] = None,
    ) -> None:
        """Initialize Command object.

        :param f: The base function to be called.
        :type f: Callable
        :param parser: The parser object that handles the command line arguments.
        :type parser: Parser
        :return: None
        """
        super().__init__(f=f, context=context, name=name)
        self._parser = parser

    def invoke(self, argv: Argv, isolated: bool = False) -> int:
        """Run the command.

        :param argv: The command line arguments.
        :type argv: Argv
        :param isolated: Whether to run the command in an isolated context. Defaults to False.
        :type isolated: bool
        :return: 0 if the command runs successfully, 1 otherwise.
        :rtype: int
        """
        args, kwargs, help_only = self._parser.parse(argv=argv)
        return self._invoke(
            args=args, kwargs=kwargs, isolated=isolated, help_only=help_only
        )

    @classmethod
    def wrap(
        cls, f: Callable, context: Optional[Context] = None, **kwargs: Any
    ) -> "Command":
        """
        Decorator function to wrap a function as a command.

        :param f: The function to be wrapped.
        :type f: callable
        :return: A `Command` object representing the wrapped function.
        :rtype: Command
        """
        parser = CommandParser()
        context = context or Context()
        context_param = ContextParameter()
        context_param.name = "context"
        context_param.default = context
        defaults_mapping, annotations = get_function_metadata(f=f)
        for name, annotation in cast(Dict[str, Annotations], annotations).items():
            if name == "return":
                continue
            if name == "context":
                parser.add(defintion=context_param)
                continue
            (parameter,) = cast(
                Tuple[Parameter, ...], getattr(annotation, "__metadata__")
            )
            default = defaults_mapping.get(name)
            if default is not None:
                parameter.default = default
            parameter.name = name
            parser.add(defintion=parameter)
        return cls(f=f, parser=parser, **kwargs)


class Group(BaseWrapper):
    """Command group."""

    _children: Dict[str, Union[Command, "Group"]]

    def __init__(
        self,
        f: Callable,
        parser: GroupParser,
        context: Optional[Context] = None,
        name: Optional[str] = None,
        allow_direct_exec: bool = False,
    ) -> None:
        """Initialize Command object.

        :param f: The base function to be called.
        :type f: Callable
        :param parser: The parser object that handles the command line arguments.
        :type parser: Parser
        :return: None
        """
        super().__init__(f=f, context=context, name=name)

        self._parser = parser
        self._children = {}
        self._allow_direct_exec = allow_direct_exec

    @classmethod
    def wrap(
        cls, f: Callable, context: Optional[Context] = None, **kwargs: Any
    ) -> "Group":
        """
        Decorator function to wrap a function as a command.

        :param f: The function to be wrapped.
        :type f: callable
        :return: A `Command` object representing the wrapped function.
        :rtype: Command
        """
        parser = GroupParser()
        context = context or Context()
        context_param = ContextParameter()
        context_param.name = "context"
        context_param.default = context
        defaults_mapping, annotations = get_function_metadata(f=f)
        for name, annotation in cast(Dict[str, Annotations], annotations).items():
            if name == "return":
                continue
            if name == "context":
                parser.add(defintion=context_param)
                continue
            (parameter,) = cast(
                Tuple[Parameter, ...], getattr(annotation, "__metadata__")
            )
            default = defaults_mapping.get(name)
            if default is not None:
                parameter.default = default
            parameter.name = name
            parser.add(defintion=parameter)
        return cls(f=f, parser=parser, **kwargs)

    def invoke(self, argv: Argv, isolated: bool = False) -> int:
        """Run the command."""
        args, kwargs, help_only, sub_command, sub_argv = self._parser.parse(
            argv=argv, commands=self._children
        )
        exec_subcommand = sub_command is not None
        if exec_subcommand:
            self._invoke(
                args=args, kwargs=kwargs, isolated=isolated, help_only=help_only
            )
            return sub_command.invoke(argv=sub_argv)

        if self._allow_direct_exec:
            return self._invoke(
                args=args, kwargs=kwargs, isolated=isolated, help_only=help_only
            )
        return self.help()

    def command(self, f: Callable, name: Optional[str] = None) -> Command:
        """Command decorator."""
        wrapped = Command.wrap(f=f, context=self.context, name=name)
        self._children[wrapped.name] = wrapped
        return wrapped

    def group(
        self,
        f: Callable,
        name: Optional[str] = None,
        allow_direct_exec: bool = False,
    ) -> "Group":
        """Group decorator."""
        print(self, self.context)
        wrapped = Group.wrap(
            f=f,
            context=self.context,
            name=name,
            allow_direct_exec=allow_direct_exec,
        )
        self._children[wrapped.name] = wrapped
        return wrapped

    def help(self) -> int:
        """Print help string."""
        args = " ".join(self._parser.get_arg_vars())
        print(f"Usage: {self.name} [OPTIONS] {args}")
        print(f"\n\t{self.doc_full()}\n")
        print(f"Options:\n")
        for parameter in set(self._parser._kwargs.values()):
            print(f"    {parameter.help()}")
        print(f"    --help                        Show help and exit.")
        print(f"\nCommands:\n")
        for name, child in self._children.items():
            help_str = f"    {name}"
            help_str += " " * (HELP_COL_LENGTH - len(help_str))
            help_str += "    "
            help_str += child.doc_one()
            print(help_str)
        return 0


@overload
def command(f: Optional[Callable] = None) -> Command:
    """
    Decorator function to wrap a function as a command.

    :param f: The function to be wrapped.
    :type f: callable
    :return: A `Command` object representing the wrapped function.
    :rtype: Command
    """


@overload
def command(
    f: Optional[Callable] = None,
    name: Optional[str] = None,
    context: Optional[Context] = None,
) -> Callable[[Callable], Command]:
    """Command wrapper"""


def command(
    f: Optional[Callable] = None,
    name: Optional[str] = None,
    context: Optional[Context] = None,
) -> Callable[[Callable], Command]:
    """
    Decorator function to wrap a function as a command.

    :param f: The function to be wrapped.
    :type f: callable
    :return: A `Command` object representing the wrapped function.
    :rtype: Command
    """
    if f is not None:
        return Command.wrap(f=f, context=context)
    return partial(Command.wrap, name=name, context=context)


@overload
def group(f: Optional[Callable] = None) -> Group:
    """
    Decorator function to wrap a function as a command.

    :param f: The function to be wrapped.
    :type f: callable
    :return: A `Command` object representing the wrapped function.
    :rtype: Command
    """


@overload
def group(
    f: Optional[Callable] = None,
    name: Optional[str] = None,
    allow_direct_exec: bool = False,
    context: Optional[Context] = None,
) -> Callable[[Callable], Group]:
    """
    Decorator function to wrap a function as a command.

    :param f: The function to be wrapped.
    :type f: callable
    :return: A `Command` object representing the wrapped function.
    :rtype: Command
    """


def group(
    f: Optional[Callable] = None,
    name: Optional[str] = None,
    allow_direct_exec: bool = False,
    context: Optional[Context] = None,
) -> Callable[[Callable], Group]:
    """
    Decorator function to wrap a function as a command.

    :param f: The function to be wrapped.
    :type f: callable
    :return: A `Command` object representing the wrapped function.
    :rtype: Command
    """
    if f is not None:
        return Group.wrap(f=f, context=context)
    return partial(
        Group.wrap, name=name, allow_direct_exec=allow_direct_exec, context=context
    )
