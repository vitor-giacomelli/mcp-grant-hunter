#!/usr/bin/env python3
"""
Validate that every TODO.md item tagged *(new issue - pending workflow)*
has a corresponding entry in scripts/create_todo_issues.py.

Usage:
    python scripts/validate_todo_issues.py

Exit codes:
    0  All tagged TODO items are covered by an ISSUES entry.
    1  One or more tagged TODO items have no matching ISSUES entry.
"""

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
TODO_PATH = REPO_ROOT / "TODO.md"
SCRIPT_PATH = REPO_ROOT / "scripts" / "create_todo_issues.py"

# A keyword must be at least this many characters to be considered significant.
_MIN_WORD_LEN = 4
# Fraction of a TODO item's keywords that must appear in an ISSUES title
# for the item to be considered covered.
_MATCH_THRESHOLD = 0.5

PENDING_SUFFIX = "*(new issue - pending workflow)*"


def extract_todo_titles(todo_path: Path) -> list[str]:
    """Return bold titles of TODO items tagged *(new issue - pending workflow)*."""
    if not todo_path.exists():
        print(f"ERROR: TODO file not found: {todo_path}", file=sys.stderr)
        sys.exit(1)
    titles: list[str] = []
    for line in todo_path.read_text(encoding="utf-8-sig").splitlines():
        if PENDING_SUFFIX not in line:
            continue
        match = re.search(r"\*\*(.+?)\*\*", line)
        if match:
            titles.append(match.group(1).strip())
    return titles


def extract_issue_titles(script_path: Path) -> list[str]:
    """Parse the ISSUES list from create_todo_issues.py and return all titles."""
    if not script_path.exists():
        print(f"ERROR: Script file not found: {script_path}", file=sys.stderr)
        sys.exit(1)
    source = script_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not (isinstance(target, ast.Name) and target.id == "ISSUES"):
                continue
            if not isinstance(node.value, ast.List):
                continue
            titles: list[str] = []
            for elt in node.value.elts:
                if not isinstance(elt, ast.Dict):
                    continue
                for key, val in zip(elt.keys, elt.values):
                    if (
                        isinstance(key, ast.Constant)
                        and key.value == "title"
                        and isinstance(val, ast.Constant)
                    ):
                        titles.append(val.value)
            return titles
    return []


def _keywords(text: str) -> set[str]:
    """Normalize text and return significant words (length >= _MIN_WORD_LEN)."""
    text = text.lower()
    text = re.sub(r"[`'\",.()/\\[\]:;!?]", " ", text)
    words = re.split(r"[\s\-_]+", text)
    return {w for w in words if len(w) >= _MIN_WORD_LEN}


def is_covered(todo_title: str, issue_titles: list[str]) -> bool:
    """Return True if todo_title is covered by at least one ISSUES entry.

    Coverage is determined by keyword overlap: at least _MATCH_THRESHOLD of
    the TODO item's significant keywords must appear in an ISSUES title.
    """
    todo_kws = _keywords(todo_title)
    if not todo_kws:
        return True
    for issue_title in issue_titles:
        issue_kws = _keywords(issue_title)
        coverage = len(todo_kws & issue_kws) / len(todo_kws)
        if coverage >= _MATCH_THRESHOLD:
            return True
    return False


def main() -> int:
    todo_titles = extract_todo_titles(TODO_PATH)
    issue_titles = extract_issue_titles(SCRIPT_PATH)

    missing = [t for t in todo_titles if not is_covered(t, issue_titles)]

    if missing:
        print(
            "ERROR: The following TODO items tagged '*(new issue - pending workflow)*' "
            "have no matching entry in scripts/create_todo_issues.py:"
        )
        for title in missing:
            print(f"  - {title}")
        print()
        print(
            "Add a corresponding issue definition (with a matching title) to the "
            "ISSUES list in scripts/create_todo_issues.py."
        )
        return 1

    print(
        f"OK: All {len(todo_titles)} TODO item(s) tagged "
        f"'*(new issue - pending workflow)*' are covered by an ISSUES entry."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
