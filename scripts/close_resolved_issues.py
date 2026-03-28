#!/usr/bin/env python3
"""
Script to close GitHub Issues that are resolved in the current codebase.
Idempotent: only closes issues that are still open.

Usage:
    GH_TOKEN=<token> python scripts/close_resolved_issues.py [--dry-run]

Requires:
    - gh CLI (available in GitHub Actions runners)
    - GH_TOKEN or GITHUB_TOKEN environment variable
"""

import json
import subprocess
import sys

REPO = "vitor-giacomelli/mcp-grant-hunter"

# Issues to close with resolution notes.
# Each entry maps an issue title to a close comment.
RESOLVED_ISSUES = [
    {
        "title": "Migrate from requests to httpx for async network layer in grants_gov_api.py",
        "comment": (
            "## Resolved ✅\n\n"
            "This issue has been completed. `grants_gov_api.py` now uses `httpx.AsyncClient` "
            "with full async/await support and 5x exponential-backoff retry logic. "
            "The `requests` library is no longer present in `requirements.txt`.\n\n"
            "**Evidence:**\n"
            "- `grants_gov_api.py` uses `async with httpx.AsyncClient(...)` in `_search_by_keyword`.\n"
            "- `requirements.txt` contains `httpx>=0.27.0` with no `requests` entry.\n"
            "- Retry/backoff logic preserved using `asyncio.sleep` + attempt counter.\n\n"
            "Closing as completed."
        ),
    },
]


def get_open_issue_number(title: str) -> int | None:
    """Return the issue number if an open issue with the given title exists."""
    try:
        result = subprocess.run(
            [
                "gh", "issue", "list",
                "--repo", REPO,
                "--state", "open",
                "--search", title,
                "--json", "number,title",
                "--limit", "50",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        issues = json.loads(result.stdout)
        for issue in issues:
            if issue["title"].strip().lower() == title.strip().lower():
                return issue["number"]
        return None
    except subprocess.CalledProcessError as e:
        print(f"  WARNING: Could not check for existing issue: {e.stderr}", file=sys.stderr)
        return None


def close_issue(number: int, comment: str, dry_run: bool = False) -> None:
    """Add a comment to an issue and close it."""
    if dry_run:
        print(f"  [DRY RUN] Would close issue #{number} with resolution comment.")
        return

    # Add resolution comment
    try:
        subprocess.run(
            [
                "gh", "issue", "comment", str(number),
                "--repo", REPO,
                "--body", comment,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"  Added resolution comment to issue #{number}.")
    except subprocess.CalledProcessError as e:
        print(f"  WARNING: Could not add comment to #{number}: {e.stderr}", file=sys.stderr)

    # Close the issue
    try:
        result = subprocess.run(
            [
                "gh", "issue", "close", str(number),
                "--repo", REPO,
                "--reason", "completed",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"  Closed: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"  ERROR closing issue #{number}: {e.stderr}", file=sys.stderr)


def main() -> None:
    dry_run = "--dry-run" in sys.argv[1:] or sys.argv[1:] == ["true"]

    if dry_run:
        print("=== DRY RUN MODE — no issues will be closed ===\n")

    print(f"Processing {len(RESOLVED_ISSUES)} resolved issue(s)...\n")

    closed = 0
    skipped = 0

    for entry in RESOLVED_ISSUES:
        title = entry["title"]
        comment = entry["comment"]
        print(f"Checking: {title}")

        number = get_open_issue_number(title)
        if number is None:
            print(f"  SKIP — issue not found or already closed.\n")
            skipped += 1
        else:
            print(f"  Found open issue #{number}.")
            close_issue(number, comment, dry_run)
            closed += 1
            print()

    print(f"\nDone. Closed: {closed}, Skipped (already closed or not found): {skipped}")


if __name__ == "__main__":
    main()
