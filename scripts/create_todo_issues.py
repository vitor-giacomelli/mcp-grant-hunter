#!/usr/bin/env python3
"""
Script to create GitHub Issues for TODO items not yet tracked in the issue tracker.
Idempotent: checks for existing issues with the same title before creating.

Usage:
    GH_TOKEN=<token> python scripts/create_todo_issues.py [--dry-run]

Requires:
    - gh CLI (available in GitHub Actions runners)
    - GH_TOKEN or GITHUB_TOKEN environment variable
"""

import json
import subprocess
import sys

REPO = "vitor-giacomelli/mcp-grant-hunter"

ISSUES = [
    {
        "title": "Add unit tests for core modules (grants_gov_api, pitch_generator, pydantic_models)",
        "labels": ["enhancement", "sub-issue", "area/testing"],
        "body": """## Summary
Add dedicated unit tests for the three core Python modules to ensure correctness, catch regressions, and unblock safe refactoring.

## Why
The project currently lacks a unit test suite. Any change to `grants_gov_api.py`, `pitch_generator.py`, or `pydantic_models.py` carries silent regression risk.

## Scope
- `tests/test_grants_api.py`: unit tests for `search_grants` with mocked HTTP responses.
- `tests/test_pitch_generator.py`: tests for prompt construction and fallback logic.
- `tests/test_pydantic_models.py`: validation rule tests for all Pydantic models.

## Implementation Tasks
- [ ] Create `tests/` directory with `__init__.py`.
- [ ] Add `tests/test_grants_api.py` covering success path, retry behavior, and mock fallback.
- [ ] Add `tests/test_pitch_generator.py` covering prompt assembly and AI-service fallback.
- [ ] Add `tests/test_pydantic_models.py` covering required fields, type coercion, and rejection of invalid inputs.
- [ ] Add `pytest` and `pytest-mock` to `requirements.txt` (dev section or separate `requirements-dev.txt`).
- [ ] Update README with local test instructions (`pytest tests/ -v`).

## Acceptance Criteria
- [ ] All three test files exist and pass with `pytest`.
- [ ] External HTTP calls are fully mocked (no live network required).
- [ ] Test coverage for both success and error/fallback paths.

## Verification
- Run `pytest tests/ -v` locally and confirm green output.
- Intentionally break a validation rule and confirm the corresponding test fails.

## Risks
- Mocking `google.generativeai` may require additional fixtures.

## Out of Scope
- End-to-end tests with live credentials (tracked separately in issue #3).
""",
    },
    {
        "title": "Refactor grants_gov_api.py for maintainability and testability",
        "labels": ["enhancement", "sub-issue"],
        "body": """## Summary
Refactor `grants_gov_api.py` to break down the monolithic `search_grants` method and relocate the `MOCK_GRANTS` constant to a dedicated file.

## Why
`search_grants` currently handles searching, deduplicating, sorting, and formatting in a single method, making it hard to test each concern independently and difficult to extend.

## Scope
- Extract private helper methods: `_fetch_grants`, `_deduplicate`, `_sort_by_deadline`, `_format_results`.
- Move `MOCK_GRANTS` constant to `mock_data.py` to keep API logic clean.

## Implementation Tasks
- [ ] Create `mock_data.py` and move `MOCK_GRANTS` there.
- [ ] Break `search_grants` into `_fetch_grants`, `_deduplicate`, `_sort_by_deadline`, `_format_results`.
- [ ] Update all import references to `MOCK_GRANTS`.
- [ ] Ensure existing behavior is preserved (all tests must pass after refactor).

## Acceptance Criteria
- [ ] `search_grants` delegates to clearly named private methods.
- [ ] `MOCK_GRANTS` lives in `mock_data.py` with no logic duplication.
- [ ] No functional regression (behavior unchanged for all inputs).

## Verification
- Run unit tests (`pytest tests/test_grants_api.py -v`) after refactoring.
- Manual smoke test via `/query_grants` endpoint with demo mode.

## Risks
- Risk of subtle behavioral changes during method extraction.

## Out of Scope
- Performance optimizations (tracked in async/caching issues).
""",
    },
    {
        "title": "Refactor pitch_generator.py — extract prompt template to a separate constant or file",
        "labels": ["enhancement", "sub-issue"],
        "body": """## Summary
Extract the hardcoded prompt template inside `pitch_generator.py` into a separate named constant or text file for easier editing, versioning, and testing.

## Why
Embedding the prompt template inline makes it difficult to iterate on prompt engineering without modifying core Python logic, and complicates unit testing of the template separately from generation logic.

## Scope
- Extract the Triple-Horizon Framework prompt template to a named constant (e.g., `PITCH_PROMPT_TEMPLATE`) or a separate `prompts/pitch_template.txt` file.
- Update `pitch_generator.py` to load and use the extracted template.

## Implementation Tasks
- [ ] Decide on location: `PITCH_PROMPT_TEMPLATE` constant in `pitch_generator.py` header, or `prompts/pitch_template.txt`.
- [ ] Extract the full prompt string to the chosen location.
- [ ] Update `pitch_generator.py` to reference the extracted template.
- [ ] Add test assertion verifying the template contains required framework headings.

## Acceptance Criteria
- [ ] Prompt template is no longer embedded inline in the generation method.
- [ ] Changing the template does not require editing generation logic.
- [ ] All existing pitch generation tests pass.

## Verification
- Review the diff: generation method body should contain no multiline string literals.
- Run `pytest tests/test_pitch_generator.py -v`.

## Risks
- Template loading may fail silently if file path changes; add explicit error handling.

## Out of Scope
- Multi-language prompt templates (tracked separately).
""",
    },
    {
        "title": "Migrate from requests to httpx for async network layer in grants_gov_api.py",
        "labels": ["enhancement", "sub-issue"],
        "body": """## Summary
Replace the synchronous `requests` library with `httpx` (async-capable) in `grants_gov_api.py` to support high-concurrency production environments and align with FastAPI's async model.

## Why
Using blocking `requests.get` inside a FastAPI async endpoint blocks the event loop, limiting throughput. `httpx` provides a drop-in async replacement that is fully compatible with `asyncio` and FastAPI.

## Scope
- Replace `requests` with `httpx.AsyncClient` in `grants_gov_api.py`.
- Propagate `async/await` through the call stack to `main.py` endpoint handlers.
- Maintain the existing 5x retry with exponential backoff behavior.

## Implementation Tasks
- [ ] Add `httpx` to `requirements.txt` and remove `requests`.
- [ ] Rewrite HTTP calls in `grants_gov_api.py` using `async with httpx.AsyncClient()`.
- [ ] Update retry logic to use async-compatible approach (e.g., `tenacity` with async support).
- [ ] Update FastAPI route handlers in `main.py` to `async def` where needed.
- [ ] Update unit tests to mock `httpx.AsyncClient` instead of `requests`.

## Acceptance Criteria
- [ ] No synchronous blocking HTTP calls remain in the hot path.
- [ ] Retry behavior (5x, exponential backoff) is preserved.
- [ ] All tests pass; load test shows improved concurrency.

## Verification
- Run `pytest tests/ -v` after migration.
- Benchmark with `locust` or `wrk` to confirm improved throughput under concurrent load.

## Risks
- Retry library may require refactoring if current approach is incompatible with async.

## Out of Scope
- Google Services async migration (separate effort).
""",
    },
    {
        "title": "Implement caching for grant search results to reduce API calls",
        "labels": ["enhancement", "sub-issue"],
        "body": """## Summary
Add in-memory or Redis-based caching for `search_grants` responses to reduce redundant Grants.gov API calls and improve response latency.

## Why
Identical or similar keyword searches may be issued repeatedly by multiple users or MCP clients. Without caching, every call hits the Grants.gov API, increasing latency and risk of rate limiting.

## Scope
- In-memory TTL cache as the default (no external dependencies required).
- Optional Redis backend for distributed deployments.
- Cache keyed on normalized query parameters (`keyword`, `max_results`, `focus_area`).

## Implementation Tasks
- [ ] Implement a simple TTL in-memory cache (e.g., using `cachetools` or `functools.lru_cache` with TTL wrapper).
- [ ] Add cache key normalization for query parameters.
- [ ] Document Redis configuration path in `.env.example` and README.
- [ ] Add cache hit/miss logging (at DEBUG level, no PII).
- [ ] Add unit tests for cache behavior (hit, miss, expiry).

## Acceptance Criteria
- [ ] Repeated identical queries return cached results without hitting the external API.
- [ ] Cache TTL is configurable via environment variable.
- [ ] Cache does not persist PII or sensitive grant officer data.

## Verification
- Run unit tests with mock cache and confirm hit/miss behavior.
- Enable DEBUG logging and observe cache hit logs on repeated queries.

## Risks
- Stale cache may return outdated grant listings; TTL must be carefully tuned.

## Out of Scope
- Cache invalidation webhooks from Grants.gov (not available in their API).
""",
    },
    {
        "title": "Implement full OAuth2 lifecycle for Google Services authentication",
        "labels": ["enhancement", "sub-issue"],
        "body": """## Summary
Replace the current manual OAuth token passing with a dedicated authentication service that manages the full OAuth2 lifecycle, including token exchange and refresh token handling.

## Why
Currently, OAuth tokens are passed at runtime by the caller and are expected to already be valid. This places the entire OAuth lifecycle burden on the MCP client and does not support long-running sessions where tokens expire.

## Scope
- OAuth2 authorization code flow or service account flow.
- Token storage and automatic refresh.
- Secure credential injection (no token logging).

## Implementation Tasks
- [ ] Add `google-auth-oauthlib` to `requirements.txt`.
- [ ] Implement `auth_service.py` with `get_credentials()`, `refresh_token()` helpers.
- [ ] Update `google_services_manager.py` to use `auth_service` instead of inline token injection.
- [ ] Add `.env.example` entries for `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`.
- [ ] Add unit tests for token refresh and expiry detection.

## Acceptance Criteria
- [ ] Tokens are automatically refreshed without caller intervention.
- [ ] No raw token values appear in logs.
- [ ] Service account flow supported as an alternative for server-to-server use.

## Verification
- Test token refresh by expiring a token and confirming auto-renewal.
- Inspect logs to confirm no token values are emitted.

## Risks
- OAuth flow requires user interaction in non-service-account scenarios.

## Out of Scope
- Multi-tenant OAuth with per-user token storage.
""",
    },
    {
        "title": "Add Brazil grant sources support (Transferegov, Sebrae, FAPESP)",
        "labels": ["enhancement", "sub-issue"],
        "body": """## Summary
Extend the grant discovery engine to support Brazilian funding sources — Transferegov, Sebrae, and FAPESP — as part of the \"Brazil Grant Hunter\" initiative.

## Why
Brazilian startups and research institutions have access to significant non-dilutive funding through government and quasi-public bodies. Supporting these sources broadens the MCP's value beyond US-centric Grants.gov.

## Scope
- Integrations for at least Transferegov and Sebrae public APIs or web scraping (where APIs are unavailable).
- Normalize results to the existing `GrantResult` Pydantic model.
- Optional FAPESP integration if a stable public endpoint exists.

## Implementation Tasks
- [ ] Research available APIs for Transferegov, Sebrae, FAPESP.
- [ ] Create `brazil_grants_api.py` with `search_brazil_grants(keyword, max_results)`.
- [ ] Normalize Brazilian grant data to `GrantResult` schema.
- [ ] Add `source` field to `GrantResult` model (`"grants_gov"`, `"transferegov"`, etc.).
- [ ] Update `/query_grants` endpoint to accept optional `country` parameter (`"US"`, `"BR"`, `"all"`).
- [ ] Add unit tests with mocked Brazilian API responses.

## Acceptance Criteria
- [ ] `/query_grants` returns results from Brazilian sources when `country="BR"` or `"all"`.
- [ ] Results are normalized to the existing `GrantResult` schema.
- [ ] Brazilian API errors are handled with the same retry/fallback policy as Grants.gov.

## Verification
- Run unit tests with mock Brazilian API responses.
- Live smoke test with a keyword in Portuguese.

## Risks
- Brazilian government APIs may lack stable public endpoints; scraping may be fragile.

## Out of Scope
- Full Portuguese localization of the pitch generation (tracked separately).
""",
    },
    {
        "title": "Build React/Next.js user interface dashboard for the grant pipeline",
        "labels": ["enhancement", "sub-issue"],
        "body": """## Summary
Develop a React/Next.js frontend dashboard to provide a visual interface for grant discovery, pitch generation, and Google Services integration, replacing direct raw MCP API interaction.

## Why
The current raw MCP interface requires technical users. A UI lowers the barrier to entry for startup founders and grant managers who are not comfortable with API calls.

## Scope
- Grant search and results display.
- Pitch generation form and output viewer.
- Calendar and Gmail integration status panel.
- Authentication flow for Google Services.

## Implementation Tasks
- [ ] Bootstrap Next.js application in `ui/` subdirectory.
- [ ] Implement `/search` page: keyword input, results table with deadline sorting.
- [ ] Implement `/pitch` page: form for startup name/focus area/grant title, generated pitch display.
- [ ] Implement `/integrations` page: OAuth login, Gmail draft status, Calendar event status.
- [ ] Configure API base URL via `NEXT_PUBLIC_API_URL` environment variable.
- [ ] Add Dockerfile for the UI service.
- [ ] Update docker-compose (if present) to include UI service.

## Acceptance Criteria
- [ ] Users can search grants and view results without using the API directly.
- [ ] Pitch generation is accessible via a form.
- [ ] Google Services integration status is visible.

## Verification
- Run `npm run dev` in `ui/` and verify all three pages are functional.
- Screenshot key pages for documentation.

## Risks
- UI/backend API contracts must stay in sync; Pydantic schema changes break the UI.

## Out of Scope
- Mobile-native applications.
""",
    },
    {
        "title": "Set up comprehensive CI/CD pipeline for automated testing and Docker image building",
        "labels": ["enhancement", "sub-issue", "area/ci"],
        "body": """## Summary
Establish a complete GitHub Actions CI/CD pipeline that runs the full test suite on every PR and builds/publishes a Docker image on releases.

## Why
The project currently lacks automated test execution in CI. Without it, PRs can silently introduce regressions, and there is no automated path for producing versioned Docker images.

## Scope
- CI job: lint (flake8/mypy) + unit and integration tests (pytest) on every PR.
- CD job: build and push Docker image to GitHub Container Registry (ghcr.io) on tagged releases.
- Badge in README showing CI status.

## Implementation Tasks
- [ ] Create `.github/workflows/ci.yml` with lint and pytest jobs.
- [ ] Configure matrix testing for Python 3.11.
- [ ] Create `.github/workflows/docker-publish.yml` triggered on `push` to version tags (`v*.*.*`).
- [ ] Configure GHCR login and image tagging (semver + `latest`).
- [ ] Add CI status badge to README.
- [ ] Ensure tests run in under 5 minutes (mock all external calls).

## Acceptance Criteria
- [ ] Every PR triggers the CI workflow; failing tests block merge.
- [ ] Tagged releases produce a Docker image published to GHCR.
- [ ] CI badge in README reflects real-time pipeline status.

## Verification
- Open a test PR with a deliberate test failure and confirm CI blocks merge.
- Tag a test release and confirm Docker image appears in GHCR.

## Risks
- Docker build caching configuration needed to keep CD pipeline fast.

## Out of Scope
- Kubernetes deployment automation (tracked in Helm Charts issue).
""",
    },
    {
        "title": "Create Helm charts for Kubernetes deployment",
        "labels": ["enhancement", "sub-issue"],
        "body": """## Summary
Provide Helm charts for deploying the Grant Hunter MCP server to Kubernetes, enabling production-grade orchestration and configuration management.

## Why
As the MCP server matures for production use, teams deploying to Kubernetes need a standardized, configurable deployment artifact. Helm charts provide templated, versioned deployments that are easy to customize per environment.

## Scope
- Helm chart for the MCP API server.
- Configurable replicas, resource limits, environment variable injection, and health probes.
- Optional chart for Redis (if caching is implemented).
- `values.yaml` covering common deployment scenarios.

## Implementation Tasks
- [ ] Create `helm/grant-hunter-mcp/` chart using `helm create`.
- [ ] Configure `Deployment`, `Service`, `ConfigMap`, and `HorizontalPodAutoscaler` templates.
- [ ] Add liveness and readiness probes pointing to `/health`.
- [ ] Parameterize `GEMINI_API_KEY` and other secrets via Kubernetes Secret references.
- [ ] Add `helm/README.md` with installation and upgrade instructions.
- [ ] Validate chart with `helm lint` and `helm template` in CI.

## Acceptance Criteria
- [ ] `helm install grant-hunter ./helm/grant-hunter-mcp` deploys successfully to a local cluster (e.g., kind or minikube).
- [ ] All environment variables are injectable without modifying chart source.
- [ ] Chart passes `helm lint` with no errors.

## Verification
- Deploy to a local kind cluster and verify `/health` responds with 200.
- Run `helm upgrade` and confirm zero-downtime rollout.

## Risks
- Secret management strategy varies by cluster (Vault, Sealed Secrets, etc.); document supported approaches.

## Out of Scope
- GitOps integration (ArgoCD, Flux) — can be added as a follow-up.
""",
    },
    {
        "title": "[Suggestion] Add grant matching engine using vector embeddings for semantic similarity",
        "labels": ["enhancement", "sub-issue", "suggestion"],
        "body": """## Summary
Implement a more sophisticated grant matching algorithm using vector embeddings to match startups with grants based on semantic similarity rather than simple keyword matching.

## Type
Suggestion (optional, moderate complexity)

## Why
Keyword matching produces false negatives when grant descriptions use different terminology than the startup's focus area. A semantic similarity approach using vector embeddings would improve match quality and discover non-obvious funding opportunities.

## Proposed Changes
- Embed grant titles/descriptions using a lightweight embedding model (e.g., `sentence-transformers` or Gemini Embeddings API).
- Embed the startup's focus area description.
- Rank results by cosine similarity instead of keyword frequency.
- Cache embeddings to avoid recomputation.

## Implementation Tasks
- [ ] Add `sentence-transformers` or Gemini Embeddings integration to `grants_gov_api.py`.
- [ ] Implement `compute_similarity(startup_description, grant_description)` helper.
- [ ] Update `/query_grants` to support optional `matching_mode` parameter (`"keyword"` | `"semantic"`).
- [ ] Add embedding cache to avoid repeated calls for the same grant.
- [ ] Add unit tests for similarity scoring with known pairs.

## Acceptance Criteria
- [ ] `matching_mode=semantic` returns semantically related grants not matched by keywords.
- [ ] Keyword mode remains the default (backward-compatible).
- [ ] Embedding calls are cached per grant ID.

## Verification
- Compare keyword vs. semantic results for a test query.
- Confirm caching reduces API calls on repeated queries.

## Risks
- Embedding model latency may increase response times; async + caching required.

## Out of Scope
- Fine-tuning embedding models on grant-specific data.
""",
    },
    {
        "title": "[Suggestion] Add multi-language support for pitch generation (Spanish, Portuguese, French)",
        "labels": ["enhancement", "sub-issue", "suggestion"],
        "body": """## Summary
Localize the AI pitch generation to support multiple output languages — initially Spanish, Portuguese, and French — enabling non-English-speaking startups to generate compelling grant pitches in their native language.

## Type
Suggestion (optional, low-to-moderate complexity)

## Why
Grant applications in non-US jurisdictions (e.g., Brazil, France, Spain) are typically submitted in the local language. Allowing pitch output in the applicant's language removes a significant barrier and increases global utility.

## Proposed Changes
- Add optional `language` parameter to `PitchGenerateInput` Pydantic model (`"en"`, `"es"`, `"pt"`, `"fr"`).
- Update the prompt template in `pitch_generator.py` to instruct the model to respond in the specified language.
- Add language-specific fallback templates for when the AI service is unavailable.

## Implementation Tasks
- [ ] Add `language: str = "en"` field to `PitchGenerateInput` with validation for supported codes.
- [ ] Update prompt template to include language instruction: `"Respond in {language}."`.
- [ ] Add localized fallback templates for `"es"`, `"pt"`, `"fr"`.
- [ ] Add unit tests verifying language parameter is correctly injected into the prompt.
- [ ] Update API reference in README with `language` field documentation.

## Acceptance Criteria
- [ ] `language="pt"` produces a pitch in Brazilian Portuguese.
- [ ] Unsupported language codes return a validation error (422).
- [ ] Fallback template is language-appropriate when AI is unavailable.

## Verification
- Generate pitches in all four supported languages and review output quality.
- Test with an invalid language code and confirm 422 response.

## Risks
- AI model quality varies by language; Portuguese and Spanish are well-supported but quality should be evaluated.

## Out of Scope
- UI localization (tracked in the User Interface issue).
""",
    },
    # --- Architecture Hardening Bundle (from ARCHITECTURE_REVIEW.md 2026-03-26) ---
    {
        "title": "P0: Async network boundary refactor and non-blocking external calls",
        "labels": ["enhancement", "sub-issue", "area/architecture", "priority/P0"],
        "body": """## Summary
Complete the async migration so that no blocking external I/O occurs in FastAPI endpoint hot paths.

## Context
- Grants.gov path is fully async (httpx.AsyncClient). ✅
- Google API SDK calls (Gmail, Calendar) are synchronous and currently offloaded via `asyncio.to_thread` at route level. This is a workaround, not a proper async boundary.

## Why
Blocking operations in the event loop limit concurrency and degrade latency under load. Full async separation improves throughput and meets production-grade concurrency requirements.

## Scope
- Isolate or replace Google API blocking operations to avoid blocking the event loop.
- Add timeout budget per external call.
- Verify no blocking I/O remains in endpoint hot paths.

## Implementation Tasks
- [ ] Evaluate async-compatible Google API client (e.g., `google-api-python-client` async or `aiohttp` based approach).
- [ ] Move thread offload (`asyncio.to_thread`) to a dedicated executor pool configuration instead of ad-hoc at route level.
- [ ] Add per-external-call timeout configuration.
- [ ] Add integration test confirming no blocking calls in hot path.

## Acceptance Criteria
- [ ] No synchronous blocking calls remain in the FastAPI event loop for any endpoint.
- [ ] Concurrency improvement measurable under simulated load.

## Verification
- Load test with `locust` or `wrk` to confirm improved concurrency.
- Inspect async trace to confirm no blocking I/O in event loop.

## Risks
- Google API Python SDK may not have a fully async-native alternative; thread pool approach may be the pragmatic solution.

## Out of Scope
- Caching layer (tracked separately in Issue #14).
""",
    },
    {
        "title": "P1: Query grants contract cleanup (focus_area and fallback transparency)",
        "labels": ["enhancement", "sub-issue", "area/api-contract", "priority/P1"],
        "body": """## Summary
Resolve the `focus_area` contract ambiguity and ensure fallback behavior is fully transparent in API responses.

## Context
- `fallback_used` and `data_source` fields are present in `GrantsQueryOutput`. ✅
- `focus_area` is accepted in `GrantsQueryInput` but is not used for filtering. ❌

## Why
Consumers may assume `focus_area` filters results, causing incorrect integrations. The contract must match the behavior.

## Scope
- Decide: implement real `focus_area` filtering or remove the field from the input schema.
- Ensure fallback metadata is always present and accurate in responses.

## Implementation Tasks
- [ ] Decide on `focus_area`: implement filtering against grant categories/titles or remove from schema.
- [ ] If removing: add deprecation notice and bump API version.
- [ ] If implementing: add filter logic in `grants_gov_api.py` and add unit tests.
- [ ] Verify `fallback_used` and `data_source` are always set correctly in all code paths.

## Acceptance Criteria
- [ ] `focus_area` behavior matches its documented contract (either filtering or explicitly documented as unused).
- [ ] `fallback_used` and `data_source` are always present and accurate in `/query_grants` responses.

## Verification
- Send a request with `focus_area` set and verify results match the filter or field is removed.
- Trigger a fallback path and confirm `fallback_used=true` and `data_source=mock_fallback` are returned.

## Risks
- Removing `focus_area` is a breaking change for existing clients.

## Out of Scope
- Semantic search / vector-based filtering (tracked in Issue #20).
""",
    },
    {
        "title": "P1: Harden OAuth lifecycle handling for Google Services",
        "labels": ["enhancement", "sub-issue", "area/security", "priority/P1"],
        "body": """## Summary
Improve server-side OAuth token lifecycle management for the Google Services integration.

## Context
- `deadline_date` validation is fully implemented (explicit format enforcement). ✅
- OAuth tokens are passed raw by the caller per request with no server-side refresh or lifecycle management. ❌

## Why
Long-running integrations using the MCP will encounter token expiry without a refresh path. Delegating the full OAuth lifecycle to clients creates fragility and operational risk.

## Scope
- Define and document the server-side token lifecycle strategy.
- Optionally implement token refresh using refresh token (stored securely).
- Enforce explicit error on expired/invalid token rather than silent failure.

## Implementation Tasks
- [ ] Define integration contract: short-lived token per call vs. refresh token in environment.
- [ ] If refresh token: add `google-auth-oauthlib` to `requirements.txt` and implement `refresh_credentials()` helper.
- [ ] Return explicit `AUTH_ERROR` response with clear message when token is expired or invalid (already partially handled via HttpError 401 checks).
- [ ] Add `.env.example` entries for `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`.
- [ ] Add unit tests for token expiry detection and refresh behavior.

## Acceptance Criteria
- [ ] Expired or invalid tokens return an explicit, machine-readable error (not a silent partial failure).
- [ ] Token lifecycle strategy is clearly documented in TECHNICAL.md.

## Verification
- Test with an expired token and confirm explicit `AUTH_ERROR` response.
- Inspect logs to confirm no token values are emitted.

## Risks
- OAuth refresh flow requires stored refresh token; service account flow may be preferable for server-to-server use.

## Out of Scope
- Multi-tenant OAuth with per-user token storage.
""",
    },
    {
        "title": "P1: Normalize documentation encoding and remove stale sections",
        "labels": ["documentation", "sub-issue", "area/docs", "priority/P1"],
        "body": """## Summary
Remove BOM (byte order mark) characters from top-level documentation files and ensure all docs are consistently UTF-8 encoded without encoding artifacts.

## Context
- `ARCHITECTURE_REVIEW.md`, `TODO.md`, and `TECHNICAL.md` contain UTF-8 BOM markers (﻿) at the start of files.
- These cause display artifacts in some editors and markdown renderers.

## Why
BOM markers in UTF-8 files reduce readability and can cause parsing issues in automated tooling.

## Scope
- Strip BOM markers from all affected top-level `.md` files.
- Verify no stale or duplicate narrative sections remain.

## Implementation Tasks
- [ ] Identify all `.md` files with BOM markers using `grep` or `file` command.
- [ ] Re-save affected files as UTF-8 without BOM.
- [ ] Verify all docs render correctly in GitHub markdown preview.

## Acceptance Criteria
- [ ] No BOM markers in top-level documentation files.
- [ ] All docs render cleanly in GitHub.

## Verification
- Run `file *.md` and confirm all files are `UTF-8 Unicode text` (not `UTF-8 Unicode (with BOM) text`).

## Risks
- Low risk; purely cosmetic/encoding fix.

## Out of Scope
- Content rewrites or narrative reorganization.
""",
    },
    {
        "title": "P2: Observability baseline (structured logs, request IDs, external call metrics)",
        "labels": ["enhancement", "sub-issue", "area/architecture", "priority/P2"],
        "body": """## Summary
Add request correlation IDs, structured log fields, and external call timing/failure telemetry to improve operational visibility.

## Why
Currently, logs use basic `logging.info/error` with no correlation IDs. When a request fails, there is no way to trace a specific request end-to-end or identify which upstream call caused a latency spike.

## Scope
- Request correlation ID injected per request and included in all log lines.
- Structured log fields (JSON or key=value format) for key events.
- External call timing metrics (Grants.gov response time, Gemini response time).

## Implementation Tasks
- [ ] Add middleware to inject a `request_id` UUID per incoming request.
- [ ] Pass `request_id` through to all service calls and log lines.
- [ ] Add timing measurements for external calls (Grants.gov, Gemini, Google APIs).
- [ ] Emit structured log entries at key decision points (fallback triggered, retry attempted, auth error).
- [ ] Document log format in TECHNICAL.md.

## Acceptance Criteria
- [ ] Every request log line includes a stable `request_id`.
- [ ] External call duration is logged at DEBUG level.
- [ ] Fallback events are logged at WARNING level with `request_id` context.

## Verification
- Send a request and grep logs for the `request_id` across all log lines.
- Trigger a fallback and confirm structured warning log is emitted.

## Risks
- Log verbosity at DEBUG level may be high; ensure production log level defaults to INFO.

## Out of Scope
- Metrics export to Prometheus/OpenTelemetry (can be added as follow-up).
""",
    },
    {
        "title": "P2: Add TODO-to-issue synchronization guardrails",
        "labels": ["enhancement", "sub-issue", "area/architecture", "priority/P2"],
        "body": """## Summary
Add automated validation to detect drift between `TODO.md` architecture backlog items and the issue automation script (`scripts/create_todo_issues.py`).

## Why
The TODO and issue automation are manually kept in sync. Any new backlog item added to `TODO.md` without a corresponding entry in the issue script creates silent drift and means issues are never created for those items.

## Scope
- A validation script or CI step that compares TODO backlog item titles against the `ISSUES` list in `create_todo_issues.py`.
- Fail with a clear message if a TODO item has no matching issue definition.

## Implementation Tasks
- [ ] Add `scripts/validate_todo_issues.py` that reads both `TODO.md` and `create_todo_issues.py` and checks for missing mappings.
- [ ] Add naming convention: TODO items intended to become issues must use a `*(new issue - pending workflow)*` suffix.
- [ ] Add CI step to `.github/workflows/create-todo-issues.yml` that runs the validation before issue creation.

## Acceptance Criteria
- [ ] Adding a new `*(new issue - pending workflow)*` item to `TODO.md` without a script entry causes the validation to fail.
- [ ] Validation passes for all current TODO/issue pairs.

## Verification
- Add a dummy TODO item without a script entry and confirm validation fails.
- Remove the dummy item and confirm validation passes.

## Risks
- Low risk; purely a tooling addition.

## Out of Scope
- Automatic creation of issues from TODO.md (this is the existing script's responsibility).
""",
    },
]


def issue_exists(title: str, dry_run: bool = False) -> bool:
    """Check if an issue with the given title already exists."""
    try:
        result = subprocess.run(
            [
                "gh", "issue", "list",
                "--repo", REPO,
                "--state", "open",
                "--search", title,
                "--json", "title",
                "--limit", "50",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        issues = json.loads(result.stdout)
        for issue in issues:
            if issue["title"].strip().lower() == title.strip().lower():
                return True
        return False
    except subprocess.CalledProcessError as e:
        print(f"  WARNING: Could not check for existing issue: {e.stderr}", file=sys.stderr)
        return False


def create_issue(issue: dict, dry_run: bool = False) -> None:
    """Create a GitHub issue with the given title, body, and labels."""
    title = issue["title"]
    body = issue["body"]
    labels = issue.get("labels", [])

    if dry_run:
        print(f"  [DRY RUN] Would create: {title}")
        print(f"  [DRY RUN] Labels: {', '.join(labels)}")
        return

    cmd = [
        "gh", "issue", "create",
        "--repo", REPO,
        "--title", title,
        "--body", body,
    ]
    for label in labels:
        cmd.extend(["--label", label])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"  Created: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"  ERROR creating issue '{title}': {e.stderr}", file=sys.stderr)


def main() -> None:
    dry_run = "--dry-run" in sys.argv[1:] or sys.argv[1:] == ["true"]

    if dry_run:
        print("=== DRY RUN MODE — no issues will be created ===\n")

    print(f"Processing {len(ISSUES)} TODO-tracked issues...\n")

    created = 0
    skipped = 0

    for issue in ISSUES:
        title = issue["title"]
        print(f"Checking: {title}")

        if issue_exists(title, dry_run):
            print(f"  SKIP — issue already exists.\n")
            skipped += 1
        else:
            create_issue(issue, dry_run)
            created += 1
            print()

    print(f"\nDone. Created: {created}, Skipped (already exist): {skipped}")


if __name__ == "__main__":
    main()
