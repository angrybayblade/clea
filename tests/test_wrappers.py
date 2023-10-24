"""Test wrappers."""

from typing_extensions import Annotated

from clea import params as p
from clea.wrappers import Command, Group
from clea.runner import run
import pytest


class TestCommandWrapper:
    """Test command wrapper."""

    def test_wrap(self) -> None:
        """Test wrapper."""

        @Command.wrap
        def _command() -> None:
            """Example command"""

        assert isinstance(_command, Command)

    def test_wrap_with_arguments(self) -> None:
        """Test wrapper with arguments."""

        @Command.wrap(name="cmd")
        def _command() -> None:
            """Example command"""

        result = run(cli=_command, argv=["--help"], isolated=True)
        assert "cmd" in result.stdout

    def test_version(self) -> None:
        """Test wrapper with arguments."""

        @Command.wrap(version="0.1.0")
        def _command() -> None:
            """Example command"""

        result = run(cli=_command, argv=["--version"], isolated=True)
        assert "0.1.0" in result.stdout

    def test_help(self) -> None:
        """Test wrapper."""

        @Command.wrap
        def _command(
            p1: Annotated[str, p.String()],
            p2: Annotated[str, p.String()] = "kwarg",
        ) -> None:
            """Example command"""

        result = run(cli=_command, argv=["--help"], isolated=True)
        assert "Example command" in result.stdout

    def test_runtime_exception(self) -> None:
        """Test exception raising"""

        @Command.wrap
        def _command() -> None:
            """Example command"""
            raise Exception("Some error...")

        with pytest.raises(Exception, match="Some error..."):
            _command.invoke([])
        assert _command.invoke([], isolated=True) == 1


class TestGroupWrapper:
    """Test Group wrapper."""

    def test_wrap(self) -> None:
        """Test wrapper."""

        @Group.wrap
        def _group() -> None:
            """Example group"""

        assert isinstance(_group, Group)

    def test_help(self) -> None:
        """Test wrapper."""

        @Group.wrap
        def _group(
            p1: Annotated[str, p.String()],
            p2: Annotated[str, p.String()] = "kwarg",
        ) -> None:
            """Example group"""

        result = run(cli=_group, argv=["--help"], isolated=True)
        assert "Example group" in result.stdout

    def test_version(self) -> None:
        """Test wrapper."""

        @Group.wrap(version="0.1.0")
        def _group() -> None:
            """Example group"""

        result = run(cli=_group, argv=["--version"], isolated=True)
        assert "0.1.0" in result.stdout

    def test_allow_direct_exec(self) -> None:
        """Test allow direct execution."""

        @Group.wrap(allow_direct_exec=True)
        def _group() -> None:
            """Example group"""
            print("Running...")

        result = run(cli=_group, argv=[], isolated=True)
        assert "Running..." in result.stdout
