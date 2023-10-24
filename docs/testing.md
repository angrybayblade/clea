## Testing clea applications

To test a clea application you can use the `isolated` flag in the `clea.runner.run` method. For example, to test the `add.py`

```python
from examples.add import add as cli
from clea.runner import run


def test_missing_arguments() -> None:
    """Test add."""
    result = run(cli=cli, argv=[], isolated=True)
    assert result.exit_code == 1
    assert (
        "Missing argument for positional arguments <N1 type=int>, <N2 type=int>"
        in result.stderr
    )


def test_add() -> None:
    """Test add."""
    result = run(cli=cli, argv=["1", "2"], isolated=True)
    assert result.exit_code == 0
    assert "Total 3" in result.stdout
```