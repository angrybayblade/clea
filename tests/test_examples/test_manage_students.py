"""Test manage_students.py"""

from clea.runner import run
from examples.manage_students import main as cli


def test_add() -> None:
    """Test add student."""
    result = run(
        cli=cli,
        argv=["admin", "add", "name", "22", "100"],
        isolated=True,
    )
    assert result.exit_code == 0
    assert (
        "name='name'\nage=22\nscore=100.0\nblood_group=None\n"
        "gender=<Gender.MALE: 'male'>\ninterests=[]\ntransfer=False"
        "\ncertificate=None\n"
    ) in result.stdout


def test_remove() -> None:
    """Test remove student."""
    result = run(
        cli=cli,
        argv=["admin", "remove", "name"],
        isolated=True,
    )
    assert result.exit_code == 0
    assert "Removed name\n" in result.stdout
