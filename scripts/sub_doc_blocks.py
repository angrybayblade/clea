"""
Substitute blocks in the documentation

Example block:
    Define an example block using following template
        ```python !example:FILE:STARTING_LINE:ENDING_LINE
        # content will be added here
        ```
Exectution block:
    Define an example block using following template
        ```bash !exec:DIRECTORY:CAPTURE(stdout|stderr)
        $ CMD
        # output will be added here
        ```
"""

import re
import subprocess
import typing as t
from enum import Enum
from pathlib import Path

from typing_extensions import Annotated

from clea import Boolean, CleaException, Directory, command, run


FILE_RE = re.compile(r"[a-z0-9A-Z]+\.py")

_cache = {}


class BlockType(Enum):
    """Block type."""

    EXAMPLE = "example"
    EXEC = "exec"


def load_example(file: Path) -> str:
    """Load example file."""
    if file in _cache:
        return _cache[file]
    content = file.read_text(encoding="utf-8")
    content = re.sub("  # pragma: nocover", "", content)
    _cache[file] = content
    return _cache[file]


def parse_blocks(content: str) -> t.List[t.Dict[str, str]]:
    """Parse example blocks from file content."""
    blocks = []
    lines = content.split("\n")
    while len(lines) > 0:
        line = lines.pop(0)
        if "```python !!example:" in line:
            config = line.replace("```python !!example:", "").strip()
            example_file, *slc = config.split(":")
            example_block = line + "\n"
            while len(lines) > 0:
                line = lines.pop(0)
                example_block += line + "\n"
                if line == "```":
                    break
            blocks.append(
                {
                    "example": example_file,
                    "block": example_block,
                    "slc": list(map(int, slc)),
                    "type": BlockType.EXAMPLE,
                }
            )

        if "```bash !!exec" in line:
            exec_dir, read = line.replace("```bash !!exec:", "").strip().split(":")
            exec_block = line + "\n"
            while len(lines) > 0:
                line = lines.pop(0)
                exec_block += line + "\n"
                if line == "```":
                    break
            blocks.append(
                {
                    "directory": exec_dir,
                    "block": exec_block,
                    "read": read,
                    "type": BlockType.EXEC,
                }
            )

    return blocks


def sub_example(
    content: str,
    example: str,
    block: str,
    slc: t.List[int],
) -> str:
    """Substitute block with content from example file."""
    example_content = load_example(file=Path("examples", example))
    replace_block = f"```python !!example:{example}"
    if len(slc) == 2:
        start, end = slc
        replace_block += f":{start}:{end}"
        skim = example_content.split("\n")
        skim = skim[start:end]
        example_content = "\n".join(skim)
        example_content += "\n"
    if len(slc) == 1:
        (start,) = slc
        replace_block += f":{start}"
        skim = example_content.split("\n")
        skim = skim[start:]
        example_content = "\n".join(skim)
        example_content += "\n"
    replace_block += "\n" + example_content + "```\n"
    return content.replace(block, replace_block)


def sub_exec(
    content: str,
    directory: str,
    block: str,
    read: str,
) -> str:
    """Substitute block with output from the command execution."""
    _, cmd_str, *_ = block.split("\n")
    cmd = cmd_str.split(" ")[1:]
    process = subprocess.Popen(
        args=cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=directory
    )
    result = (
        process.stdout.read().decode()
        if read == "stdout"
        else process.stderr.read().decode()
    )
    replace_block = (
        "```bash !!exec:"
        + directory
        + ":"
        + read
        + "\n"
        + "$ "
        + " ".join(cmd)
        + "\n\n"
        + result
        + "```\n"
    )
    return content.replace(block, replace_block)


sub_funcs: t.Dict[BlockType, t.Callable[[str], str]] = {
    BlockType.EXAMPLE: sub_example,
    BlockType.EXEC: sub_exec,
}


def search_and_replace(file: Path) -> None:
    """Perform search and replace."""
    print(f"Processing {file}")
    doc_content = file.read_text(encoding="utf-8")
    blocks = parse_blocks(content=doc_content)
    for pblock in blocks:
        btype = t.cast(BlockType, pblock.pop("type"))
        sub_func = sub_funcs[btype]
        doc_content = sub_func(doc_content, **pblock)
    file.write_text(doc_content)


def search_and_check(file: Path) -> None:
    """Perform search and replace."""
    print(f"Checking {file}")
    doc_content = file.read_text(encoding="utf-8")
    check_content = doc_content
    blocks = parse_blocks(content=doc_content)
    for pblock in blocks:
        btype = t.cast(BlockType, pblock.pop("type"))
        sub_func = sub_funcs[btype]
        doc_content = sub_func(doc_content, **pblock)
    if check_content != doc_content:
        raise ValueError(f"Updated content does not match for {file}")


@command
def sub(
    check: Annotated[bool, Boolean(help="Perform check.")],
    docs: Annotated[Path, Directory(help="Path to documentation.")] = Path(
        "./docs",
    ),
) -> None:
    """
    Substitute {{example:FILE}} blocks in the documentation
    """

    errors = []
    for file in docs.rglob("*.md"):
        try:
            if check:
                search_and_check(file=file)
                continue
            search_and_replace(file=file)
        except ValueError as e:
            errors.append(str(e))
    if len(errors) > 0:
        raise CleaException(message="\n - ".join(["Documentation check failed", *errors]))


if __name__ == "__main__":
    run(sub)
