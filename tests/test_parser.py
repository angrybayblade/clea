"""Test parser module."""

import typing as t

import pytest

from clea.exceptions import ExtraArgumentProvided, ArgumentsMissing
from clea.params import Boolean, ContextParameter, String, StringList, VersionParameter
from clea.parser import BaseParser, CommandParser, GroupParser
from clea.runner import run


@pytest.mark.parametrize(
    "Parser",
    argvalues=(
        CommandParser,
        GroupParser,
    ),
)
class TestBaseFunctionality:
    """Test commmand parser."""

    def get_param(self) -> String:
        """Get string parameter."""
        param = String(short_flag="-p", long_flag="--param", default="foo")
        param.name = "param"
        return param

    def test_parse_args(self, Parser: t.Type[BaseParser]) -> None:
        """Test short flag parsing."""
        param = String()
        param.name = "param"
        parser = Parser()
        parser.add(param)

        args, *_ = parser.parse(["hello"])
        assert args == ["hello"]

    def test_missing_arg(self, Parser: t.Type[BaseParser]) -> None:
        """Test short flag parsing."""
        param = String()
        param.name = "param"
        parser = Parser()
        parser.add(param)
        with pytest.raises(
            ArgumentsMissing,
            match="Missing argument for positional arguments <PARAM type=str>",
        ):
            parser.parse([])

    def test_extra_args(self, Parser: t.Type[BaseParser]) -> None:
        """Test short flag parsing."""
        with pytest.raises(
            ExtraArgumentProvided, match="Extra argument provided `hello`"
        ):
            Parser().parse(["hello"])

    def test_short_flag_parsing(self, Parser: t.Type[BaseParser]) -> None:
        """Test short flag parsing."""
        parser = Parser()
        parser.add(defintion=self.get_param())
        _, kwargs, *_ = parser.parse(["-p=bar"])
        assert kwargs == {"param": "bar"}

    def test_long_flag_parsing(self, Parser: t.Type[BaseParser]) -> None:
        """Test long flag parsing."""
        parser = Parser()
        parser.add(defintion=self.get_param())
        _, kwargs, *_ = parser.parse(["--param=bar"])
        assert kwargs == {"param": "bar"}

    def test_extra_flag(self, Parser: t.Type[BaseParser]) -> None:
        """Test extra argument."""
        with pytest.raises(
            ExtraArgumentProvided, match="Extra argument provided with flag `--param`"
        ):
            Parser().parse(["--param=hello"])

    def test_parse_container(self, Parser: t.Type[BaseParser]) -> None:
        """Test extra argument."""
        parser = Parser()
        param = StringList(short_flag="-p", long_flag="--param")
        param.name = "param"
        parser.add(defintion=param)

        _, kwargs, *_ = parser.parse(["-p=foo", "--param=bar"])
        assert kwargs["param"] == ["foo", "bar"]

    def test_parse_switch(self, Parser: t.Type[BaseParser]) -> None:
        """Test extra argument."""
        parser = Parser()
        param = Boolean(long_flag="--param")
        param.name = "param"
        parser.add(defintion=param)

        _, kwargs, *_ = parser.parse(["--param"])
        assert kwargs["param"] is True

    def test_parse_switch_default(self, Parser: t.Type[BaseParser]) -> None:
        """Test extra argument."""
        parser = Parser()
        param = Boolean(long_flag="--param")
        param.name = "param"
        parser.add(defintion=param)
        _, kwargs, *_ = parser.parse([])
        assert kwargs["param"] is False

    def test_parse_version(self, Parser: t.Type[BaseParser]) -> None:
        """Test version argument."""
        parser = Parser()
        version = VersionParameter(long_flag="--version")
        version.name = "version"
        parser.add(version)

        _, _, _, version_only, *_ = parser.parse(["--version"])
        assert version_only is True

    def test_parse_help(self, Parser: t.Type[BaseParser]) -> None:
        """Test version argument."""
        parser = Parser()
        _, _, help_only, _, *_ = parser.parse(["--help"])
        assert help_only is True


class TestGroupParser:
    """Test GroupParser"""

    def test_sub_command(self) -> None:
        """Test sub-command parsing"""
        parser = GroupParser()
        *_, sub_command, _ = parser.parse(["hello"], commands={"hello": "cmd"})
        assert sub_command == "cmd"
