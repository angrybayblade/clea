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
from clea.wrappers import command


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
    NONE_BINARY = "none_binary"


@command
def add(
    name: Annotated[str, String()],
    age: Annotated[int, Integer()],
    score: Annotated[int, Float()],
    blood_group: Annotated[
        BloodGroup,
        Choice(BloodGroup, "-b", help="Blood group of the student"),
    ],
    gender: Annotated[
        Gender, ChoiceByFlag(Gender, Gender.MALE, help="Gender of the student")
    ],
    transfer: Annotated[
        bool, Boolean(help="Whether the student is a transfer student or not")
    ],
    certificate: Annotated[
        Path,
        File(
            "-c",
            help="Path to the certificate file.",
            resolve=True,
            env="CERTIFICATE_FILE",
        ),
    ],
    interests: Annotated[List[str], StringList("-i", help="List of hobbies")],
) -> None:
    """
    Add a student.
    """
    print(
        f"{name=}\n{age=}\n{score=}\n{blood_group=}\n{gender=}\n{interests=}\n{transfer=}\n{certificate=}"
    )


if __name__ == "__main__":
    run(cli=add)
