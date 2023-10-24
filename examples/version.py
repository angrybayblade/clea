"""Version flag example."""


from clea.runner import run
from clea.wrappers import command


@command(version="0.1.0.rc0")
def example() -> None:
    """Version example."""


if __name__ == "__main__":  # pragma: nocover
    run(cli=example)
