"""Block commits while temporary educational explanations remain in source code."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORIES = (PROJECT_ROOT / "backend", PROJECT_ROOT / "frontend" / "src")
SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".vue", ".js", ".jsx"}
MARKER = "LEARN:"
IGNORED_PARTS = {".venv", "node_modules", "dist", "__pycache__"}


def find_markers() -> list[tuple[Path, int, str]]:
    """Return every source line that still contains the LEARN marker."""

    matches: list[tuple[Path, int, str]] = []

    for source_directory in SOURCE_DIRECTORIES:
        if not source_directory.exists():
            continue

        for path in source_directory.rglob("*"):
            if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
                continue
            if any(part in IGNORED_PARTS for part in path.parts):
                continue

            for line_number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                if MARKER in line:
                    matches.append((path.relative_to(PROJECT_ROOT), line_number, line.strip()))

    return matches


def main() -> int:
    """Print an actionable report and return a non-zero exit code to block the commit."""

    matches = find_markers()
    if not matches:
        print("Temporary learning comments: OK")
        return 0

    print("Commit blocked: remove or rewrite temporary LEARN comments:\n")
    for path, line_number, line in matches:
        print(f"  {path}:{line_number}: {line}")

    print("\nKeep useful production comments without the LEARN marker.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
