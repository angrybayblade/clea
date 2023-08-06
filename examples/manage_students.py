"""CLI tool to manage student data"""

from enum import Enum
from pathlib import Path
from typing import List

from typing_extensions import Annotated

from clea.context import Context
from clea.params import (
    Boolean,
    Choice,
    ChoiceByFlag,
    File,
    Float,
    Integer,
    String,
    StringList,
)
from clea.runner import run
from clea.wrappers import group


class BloodGroup(Enum):
    """Blood group enum"""

    OP = "OP"
    ON = "ON"
    AP = "AP"
    AN = "AN"
    BP = "BP"
    BN = "BN"


class Gender(Enum):
    """Gender enum"""

    MALE = "male"
    FEMALE = "female"


class Verbosity(Enum):
    """Verbosity level."""

    INFO = "info"
    DEBUG = "debug"
    ERROR = "error"
    WARNING = "warning"


@group(name="students")
def main(
    verbosity: Annotated[Verbosity, ChoiceByFlag(Verbosity, help="Verbosity level")],
    context: Context,
) -> None:
    """Student helper."""
    context.set("verbosity", verbosity)
    print(context.get("verbosity"))


@main.command
def add(
    name: Annotated[str, String()],
    age: Annotated[int, Integer()],
    score: Annotated[int, Float()],
    blood_group: Annotated[
        BloodGroup, Choice(BloodGroup, "-b", help="Blood group of the student")
    ],
    gender: Annotated[
        Gender, ChoiceByFlag(Gender, Gender.MALE, help="Gender of the student")
    ],
    transfer: Annotated[
        bool, Boolean(help="Whether the student is a transfer student or not")
    ],
    certificate: Annotated[
        Path,
        File("-c", help="Path to the certificate file.", resolve=True),
    ],
    interests: Annotated[List[str], StringList("-i", help="List of hobbies")],
) -> None:
    """Add a student."""
    print(
        f"{name=}\n{age=}\n{score=}\n{blood_group=}\n{gender=}\n{interests=}\n{transfer=}\n{certificate=}"
    )


@main.group
def admin() -> None:
    """Admin tool."""


@admin.command
def remove(
    name: Annotated[str, String()],
    context: Context,
) -> None:
    """Remove a student."""
    print(name)
    print(context.get("verbosity"))


if __name__ == "__main__":
    run(cli=main)
