### [MEM-WORKFLOW-001 | Issue Automation Auth + Label Failure Pattern]

**Context**
- Multiple runs of `python scripts/create_todo_issues.py` during backlog sync.

**Insight**
- Observed failure pattern:
  - `GraphQL: Resource not accessible by personal access token (createIssue)`
  - Label errors for missing labels: `area/architecture`, `area/api-contract`, `area/security`, `priority/P*`.
- Current repo labels listed via `gh label list` do not include required architecture/priority labels.
- Operationally safe token switch pattern (non-destructive):
  - Temporarily map alternate token env value to `GH_TOKEN` for one command, then restore prior value.

**Status Update (2026-03-27)**
- Reliability gap fixed in `scripts/create_todo_issues.py`:
  - `create_issue(...)` now returns `bool`.
  - `main()` tracks `created`, `skipped`, and `failed` separately.
  - `created` increments only when creation step reports success.
- Label preflight added:
  - script fetches repo labels once via `gh label list`.
  - missing labels are reported and skipped (issue creation continues).
- Verified with:
  - `python -m py_compile scripts/create_todo_issues.py`
  - `python scripts/create_todo_issues.py --dry-run`
  - result snapshot: `Created: 10, Skipped: 11, Failed: 0` (dry-run semantics).

**Why it matters**
- Prevents false assumption that backlog issues were created.
- Prevents accidental permanent token replacement when managing multiple GitHub identities.

**When to use this note**
- Before re-running issue automation.
- When diagnosing `created/skipped/failed` discrepancies in script output.

**Actionable Follow-up**
- Create missing repo labels (architecture + priority namespaces) before non-dry-run creation to preserve triage taxonomy.
- Keep auth-token mapping procedure documented for multi-account usage.

**Related Files**
- `scripts/create_todo_issues.py`
- `ISSUES_DOCUMENTATION.md`
- `TODO.md`

**Tags**
- workflow, github, auth, labels, automation, reliability
