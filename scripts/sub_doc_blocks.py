"""
Substitute blocks in the documentation

Example block:
    Define an example block using following template
        <!-- {"type": "example", "file"FILE:STARTING_LINE:ENDING_LINE -->
        ```python
        # content will be added here
        ```
Exectution block:
    Define an example block using following template
        <!-- exec:DIRECTORY:CAPTURE(stdout|stderr) -->
        ```bash
        $ CMD
        # output will be added here
        ```
"""

import json
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
        if line.startswith("<!-- {"):
            config = json.loads(line.replace("<!-- ", "").replace(" -->", "").strip())
            block = line + "\n"
            while len(lines) > 0:
                line = lines.pop(0)
                block += line + "\n"
                if line == "```":
                    break
            config["type"] = BlockType(config["type"])
            config["block"] = block
            blocks.append(config)
    return blocks


def sub_example(
    content: str,
    file: str,
    block: str,
    start: int = 0,
    end: int = -1,
) -> str:
    """Substitute block with content from example file."""
    config = {"file": file, "type": BlockType.EXAMPLE.value}
    example_content = load_example(file=Path(file))
    example_lines = example_content.splitlines() + [""]
    example_lines = example_lines[start:end]
    if start != 0:
        config["start"] = start
    if end > -1:
        config["end"] = end

    replace_block = f"<!-- {json.dumps(config)} -->\n"
    replace_block += "```python\n"
    replace_block += "\n".join(example_lines)
    replace_block += "\n```\n"
    return content.replace(block, replace_block)


def sub_exec(
    content: str,
    directory: str,
    read: str,
    block: str,
) -> str:
    """Substitute block with output from the command execution."""
    _, _, cmd_str, *_ = block.split("\n")
    cmd = cmd_str.split(" ")[1:]
    process = subprocess.Popen(
        args=cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=directory
    )
    result = (
        process.stdout.read().decode()
        if read == "stdout"
        else process.stderr.read().decode()
    )
    config = {"type": BlockType.EXEC.value, "directory": directory, "read": read}
    replace_block = f"<!-- {json.dumps(config)} -->\n"
    replace_block += "```bash\n"
    replace_block += f"$ "
    replace_block += " ".join(cmd)
    replace_block += "\n\n"
    replace_block += result
    replace_block += "```\n"
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
        raise CleaException(
            message="\n - ".join(["Documentation check failed", *errors])
        )


if __name__ == "__main__":
    run(sub)
