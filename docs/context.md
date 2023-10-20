Whenever a command is executed, a runtime object is created which holds state for this particular invocation. You can utilise this context object for maintining a state for the command execution.

## Data store

Context object provides a simple key-value data store for storing and retrieving data across the execution.

```python
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


if __name__ == "__main__":
    run(cli=admin)
```

## Custom context

You can define a custom context for tasks such as loading and storing application config.

```python
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


if __name__ == "__main__":
    run(cli=home)
```
