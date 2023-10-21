"""Test params"""

import re
from enum import Enum
from pathlib import Path

import pytest

from clea.exceptions import ParsingError
from clea.params import (
    Boolean,
    Choice,
    ChoiceByFlag,
    Directory,
    File,
    Float,
    Integer,
    Parameter,
    String,
    StringList,
)


class _TestEnum(Enum):
    """Test enum"""

    ONE = "one"
    TWO = "two"


def test_parameter() -> None:
    """Test Parameter object."""
    param = Parameter("-p", "--parameter", help="Param.")

    assert param.default is None

    param.default = 1
    assert param.default == 1
    assert param.short_flag == "-p"
    assert param.long_flag == "--parameter"
    with pytest.raises(ValueError, match="'name' not defined."):
        param.name

    param.name = "param"
    assert param.var == "PARAM"
    assert "-p, --parameter               Param." in param.help()
    assert str(param) == "<parameter 'ParameterType'>"


def test_integer_parameter() -> None:
    """Test Integer object."""
    param = Integer(default=1)
    param.name = "param"
    with pytest.raises(
        ParsingError,
        match="Error parsing value for <PARAM type=int>; Provided value=a; Expected type=int",
    ):
        param.parse("a")
    assert param.parse("3") == 3


def test_string_parameter() -> None:
    """Test String object."""
    param = String(default="p")
    param.name = "param"
    assert param.default == "p"
    assert param.parse("3") == "3"


def test_float_parameter() -> None:
    """Test Float object."""
    param = Float(default=0.1)
    param.name = "param"
    with pytest.raises(
        ParsingError,
        match="Error parsing value for <PARAM type=float>; Provided value=a; Expected type=float",
    ):
        param.parse("a")
    assert param.parse("3") == 3.0


def test_boolean_parameter() -> None:
    """Test Boolean object."""
    param = Boolean()
    param.name = "param"
    assert param.default is False
    assert param.parse(None) is True


def test_boolean_parameter_inverse() -> None:
    """Test Boolean object."""
    param = Boolean(default=True)
    param.name = "param"
    assert param.default is True
    assert param.parse(None) is False


def test_string_list_parameter() -> None:
    """Test StringList object."""
    param = StringList("-p", "--param", help="Param")
    param.name = "param"
    assert param.parse("hello") == ["hello"]
    assert param.help() == "-p, --param                   Param"


def test_choice_parameter() -> None:
    """Test Choice object."""
    param = Choice(_TestEnum, "-p", help="Choice")
    param.name = "param"
    with pytest.raises(
        ParsingError,
        match="Error parsing value for <PARAM type=Enum>; Provided value=three; Expected value from",
    ):
        param.parse("three")
    assert param.parse("one") == _TestEnum.ONE
    assert param.help() == "-p, --param  [one|two]        Choice"


def test_choice_by_flag_parameter() -> None:
    """Test ChoiceByFlag object."""
    param = ChoiceByFlag(_TestEnum, help="Choice")
    param.name = "param"
    with pytest.raises(
        ParsingError,
        match="Error parsing value for <PARAM type=Enum>; Provided value=three; Expected value from",
    ):
        param.parse("three")
    assert param.parse("--one") == _TestEnum.ONE
    assert param.parse("--two") == _TestEnum.TWO
    assert param.help() == "--one, --two                  Choice"


def test_file_parameter() -> None:
    """Test File object."""
    param = File(exists=True)
    param.name = "param"
    with pytest.raises(
        ParsingError,
        match="Invalid value for --param provided path `.` is not a file",
    ):
        param.parse("./")
    with pytest.raises(
        ParsingError,
        match="Invalid value for --param provided path `hello` does not exist",
    ):
        param.parse("./hello")
    assert param.parse("./tox.ini") == Path("./tox.ini")

    param.resolve = True
    assert param.parse("./tox.ini") == Path("./tox.ini").resolve()


def test_directory_parameter() -> None:
    """Test File object."""
    param = Directory(exists=True)
    param.name = "param"
    with pytest.raises(
        ParsingError,
        match="Invalid value for --param provided path `tox.ini` is not a directory",
    ):
        param.parse("./tox.ini")
    with pytest.raises(
        ParsingError,
        match="Invalid value for --param provided path `hello` does not exist",
    ):
        param.parse("./hello")
    assert param.parse("./") == Path("./")

    param.resolve = True
    assert param.parse("./") == Path("./").resolve()

