import re
from dataclasses import dataclass


@dataclass
class ChangedLine:
    filename: str
    line_number: int
    content: str


HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def parse_diff(raw_diff: str) -> list[ChangedLine]:
    results: list[ChangedLine] = []
    current_file: str | None = None
    current_line = 0

    for line in raw_diff.splitlines():
        if line.startswith("diff --git"):
            current_file = None
            continue

        if line.startswith("+++ b/"):
            current_file = line[6:]
            continue

        hunk_match = HUNK_HEADER.match(line)
        if hunk_match:
            current_line = int(hunk_match.group(1))
            continue

        if current_file is None:
            continue

        if line.startswith("+"):
            results.append(ChangedLine(
                filename=current_file,
                line_number=current_line,
                content=line[1:],
            ))
            current_line += 1

        elif line.startswith("-"):
            pass

        else:
            current_line += 1

    return results
