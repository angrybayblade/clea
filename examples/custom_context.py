"""Custom context example."""

from clea.context import Context as BaseContext
from clea.runner import run
from clea.wrappers import command


class Context(BaseContext):
    """Custom context object"""

    def config(self) -> dict:
        """Returns application config."""
        return {
            "home": "~/.app",
        }


@command(context=Context())
def home(context: Context) -> None:
    """Print home path."""
    print(context.config().get("home"))


if __name__ == "__main__":  # pragma: nocover
    run(cli=home)
