# Issue Documentation - Grant Hunter MCP

Date: 2026-03-26
Source of truth: `scripts/create_todo_issues.py`
Validation command used: `python scripts/create_todo_issues.py --dry-run`

## Purpose

This document captures the current issue backlog state before any new issue creation action.

## Summary

- Total issue definitions in automation script: **21**
- Already open (skipped by dry-run): **11**
- Pending creation (dry-run "Would create"): **10**

## Already Open (Skipped in Dry-Run)

1. Add unit tests for core modules (grants_gov_api, pitch_generator, pydantic_models)
2. Refactor grants_gov_api.py for maintainability and testability
3. Migrate from requests to httpx for async network layer in grants_gov_api.py
4. Implement caching for grant search results to reduce API calls
5. Implement full OAuth2 lifecycle for Google Services authentication
6. Add Brazil grant sources support (Transferegov, Sebrae, FAPESP)
7. Build React/Next.js user interface dashboard for the grant pipeline
8. Set up comprehensive CI/CD pipeline for automated testing and Docker image building
9. Create Helm charts for Kubernetes deployment
10. [Suggestion] Add grant matching engine using vector embeddings for semantic similarity
11. [Suggestion] Add multi-language support for pitch generation (Spanish, Portuguese, French)

## Pending Creation (Would Create)

### Existing backlog item not yet open

1. Refactor pitch_generator.py - extract prompt template to a separate constant or file

### Architecture hardening bundle

2. P0: Async network boundary refactor and non-blocking external calls
3. P0: Standardize error taxonomy and typed error envelope across endpoints
4. P1: Query grants contract cleanup (focus_area and fallback transparency)
5. P1: Add typed response contract for manage_google_services
6. P1: Harden OAuth lifecycle handling and deadline date validation
7. P1: Align README and TECHNICAL with implemented behavior
8. P1: Normalize documentation encoding and remove stale sections
9. P2: Observability baseline (structured logs, request IDs, external call metrics)
10. P2: Add TODO-to-issue synchronization guardrails

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

## Next Action (When Approved)

Create pending issues via existing automation:

```bash
python scripts/create_todo_issues.py
```

Or use GitHub Actions workflow:

- `.github/workflows/create-todo-issues.yml` (run without dry-run)
