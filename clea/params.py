"""Parameter definition."""

import typing as t
from enum import Enum
from pathlib import Path

from clea.context import Context
from clea.exceptions import ParsingError


ParameterType = t.TypeVar("ParameterType")

HELP_COL_LENGTH = 30


class Parameter(t.Generic[ParameterType]):
    """Callable parameter."""

    _name: t.Optional[str]
    _type: t.Type

    container: t.List
    is_container: bool = False

    def __init__(
        self,
        short_flag: t.Optional[str] = None,
        long_flag: t.Optional[str] = None,
        default: t.Optional[ParameterType] = None,
        help: t.Optional[str] = None,  # pylint: disable=redefined-builtin
        env: t.Optional[str] = None,
    ) -> None:
        """Initialize object."""
        self._name = None

        self._short_flag = short_flag
        self._long_flag = long_flag
        self._default = default
        self._help = help
        self._env = env

        (self._type,) = t.get_args(self.__orig_bases__[0])  # type: ignore # pylint: disable=no-member

    @property
    def short_flag(self) -> t.Optional[str]:
        """FLag"""
        return self._short_flag

    @property
    def long_flag(self) -> t.Optional[str]:
        """FLag"""
        return self._long_flag

    def create_long_flag(self) -> str:
        """Set the value of long flag."""
        self._long_flag = "--" + t.cast(str, self.name).replace("_", "-")
        return self._long_flag

    @property
    def default(self) -> t.Optional[ParameterType]:
        """Return default value."""
        return self._default

    @default.setter
    def default(self, value: ParameterType) -> None:
        """Set default."""
        self._default = value

    @property
    def name(self) -> str:
        """Name"""
        if self._name is None:
            raise ValueError("'name' not defined.")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Name"""
        self._name = value

    @property
    def metavar(self) -> str:
        """Metavar name"""
        return f"<{self.name.upper()} type={self._type.__name__}>"

    @property
    def var(self) -> str:
        """Var name"""
        return self.name.upper()

    def parse(self, value: t.Any) -> ParameterType:
        """
        Parse the object.

        :param value: The value to be parsed.
        :type value: t.Any
        :return: The parsed object.
        :rtype: ParameterType
        """
        try:
            return self._type(value)
        except ValueError as e:
            raise ParsingError(
                message=f"Error parsing value for {self.metavar}; Provided value={value}; Expected type={self._type.__name__}",
                exit_code=1,
            ) from e

    def help(self) -> str:
        """Help string."""
        if self.short_flag is not None:
            help_string = f"{self.short_flag}, "
            if self.long_flag is not None:
                help_string += f"{self.long_flag}, "
            help_string = help_string[:-2]
        else:  # pragma: nocover
            help_string = ""
            if self.long_flag is not None:
                help_string += f"{self.long_flag}"

        if self._help is not None:
            help_string += " " * (HELP_COL_LENGTH - len(help_string))
            help_string += self._help
        return help_string

    def __repr__(self) -> str:
        """String representation."""
        return f"<parameter '{self._type.__name__}'>"


class String(Parameter[str]):
    """String parameter."""


class Integer(Parameter[int]):
    """String parameter."""


class Float(Parameter[float]):
    """String parameter."""


class Boolean(Parameter[bool]):
    """Boolean flag parameter."""

    def __init__(
        self,
        short_flag: t.Optional[str] = None,
        long_flag: t.Optional[str] = None,
        default: bool = False,
        help: t.Optional[str] = None,  # pylint: disable=redefined-builtin
        env: t.Optional[str] = None,
    ) -> None:
        super().__init__(short_flag, long_flag, default, help, env)

    def parse(self, value: t.Any) -> bool:
        """Parse result"""
        return not self.default


class StringList(Parameter[t.List[str]]):
    """String list parameter."""

    container: t.List[str]
    is_container: bool = True

    def __init__(
        self,
        short_flag: t.Optional[str] = None,
        long_flag: t.Optional[str] = None,
        default: t.Optional[t.List[str]] = None,
        help: t.Optional[str] = None,  # pylint: disable=redefined-builtin
        env: t.Optional[str] = None,
    ) -> None:
        super().__init__(short_flag, long_flag, default or [], help, env)
        self.container = []

    def parse(self, value: t.Any) -> t.List[str]:
        """
        Parse as t.list of strings.

        :param value: The value to be parsed.
        :type value: t.Any
        :return: The parsed object.
        :rtype: ParameterType
        """
        self.container.append(str(value))
        return self.container

    def help(self) -> str:
        if self.short_flag is not None:
            help_string = f"{self.short_flag}, "
            if self.long_flag is not None:
                help_string += f"{self.long_flag}, "
            help_string = help_string[:-2]
        else:  # pragma: nocover
            help_string = ""
            if self.long_flag is not None:
                help_string += f"{self.long_flag}"

        if self._help is not None:
            help_string += " " * (HELP_COL_LENGTH - len(help_string))
            help_string += self._help
        return help_string


class Choice(Parameter[Enum]):
    """Choice parameter."""

    def __init__(
        self,
        enum: t.Type[Enum],
        short_flag: t.Optional[str] = None,
        long_flag: t.Optional[str] = None,
        default: t.Optional[Enum] = None,
        help: t.Optional[str] = None,  # pylint: disable=redefined-builtin
        env: t.Optional[str] = None,
    ) -> None:
        super().__init__(short_flag, long_flag, default, help, env)
        self.enum = enum

    def parse(self, value: t.Any) -> Enum:
        """
        Parse choice.

        :param value: The value to be parsed.
        :type value: t.Any
        :return: The parsed object.
        :rtype: ParameterType
        """
        try:
            return self.enum(value=value)
        except ValueError as e:
            raise ParsingError(
                message=f"Error parsing value for {self.metavar}; Provided value={value}; Expected value from {set(map(lambda x:x.value, self.enum))}",
                exit_code=1,
            ) from e

    def help(self) -> str:
        """Help string."""
        if self.short_flag is not None:
            help_string = f"{self.short_flag}, "
            if self.long_flag is not None:
                help_string += f"{self.long_flag}, "
            help_string = help_string[:-2]
        else:  # pragma: nocover
            help_string = ""
            if self.long_flag is not None:
                help_string += f"{self.long_flag}"

        choices = "|".join(list(map(lambda x: x.value, self.enum)))
        help_string += f"  [{choices}]"
        if self._help is not None:
            str_len = len(help_string)
            if str_len < HELP_COL_LENGTH:
                help_string += " " * (HELP_COL_LENGTH - str_len)
                help_string += self._help
            else:  # pragma: nocover # TODO
                help_string += "\n"
                help_string += " " * HELP_COL_LENGTH
                help_string += f"    {self._help}"
        return help_string


class ChoiceByFlag(Parameter[Enum]):
    """Choice parameter."""

    def __init__(
        self,
        enum: t.Type[Enum],
        default: t.Optional[Enum] = None,
        help: t.Optional[str] = None,  # pylint: disable=redefined-builtin
        env: t.Optional[str] = None,
    ) -> None:
        super().__init__(None, None, default, help, env)
        self.enum = enum
        self.flag_to_value = {}
        for choice in enum:
            long_flag = "--" + choice.name.lower().replace("_", "-")
            self.flag_to_value[long_flag] = choice

    def parse(self, value: str) -> Enum:
        """
        Parse choice.

        :param value: The value to be parsed.
        :type value: t.Any
        :return: The parsed object.
        :rtype: ParameterType
        """
        try:
            self._default = self.flag_to_value[value]
            return self._default
        except (KeyError, ValueError) as e:
            raise ParsingError(
                message=f"Error parsing value for {self.metavar}; Provided value={value}; Expected value from {set(map(lambda x:x.value, self.enum))}",
                exit_code=1,
            ) from e

    def help(self) -> str:
        """Help string."""
        help_string = ", ".join(self.flag_to_value)
        if self._help is not None:
            str_len = len(help_string)
            if str_len < HELP_COL_LENGTH:
                help_string += " " * (HELP_COL_LENGTH - str_len)
                help_string += self._help
            else:  # pragma: nocover # TODO
                help_string += "\n"
                help_string += " " * HELP_COL_LENGTH
                help_string += f"    {self._help}"
        return help_string


class File(Parameter[Path]):
    """File path parameter."""

    def __init__(
        self,
        short_flag: t.Optional[str] = None,
        long_flag: t.Optional[str] = None,
        exists: bool = False,
        resolve: bool = False,
        default: t.Optional[Path] = None,
        help: t.Optional[str] = None,  # pylint: disable=redefined-builtin
        env: t.Optional[str] = None,
    ) -> None:
        super().__init__(short_flag, long_flag, default, help, env)
        self.exists = exists
        self.resolve = resolve

    def parse(self, value: t.Any) -> Path:
        """
        Parse path string.

        :param value: The value to be parsed.
        :type value: t.Any
        :return: The parsed object.
        :rtype: ParameterType
        """
        path = super().parse(value=value)
        flag = self.short_flag or self.long_flag
        exists = path.exists()
        if self.exists and not path.exists():
            raise ParsingError(
                message=f"Invalid value for {flag} provided path `{path}` does not exist",
                exit_code=1,
            )
        if exists and not path.is_file():
            raise ParsingError(
                message=f"Invalid value for {flag} provided path `{path}` is not a file",
                exit_code=1,
            )
        if self.resolve:
            return path.resolve()
        return path


class Directory(Parameter[Path]):
    """Directory parameter."""

    def __init__(
        self,
        short_flag: t.Optional[str] = None,
        long_flag: t.Optional[str] = None,
        exists: bool = False,
        resolve: bool = False,
        default: t.Optional[Path] = None,
        help: t.Optional[str] = None,  # pylint: disable=redefined-builtin
        env: t.Optional[str] = None,
    ) -> None:
        super().__init__(short_flag, long_flag, default, help, env)

        self.exists = exists
        self.resolve = resolve

    def parse(self, value: t.Any) -> Path:
        """
        Parse path string.

        :param value: The value to be parsed.
        :type value: t.Any
        :return: The parsed object.
        :rtype: ParameterType
        """
        path = super().parse(value=value)
        flag = self.short_flag or self.long_flag
        exists = path.exists()
        if self.exists and not exists:
            raise ParsingError(
                message=f"Invalid value for {flag} provided path `{path}` does not exist",
                exit_code=1,
            )
        if exists and not path.is_dir():
            raise ParsingError(
                message=f"Invalid value for {flag} provided path `{path}` is not a directory",
                exit_code=1,
            )
        if self.resolve:
            return path.resolve()
        return path


class ContextParameter(Parameter[Context]):
    """Context parameter."""

    def set(self, context: Context) -> None:
        """Set context."""
        self._default = context


class VersionParameter(Parameter[str]):
    """Version parameter."""
