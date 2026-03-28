# Project Roadmap and Technical Debt

This document tracks known technical debt, planned improvements, and roadmap items for Grant Hunter MCP.

Items marked `(new issue - pending workflow)` are created by:

- Workflow: `.github/workflows/create-todo-issues.yml`
- Script: `scripts/create_todo_issues.py`

## Issue Creation Status (2026-03-27)

- Attempted issue creation via `python scripts/create_todo_issues.py`.
- Result: architecture bundle issues are still pending mainly due GitHub token/permission blockers in current CLI session.
- Confirmed blockers:
  - `GraphQL: Resource not accessible by personal access token (createIssue)`
- Missing labels in target repo (`area/architecture`, `area/api-contract`, `area/security`, `priority/P1`, etc.) are now handled by script preflight and skipped safely.
- Next retry command (without replacing permanent env vars):
  - Temporarily map alternate token for this shell run, then execute `python scripts/create_todo_issues.py`.

## Architecture Review Backlog (2026-03-26)

Source: [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md)

### P0

- [x] **Async network boundary refactor and non-blocking external calls** *(new issue - pending workflow)*
  - [x] Replace blocking grants lookup path with async-compatible HTTP execution.
  - [x] Isolate/offload blocking Google API operations from hot async request path.
  - [x] Add verification that async request path contains no blocking external calls.
  - Acceptance criteria: measurable concurrency improvement and no blocking I/O in endpoint hot path.

- [x] **Standardize error taxonomy and typed error envelope across endpoints** *(new issue - pending workflow)*
  - [x] Define one error response schema (`code`, `message`, optional `details`).
  - [x] Use explicit error mapping instead of broad catch-all fallback behavior.
  - [x] Document error contract in API docs.
  - Acceptance criteria: all endpoints return consistent machine-readable error responses.

### P1

- [x] **Query grants contract cleanup (`focus_area`, fallback transparency)** *(new issue - pending workflow)*
  - [x] Decide if `focus_area` is implemented filtering or remove it from input schema.
  - [x] Add optional response metadata (`fallback_used`, `data_source`).
  - [x] Ensure fallback semantics are explicit to clients.
  - Acceptance criteria: schema and behavior are aligned and documented.

- [x] **Add typed response contract for `/manage_google_services`** *(new issue - pending workflow)*
  - [x] Introduce strict response model for success/partial failure/failure outcomes.
  - [x] Remove shape-varying ad-hoc response payloads.
  - Acceptance criteria: endpoint response shape is contract-stable and testable.

- [ ] **Harden OAuth lifecycle handling and deadline date validation** *(new issue - pending workflow)*
  - [x] Define token refresh/token lifecycle approach and constraints.
    - Implemented per-request refresh flow using `refresh_token` + client credentials.
    - Implemented persisted server-side OAuth sessions (`/oauth_sessions`, SQLite-backed store).
    - Remaining: encryption-at-rest / external secret-manager integration.
  - [x] Reject invalid date formats with explicit validation errors.
  - Acceptance criteria: no silent fallback-to-today behavior on invalid input.

- [x] **Align README and TECHNICAL with implemented behavior** *(new issue - pending workflow)*
  - [x] Keep "Verified Capabilities" and "Current Limitations" sections current.
  - [x] Remove unsupported or outdated implementation claims.
  - Acceptance criteria: docs reflect current code behavior without over-claiming.

- [x] **Normalize documentation encoding and remove stale sections** *(new issue - pending workflow)*
  - [x] Eliminate mojibake and stale trailing content in top-level docs.
  - Acceptance criteria: top-level docs are clean, readable, and internally consistent.

### P2

- [ ] **Observability baseline (structured logs, request IDs, external call metrics)** *(new issue - pending workflow)*
  - [x] Add request correlation IDs and structured logging fields.
  - [x] Add external dependency timing/failure telemetry.
  - [ ] Add dashboard/query examples for operational usage.
  - Acceptance criteria: per-request traceability and upstream failure visibility.

- [ ] **TODO-to-issue synchronization guardrails** *(new issue - pending workflow)*
  - [ ] Add validation check ensuring architecture TODO items are represented in issue automation script.
  - [ ] Add naming convention to maintain traceability between TODO and issues.
  - Acceptance criteria: TODO/issue drift is automatically detectable.

---

## High Priority (Existing Technical Debt)

### 1. Testing Infrastructure (Critical)

- [x] **Create `tests/` directory**: dedicated test suite now exists.
- [ ] **Unit tests** *(new issue - pending workflow)*:
  - [x] `tests/test_grants_api.py`: test `search_grants` with mocked responses.
  - [x] `tests/test_pitch_generator.py`: test prompt construction and fallback logic.
  - [x] `tests/test_pydantic_models.py`: verify validation rules.
- [ ] **Integration tests** -> [Issue #3: Add MCP endpoint contract and resiliency tests](https://github.com/vitor-giacomelli/mcp-grant-hunter/issues/3):
  - [x] `tests/test_main.py`: test FastAPI endpoints using `TestClient`.

### 2. Code Refactoring

- [ ] **Refactor `grants_gov_api.py`** *(new issue - pending workflow)*:
  - [ ] Break `search_grants` into smaller private methods.
  - [ ] Move `MOCK_GRANTS` to `mock_data.py`.
- [ ] **Refactor `pitch_generator.py`** *(new issue - pending workflow)*:
  - [ ] Extract prompt template to a separate constant or file.

---

## Future Implementations (V2 Roadmap)

### 1. Architecture and Performance

- [x] **Async network layer** *(new issue - pending workflow)*: migrated from `requests` to `httpx` in grants path.
- [ ] **Caching** *(new issue - pending workflow)*: add in-memory or Redis caching for grant search results.

### 2. Features

- [ ] **Full OAuth2 flow** *(new issue - pending workflow)*: dedicated auth/token lifecycle service.
- [ ] **Brazil expansion** *(new issue - pending workflow)*: support Transferegov, Sebrae, FAPESP.
- [ ] **User interface** *(new issue - pending workflow)*: React/Next.js dashboard.

### 3. DevOps

- [ ] **CI/CD pipeline** *(new issue - pending workflow)*: automated tests and image pipeline.
- [ ] **Helm charts** *(new issue - pending workflow)*: Kubernetes deployment templates.

---

## Suggestions / Nice-to-Have

- [ ] **Grant matching engine** *(new issue - pending workflow)*: semantic retrieval with embeddings.
- [ ] **Multi-language support** *(new issue - pending workflow)*: localized pitch generation output.
