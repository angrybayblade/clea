"""Test add_student.py"""

from clea.runner import run
from examples.add_student import add as cli


def test_invoke() -> None:
    """Test command invocation."""
    result = run(cli=cli, argv=[], isolated=True)
    assert result.exit_code == 1
    assert (
        "Missing argument for positional arguments <NAME type=str>, <AGE type=int>, <SCORE type=float>"
        in result.stderr
    )

    result = run(cli=cli, argv=["name", "22", "98"], isolated=True)
    assert result.exit_code == 0
    assert (
        "name='name'\nage=22\nscore=98.0\nblood_group=None\ngender=<Gender.MALE: 'male'>\ninterests=[]\ntransfer=False\ncertificate=None\n"
        in result.stdout
    )
