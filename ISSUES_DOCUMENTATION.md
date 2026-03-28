# Issue Documentation - Grant Hunter MCP

Date: 2026-03-28
Source of truth: `scripts/create_todo_issues.py`
Last run: `python scripts/create_todo_issues.py` (via GitHub Actions, run #3)

## Purpose

This document captures the current issue backlog state. It was last updated after a full workflow run that created 6 new architecture hardening issues and closed 1 resolved issue.

## Summary

- Total issue definitions in automation script: **18** (12 original + 6 architecture hardening)
- Open issues in tracker: **25**
- Issues closed as resolved: **1** (Issue #13)
- Architecture hardening issues created: **6** (Issues #23–#28)

## Open Issues (Current)

| # | Title | Labels |
|---|---|---|
| #1 | Define MCP source-of-truth and sync contract with private repo | area/sync |
| #2 | Add CI drift check for shared MCP files | area/sync, area/ci |
| #3 | Add MCP endpoint contract and resiliency tests | area/testing |
| #4 | Adopt semantic versioning and changelog workflow | area/release |
| #5 | Clarify public repo scope, architecture, and contribution path | area/docs |
| #6 | [Suggestion] Add CODEOWNERS for MCP core and release files | area/docs |
| #7 | [Suggestion] Add lightweight MCP evaluation suite | area/testing |
| #8 | [EPIC] Public MCP hardening and release governance | epic |
| #10 | Add unit tests for core modules | area/testing |
| #11 | Refactor grants_gov_api.py for maintainability and testability | — |
| #12 | Refactor pitch_generator.py — extract prompt template | — |
| #14 | Implement caching for grant search results | — |
| #15 | Implement full OAuth2 lifecycle for Google Services | — |
| #16 | Add Brazil grant sources support | — |
| #17 | Build React/Next.js user interface dashboard | — |
| #18 | Set up comprehensive CI/CD pipeline | area/ci |
| #19 | Create Helm charts for Kubernetes deployment | — |
| #20 | [Suggestion] Add grant matching engine (vector embeddings) | suggestion |
| #21 | [Suggestion] Add multi-language support for pitch generation | suggestion |
| #23 | P0: Async network boundary refactor | area/architecture, priority/P0 |
| #24 | P1: Query grants contract cleanup (focus_area) | area/api-contract, priority/P1 |
| #25 | P1: Harden OAuth lifecycle handling | area/security, priority/P1 |
| #26 | P1: Normalize documentation encoding | area/docs, priority/P1 |
| #27 | P2: Observability baseline | area/architecture, priority/P2 |
| #28 | P2: TODO-to-issue synchronization guardrails | area/architecture, priority/P2 |

## Closed Issues

| # | Title | Reason |
|---|---|---|
| #13 | Migrate from requests to httpx for async network layer | **Completed** — `httpx.AsyncClient` is in use; `requests` removed from `requirements.txt` |

## Label Strategy

All labels are now present in the repository:

- `enhancement`, `documentation`, `sub-issue`, `suggestion`, `epic`
- `area/architecture`, `area/api-contract`, `area/security`, `area/docs`
- `area/testing`, `area/ci`, `area/sync`, `area/release`
- `priority/P0`, `priority/P1`, `priority/P2`

## Traceability

- Architecture review source: `ARCHITECTURE_REVIEW.md`
- TODO integration source: `TODO.md` section `Architecture Review Backlog (2026-03-26)`
- Issue automation source: `scripts/create_todo_issues.py`
- Close automation source: `scripts/close_resolved_issues.py`
- Workflow: `.github/workflows/create-todo-issues.yml`
