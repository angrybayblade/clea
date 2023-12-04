"""
Single command implementation.

This module provides a Command class that represents a single command implementation.
"""


import typing as t
from functools import partial

import clea.params as p
from clea.context import Context
from clea.helpers import get_function_metadata
from clea.parser import Args, Argv, CommandParser, GroupParser, Kwargs


Annotations = t.Dict[str, p.Parameter]


class BaseWrapper:
    """Base command wrapper."""

    _f: t.Callable
    _parser: t.Union[CommandParser, GroupParser]

    name: str
    version: t.Optional[str]
    parent: t.Optional["Group"]

    def __init__(
        self,
        f: t.Callable,
        context: t.Optional[Context] = None,
        name: t.Optional[str] = None,
        version: t.Optional[str] = None,
        parent: t.Optional["Group"] = None,
    ) -> None:
        """Initialize Command object.

        :param f: The base function to be called.
        :type f: t.Callable
        :param parser: The parser object that handles the command line arguments.
        :type parser: Parser
        :return: None
        """
        self._f = f
        self.context = context
        self.name = name or f.__name__
        self.version = version
        self.parent = parent

    def __call__(self, *args: t.Any, **kwds: t.Any) -> t.Any:
        """Call the base function.

        :param *args: Positional arguments.
        :type *args: t.Any
        :param **kwds: Keyword arguments.
        :type **kwds: t.Any
        :return: The return value of the base function.
        :rtype: t.Any
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

    def set_context(self, context: Context) -> None:
        """Set context."""
        self.context = context
        self._parser.set_context(context=context)

    def help(self) -> int:
        """
        Print help string.

        :return: None
        """
        args = " ".join(self._parser.get_arg_vars())
        print(f"Usage: {self.name} [OPTIONS] {args}")
        print(f"\n\t{self.doc_full()}\n")
        print("Options:\n")
        for parameter in set(
            self._parser._kwargs.values()  # pylint: disable=protected-access
        ):
            if parameter.name == "context":
                continue  # pragma: nocover
            print(f"    {parameter.help()}")
        print("    --help                        Show help and exit.")
        return 0

    def doc_one(self) -> str:
        """Returns the one line represenstion of the documentation."""
        doc, *_ = self.doc_full().splitlines()
        return doc

    def doc_full(self) -> str:
        """Returns the one line represenstion of the documentation."""
        return str(self._f.__doc__).lstrip().rstrip()

    def invoke(  # pylint: disable=unused-argument
        self, argv: Argv, isolated: bool = False
    ) -> int:
        """Run the command."""
        return NotImplemented  # pragma: nocover


class Command(BaseWrapper):
    """Command."""

    _parser: CommandParser

    def __init__(
        self,
        f: t.Callable,
        parser: CommandParser,
        context: t.Optional[Context] = None,
        name: t.Optional[str] = None,
        version: t.Optional[str] = None,
        parent: t.Optional["Group"] = None,
    ) -> None:
        """Initialize Command object.

        :param f: The base function to be called.
        :type f: t.Callable
        :param parser: The parser object that handles the command line arguments.
        :type parser: Parser
        :return: None
        """
        super().__init__(
            f=f, context=context, name=name, version=version, parent=parent
        )
        self._parser = parser
        if self.parent is not None:
            self.parent.add_child(self)

    def invoke(self, argv: Argv, isolated: bool = False) -> int:
        """Run the command.

        :param argv: The command line arguments.
        :type argv: Argv
        :param isolated: Whether to run the command in an isolated context. Defaults to False.
        :type isolated: bool
        :return: 0 if the command runs successfully, 1 otherwise.
        :rtype: int
        """
        args, kwargs, help_only, version_only = self._parser.copy().parse(argv=argv)
        if version_only:
            print(self.version)
            return 0
        return self._invoke(
            args=args, kwargs=kwargs, isolated=isolated, help_only=help_only
        )

    @t.overload
    @classmethod
    def wrap(
        cls,
        f: t.Optional[t.Callable] = None,
    ) -> "Command":
        """
        Decorator function to wrap a function as a command.

        :param f: The function to be wrapped.
        :type f: t.callable
        :return: A `Command` object representing the wrapped function.
        :rtype: Command
        """

    @t.overload
    @classmethod
    def wrap(
        cls,
        f: t.Optional[t.Callable] = None,
        name: t.Optional[str] = None,
        context: t.Optional[Context] = None,
        parent: t.Optional["Group"] = None,
        version: t.Optional[str] = None,
    ) -> t.Callable[[t.Callable], "Command"]:
        """Command wrapper"""

    @classmethod
    def wrap(
        cls,
        f: t.Optional[t.Callable] = None,
        name: t.Optional[str] = None,
        context: t.Optional[Context] = None,
        parent: t.Optional["Group"] = None,
        version: t.Optional[str] = None,
    ) -> t.Callable[[t.Callable], "Command"]:
        """
        Decorator function to wrap a function as a command.

        :param f: The function to be wrapped.
        :type f: t.callable
        :return: A `Command` object representing the wrapped function.
        :rtype: Command
        """
        if f is not None:
            return cls._wrap(f=f, context=context, parent=parent)
        return partial(
            cls._wrap, name=name, context=context, parent=parent, version=version
        )

    @classmethod
    def _wrap(
        cls,
        f: t.Callable,
        context: t.Optional[Context] = None,
        version: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> "Command":
        """
        Decorator function to wrap a function as a command.

        :param f: The function to be wrapped.
        :type f: t.callable
        :return: A `Command` object representing the wrapped function.
        :rtype: Command
        """
        parser = CommandParser()
        context = context or Context()
        if version:
            version_param = p.VersionParameter(
                long_flag="--version",
                help="Program version",
            )
            version_param.name = "version"
            version_param.default = version
            parser.add(version_param)
        defaults_mapping, annotations = get_function_metadata(f=f)
        for name, annotation in t.cast(t.Dict[str, Annotations], annotations).items():
            if name == "return":
                continue
            if name == "context":
                context_param = p.ContextParameter()
                context_param.name = "context"
                context_param.default = context
                parser.add(defintion=context_param)
                continue
            (parameter,) = t.cast(
                t.Tuple[p.Parameter, ...], getattr(annotation, "__metadata__")
            )
            default = defaults_mapping.get(name)
            if default is not None:
                parameter.default = default
            parameter.name = name
            parser.add(defintion=parameter)
        return cls(f=f, parser=parser, version=version, **kwargs)


class Group(BaseWrapper):
    """Command group."""

    _children: t.Dict[str, t.Union[Command, "Group"]]

    def __init__(
        self,
        f: t.Callable,
        parser: GroupParser,
        context: t.Optional[Context] = None,
        name: t.Optional[str] = None,
        version: t.Optional[str] = None,
        allow_direct_exec: bool = False,
        parent: t.Optional["Group"] = None,
    ) -> None:
        """Initialize Command object.

        :param f: The base function to be called.
        :type f: t.Callable
        :param parser: The parser object that handles the command line arguments.
        :type parser: Parser
        :return: None
        """
        super().__init__(
            f=f,
            context=context,
            name=name,
            version=version,
            parent=parent,
        )

        self._children = {}
        self._parser = parser
        self._allow_direct_exec = allow_direct_exec
        if self.parent is not None:
            self.parent.add_child(self)

        self.command = partial(Command.wrap, parent=self, context=self.context)
        self.group = partial(self.wrap, parent=self, context=self.context)

    def add_child(self, child: t.Union[Command, "Group"]) -> None:
        """Add child node."""
        if self.context is not None:
            child.set_context(context=self.context)
        self._children[t.cast(BaseWrapper, child).name] = child

    @classmethod
    def _wrap(
        cls,
        f: t.Callable,
        context: t.Optional[Context] = None,
        version: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> "Group":
        """
        Decorator function to wrap a function as a command.

        :param f: The function to be wrapped.
        :type f: t.callable
        :return: A `Command` object representing the wrapped function.
        :rtype: Command
        """
        parser = GroupParser()
        context = context or Context()
        if version:
            version_param = p.VersionParameter(
                long_flag="--version",
                help="Program version",
            )
            version_param.name = "version"
            version_param.default = version
            parser.add(version_param)
        defaults_mapping, annotations = get_function_metadata(f=f)
        for name, annotation in t.cast(t.Dict[str, Annotations], annotations).items():
            if name == "return":
                continue
            if name == "context":
                context_param = p.ContextParameter()
                context_param.name = "context"
                context_param.default = context
                parser.add(defintion=context_param)
                continue
            (parameter,) = t.cast(
                t.Tuple[p.Parameter, ...], getattr(annotation, "__metadata__")
            )
            default = defaults_mapping.get(name)
            if default is not None:
                parameter.default = default
            parameter.name = name
            parser.add(defintion=parameter)
        return cls(f=f, parser=parser, context=context, version=version, **kwargs)

    @t.overload
    @classmethod
    def wrap(
        cls,
        f: t.Optional[t.Callable] = None,
    ) -> "Group":
        """
        Decorator function to wrap a function as a command.

        :param f: The function to be wrapped.
        :type f: t.callable
        :return: A `Command` object representing the wrapped function.
        :rtype: Command
        """

    @t.overload
    @classmethod
    def wrap(
        cls,
        f: t.Optional[t.Callable] = None,
        name: t.Optional[str] = None,
        allow_direct_exec: bool = False,
        context: t.Optional[Context] = None,
        parent: t.Optional["Group"] = None,
        version: t.Optional[str] = None,
    ) -> t.Callable[[t.Callable], "Group"]:
        """
        Decorator function to wrap a function as a command.

        :param f: The function to be wrapped.
        :type f: t.callable
        :return: A `Command` object representing the wrapped function.
        :rtype: Command
        """

    @classmethod
    def wrap(
        cls,
        f: t.Optional[t.Callable] = None,
        name: t.Optional[str] = None,
        allow_direct_exec: bool = False,
        context: t.Optional[Context] = None,
        parent: t.Optional["Group"] = None,
        version: t.Optional[str] = None,
    ) -> t.Callable[[t.Callable], "Group"]:
        """
        Decorator function to wrap a function as a command.

        :param f: The function to be wrapped.
        :type f: t.callable
        :return: A `Command` object representing the wrapped function.
        :rtype: Command
        """
        if f is not None:
            return cls._wrap(f=f, context=context, parent=parent)
        return partial(
            cls._wrap,
            name=name,
            allow_direct_exec=allow_direct_exec,
            context=context,
            parent=parent,
            version=version,
        )

    def invoke(self, argv: Argv, isolated: bool = False) -> int:
        """Run the command."""
        (
            args,
            kwargs,
            help_only,
            version_only,
            sub_command,
            sub_argv,
        ) = (
            t.cast(GroupParser, self._parser)
            .copy()
            .parse(argv=argv, commands=self._children)
        )

        if version_only:
            print(self.version)
            return 0

        if sub_command is not None:
            self._invoke(
                args=args, kwargs=kwargs, isolated=isolated, help_only=help_only
            )
            return sub_command.invoke(argv=sub_argv)

        if self._allow_direct_exec:
            return self._invoke(
                args=args, kwargs=kwargs, isolated=isolated, help_only=help_only
            )

        return self.help()

    def help(self) -> int:
        """Print help string."""
        args = " ".join(self._parser.get_arg_vars())
        print(f"Usage: {self.name} [OPTIONS] {args}")
        print(f"\n\t{self.doc_full()}\n")
        print("Options:\n")
        for parameter in set(
            self._parser._kwargs.values()  # pylint: disable=protected-access
        ):
            if parameter.name == "context":
                continue  # pragma: nocover
            print(f"    {parameter.help()}")
        print("    --help                        Show help and exit.")
        print("\nCommands:\n")
        for name, child in self._children.items():
            help_str = f"    {name}"
            help_str += " " * (p.HELP_COL_LENGTH - len(help_str))
            help_str += "    "
            help_str += child.doc_one()
            print(help_str)
        return 0


command = Command.wrap
group = Group.wrap
