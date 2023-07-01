"""Parameter definition."""

from enum import Enum
from pathlib import Path
from typing import Any, Generic, List, Optional, Type, TypeVar, cast, get_args

from clea.context import Context
from clea.exceptions import ParsingError


ParameterType = TypeVar("ParameterType")

HELP_COL_LENGTH = 30


class Parameter(Generic[ParameterType]):
    """Callable parameter."""

    _name: Optional[str]
    _type: Type

    container: List
    is_container: bool = False

    def __init__(
        self,
        short_flag: Optional[str] = None,
        long_flag: Optional[str] = None,
        default: Optional[ParameterType] = None,
        help: Optional[str] = None,
        env: Optional[str] = None,
    ) -> None:
        """Initialize object."""
        self._name = None

        self._short_flag = short_flag
        self._long_flag = long_flag
        self._default = default
        self._help = help
        self._env = env

        (self._type,) = get_args(self.__orig_bases__[0])  # type: ignore

    @property
    def short_flag(self) -> Optional[str]:
        """FLag"""
        return self._short_flag

    @property
    def long_flag(self) -> str:
        """FLag"""
        if self._long_flag is not None:
            return self._long_flag
        return "--" + cast(str, self.name).replace("_", "-")

    @property
    def default(self) -> Optional[ParameterType]:
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

    def parse(self, value: Any) -> ParameterType:
        """
        Parse the object.

        :param value: The value to be parsed.
        :type value: Any
        :return: The parsed object.
        :rtype: ParameterType
        """
        try:
            return self._type(value)
        except ValueError as e:
            raise ParsingError(
                f"Error parsing value for {self.metavar}; Provided value={value}; Expected type={self._type.__name__}"
            ) from e

    def help(self) -> str:
        """Help string."""
        if self.short_flag is not None:
            help_string = f"{self.short_flag}, "
        else:
            help_string = f""
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
        short_flag: Optional[str] = None,
        long_flag: Optional[str] = None,
        default: bool = False,
        help: Optional[str] = None,
        env: Optional[str] = None,
    ) -> None:
        super().__init__(short_flag, long_flag, default, help, env)

    def parse(self, value: Any) -> bool:
        """Parse result"""
        return not self.default


class StringList(Parameter[List[str]]):
    """String list parameter."""

    container: List[str]
    is_container: bool = True

    def __init__(
        self,
        short_flag: Optional[str] = None,
        long_flag: Optional[str] = None,
        default: Optional[List[str]] = None,
        help: Optional[str] = None,
        env: Optional[str] = None,
    ) -> None:
        super().__init__(short_flag, long_flag, default or [], help, env)
        self.container = []

    def parse(self, value: Any) -> List[str]:
        """
        Parse as list of strings.

        :param value: The value to be parsed.
        :type value: Any
        :return: The parsed object.
        :rtype: ParameterType
        """
        self.container.append(str(value))
        return self.container

    def help(self) -> str:
        """Help string."""
        if self.short_flag is not None:
            help_string = f"{self.short_flag}, "
        else:
            help_string = f""
        help_string += f"{self.long_flag}"
        if self._help is not None:
            help_string += " " * (HELP_COL_LENGTH - len(help_string))
            help_string += self._help
        return help_string


class Choice(Parameter[Enum]):
    """Choice parameter."""

    def __init__(
        self,
        enum: Type[Enum],
        short_flag: Optional[str] = None,
        long_flag: Optional[str] = None,
        default: Optional[Enum] = None,
        help: Optional[str] = None,
        env: Optional[str] = None,
    ) -> None:
        super().__init__(short_flag, long_flag, default, help, env)
        self.enum = enum

    def parse(self, value: Any) -> Enum:
        """
        Parse choice.

        :param value: The value to be parsed.
        :type value: Any
        :return: The parsed object.
        :rtype: ParameterType
        """
        try:
            return self.enum(value=value)
        except ValueError as e:
            raise ParsingError(
                f"Error parsing value for {self.metavar}; Provided value={value}; "
                f"Expected value from {set(map(lambda x:x.value, self.enum))}"
            ) from e

    def help(self) -> str:
        """Help string."""
        if self.short_flag is not None:
            help_string = f"{self.short_flag}, "
        else:
            help_string = f""
        help_string += f"{self.long_flag}"
        choices = "|".join(list(map(lambda x: x.value, self.enum)))
        help_string += f"  [{choices}]"
        if self._help is not None:
            str_len = len(help_string)
            if str_len < HELP_COL_LENGTH:
                help_string += " " * (HELP_COL_LENGTH - str_len)
                help_string += self._help
            else:
                help_string += "\n"
                help_string += " " * HELP_COL_LENGTH
                help_string += f"    {self._help}"
        return help_string


class ChoiceByFlag(Parameter[Enum]):
    """Choice parameter."""

    def __init__(
        self,
        enum: Type[Enum],
        default: Optional[Enum] = None,
        help: Optional[str] = None,
        env: Optional[str] = None,
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
        :type value: Any
        :return: The parsed object.
        :rtype: ParameterType
        """
        try:
            self._default = self.flag_to_value[value]
            return self._default
        except (KeyError, ValueError) as e:
            raise ParsingError(
                f"Error parsing value for {self.metavar}; Provided value={value}; "
                f"Expected value from {set(map(lambda x:x.value, self.enum))}"
            ) from e

    def help(self) -> str:
        """Help string."""
        help_string = ", ".join(self.flag_to_value)
        if self._help is not None:
            str_len = len(help_string)
            if str_len < HELP_COL_LENGTH:
                help_string += " " * (HELP_COL_LENGTH - str_len)
                help_string += self._help
            else:
                help_string += "\n"
                help_string += " " * HELP_COL_LENGTH
                help_string += f"    {self._help}"
        return help_string


class File(Parameter[Path]):
    """File path parameter."""

    def __init__(
        self,
        short_flag: Optional[str] = None,
        long_flag: Optional[str] = None,
        exists: bool = False,
        resolve: bool = False,
        default: Optional[Path] = None,
        help: Optional[str] = None,
        env: Optional[str] = None,
    ) -> None:
        super().__init__(short_flag, long_flag, default, help, env)
        self.exists = exists
        self.resolve = resolve

    def parse(self, value: Any) -> Path:
        """
        Parse path string.

        :param value: The value to be parsed.
        :type value: Any
        :return: The parsed object.
        :rtype: ParameterType
        """
        path = super().parse(value=value)
        flag = self.short_flag or self.long_flag
        exists = path.exists()
        if self.exists and not path.exists():
            raise ParsingError(
                f"Invalid value for {flag} provided path `{path}` does not exist"
            )
        if exists and not path.is_file():
            raise ParsingError(
                f"Invalid value for {flag} provided path `{path}` is not a file"
            )
        if self.resolve:
            return path.resolve()
        return path


class Directory(Parameter[Path]):
    """Directory parameter."""

    def __init__(
        self,
        short_flag: Optional[str] = None,
        long_flag: Optional[str] = None,
        exists: bool = False,
        resolve: bool = False,
        default: Optional[Path] = None,
        help: Optional[str] = None,
        env: Optional[str] = None,
    ) -> None:
        super().__init__(short_flag, long_flag, default, help, env)

        self.exists = exists
        self.resolve = resolve

    def parse(self, value: Any) -> Path:
        """
        Parse path string.

        :param value: The value to be parsed.
        :type value: Any
        :return: The parsed object.
        :rtype: ParameterType
        """
        path = super().parse(value=value)
        flag = self.short_flag or self.long_flag
        exists = path.exists()
        if self.exists and not exists:
            raise ParsingError(
                f"Invalid value for {flag} provided path `{path}` does not exist"
            )
        if exists and not path.is_dir():
            raise ParsingError(
                f"Invalid value for {flag} provided path `{path}` is not a directory"
            )
        if self.resolve:
            return path.resolve()
        return path


class ContextParameter(Parameter[Context]):
    """Context parameter."""
