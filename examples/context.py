"""Context example."""


from clea.context import Context
from clea.runner import run
from clea.wrappers import group


@group
def admin(context: Context) -> None:
    """Admin."""
    context.set("foo", "bar")


@admin.group(name="manage")
def manage(context: Context) -> None:
    """Manage."""
    context.set("hello", "world")


@manage.command
def student(context: Context) -> None:
    """Manage."""
    print(context.get("foo"))
    print(context.get("hello"))


@manage.command(name="teacher")
def teacher(context: Context) -> None:
    """Manage."""
    print(context.get("foo"))
    print(context.get("hello"))


if __name__ == "__main__":
    run(cli=admin)
