# Issue Documentation - Grant Hunter MCP

Date: 2026-03-28
Source of truth: `scripts/create_todo_issues.py`
Validation command used: `python scripts/create_todo_issues.py --dry-run`

## Purpose

This document captures the current issue backlog state and reflects which items have been resolved in code since the last review (2026-03-26).

## Summary

- Total issue definitions in automation script: **18** (12 original + 6 architecture hardening)
- Open issues in tracker: **20** (Issues #1–#21, excluding #9)
- Issues resolved in code (pending close): **1** (Issue #13)
- Architecture hardening issues pending creation: **6**
- Architecture hardening issues resolved in code (no issue needed): **3**

## Already Open (Current Issue Tracker)

1. Add unit tests for core modules (grants_gov_api, pitch_generator, pydantic_models) — #10
2. Refactor grants_gov_api.py for maintainability and testability — #11
3. ~~Migrate from requests to httpx for async network layer in grants_gov_api.py — #13~~ **RESOLVED in code (httpx.AsyncClient already used)**
4. Implement caching for grant search results to reduce API calls — #14
5. Implement full OAuth2 lifecycle for Google Services authentication — #15
6. Add Brazil grant sources support (Transferegov, Sebrae, FAPESP) — #16
7. Build React/Next.js user interface dashboard for the grant pipeline — #17
8. Set up comprehensive CI/CD pipeline for automated testing and Docker image building — #18
9. Create Helm charts for Kubernetes deployment — #19
10. [Suggestion] Add grant matching engine using vector embeddings for semantic similarity — #20
11. [Suggestion] Add multi-language support for pitch generation (Spanish, Portuguese, French) — #21
12. Refactor pitch_generator.py — extract prompt template to a separate constant or file — #12

## Resolved in Code (No Longer Needs an Issue)

These architecture hardening items from the 2026-03-26 review have been implemented and do not require new issues:

1. **Standardize error taxonomy and typed error envelope** — `ErrorEnvelope` model + `error_response()` helper implemented in `main.py`.
2. **Add typed response contract for `/manage_google_services`** — `GoogleServicesOutput` Pydantic model fully implemented.
3. **Align README and TECHNICAL with implemented behavior** — Both documents updated with accurate "Verified Capabilities" and "Current Limitations" sections.

## Pending Creation (Architecture Hardening Bundle)

These 6 issues have been added to `scripts/create_todo_issues.py` and are ready to be created:

1. **P0: Async network boundary refactor and non-blocking external calls**
   - Grants.gov path is async ✅; Google API calls still blocking via `asyncio.to_thread` workaround.
2. **P1: Query grants contract cleanup (focus_area and fallback transparency)**
   - Fallback metadata (`fallback_used`, `data_source`) done ✅; `focus_area` still unimplemented.
3. **P1: Harden OAuth lifecycle handling for Google Services**
   - Date validation done ✅; OAuth lifecycle (token refresh) still basic.
4. **P1: Normalize documentation encoding and remove stale sections**
   - Content updated ✅; BOM markers still present in some `.md` files.
5. **P2: Observability baseline (structured logs, request IDs, external call metrics)**
   - Not yet implemented.
6. **P2: Add TODO-to-issue synchronization guardrails**
   - Not yet implemented.

## Label Strategy in Script

Architecture hardening entries use standardized labels:

- `area/architecture`
- `area/api-contract`
- `area/security`
- `area/docs`
- `priority/P0`, `priority/P1`, `priority/P2`
- plus base labels (`enhancement`, `sub-issue`) or (`documentation`, `sub-issue`)

## Traceability

- Architecture review source: `ARCHITECTURE_REVIEW.md`
- TODO integration source: `TODO.md` section `Architecture Review Backlog (2026-03-26)`
- Issue automation source: `scripts/create_todo_issues.py`

## Next Actions

### Close Issue #13
Issue #13 ("Migrate from requests to httpx") has been completed: `grants_gov_api.py` uses `httpx.AsyncClient`, and `requests` is not in `requirements.txt`. The issue should be closed with a note confirming the migration is done.

### Create Pending Architecture Hardening Issues
The 6 pending architecture hardening issues have been added to the automation script. Create them via:

```bash
python scripts/create_todo_issues.py
```

Or use GitHub Actions workflow:

- `.github/workflows/create-todo-issues.yml` (run without dry-run)

**Note:** Labels (`area/architecture`, `area/api-contract`, `area/security`, `area/docs`, `priority/P0`, `priority/P1`, `priority/P2`) must exist in the repository before running the script with these issues. Create them manually or via the GitHub API if missing.
