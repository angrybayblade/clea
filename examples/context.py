"""Context example."""

from clea.context import Context
from clea.runner import run
from clea.wrappers import command, group


@group
def admin(context: Context) -> None:
    """Admin."""
    context.set("foo", "bar")


@admin.group(name="manage", allow_direct_exec=True)
def manage(context: Context) -> None:
    """Manage."""
    context.set("hello", "world")


@command
def student(context: Context) -> None:
    """Student."""
    print(context.get("foo"))
    print(context.get("hello"))


manage.add_child(student)

if __name__ == "__main__":  # pragma: nocover
    run(cli=admin)
