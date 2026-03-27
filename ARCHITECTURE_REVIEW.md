# Architecture Review - Grant Hunter MCP

Date: 2026-03-26
Reviewer: Codex architectural pass

## Summary

This review focuses on architecture quality attributes, API contract stability, operational safety, and documentation fidelity. Findings are converted into actionable backlog items and mapped to TODO and automated GitHub issue creation.

## Risk Matrix

| ID | Finding | Severity | Priority | Status |
|---|---|---|---|---|
| AR-01 | Async/sync mismatch in request path | High | P0 | Backlog |
| AR-02 | Contract drift and misleading fallback behavior | High | P0 | Backlog |
| AR-03 | Unstable response contracts | High | P1 | Backlog |
| AR-04 | Auth and date safety gaps | Medium | P1 | Backlog |
| AR-05 | Docs-to-code inconsistency | Medium | P1 | Backlog |
| AR-06 | Documentation quality defects and stale sections | Medium | P1 | In progress |
| AR-07 | TODO to issue synchronization drift risk | Medium | P2 | Backlog |

## Findings and Recommendations

### AR-01 - Async/sync mismatch in request path (High, P0)

**Evidence**

- FastAPI handlers are async in `main.py`.
- Grants path uses blocking `requests` client in `grants_gov_api.py`.
- Google service calls use blocking Google client operations in `google_services_manager.py`.

**Impact**

- event loop blocking under concurrency
- reduced throughput and degraded latency during upstream slowness

**Recommended Remediation**

- migrate Grants.gov path to async HTTP client (`httpx.AsyncClient`)
- isolate or offload blocking Google operations (or move to async-compatible pattern)
- add timeout budget and observability per external call

### AR-02 - Contract drift and fallback opacity (High, P0)

**Evidence**

- `focus_area` is accepted by `/query_grants` input model but not used in filtering.
- broad exception fallback can return mock data without explicit `fallback_used` contract flag.

**Impact**

- consumers may assume semantic filtering that does not happen
- operational incidents may be masked as successful responses

**Recommended Remediation**

- choose and document one path for `focus_area`: implement real filtering or remove from input contract
- include explicit response metadata (`fallback_used`, `data_source`)
- narrow exception handling and return explicit error envelope when appropriate

### AR-03 - Unstable response contracts (High, P1)

**Evidence**

- `/manage_google_services` response is currently untyped and shape-varying.

**Impact**

- client integrations become brittle
- difficult automated contract testing

**Recommended Remediation**

- add strict Pydantic response model for Google services endpoint
- introduce standardized error envelope across endpoints

### AR-04 - Auth and date safety gaps (Medium, P1)

**Evidence**

- raw OAuth token is passed per request and refresh lifecycle is externalized
- date parse fallback can silently default to current date

**Impact**

- operational risk for long-lived integrations
- potential incorrect calendar event scheduling

**Recommended Remediation**

- add server-side token lifecycle strategy or clearly constrained integration contract
- enforce date validation and return explicit validation failure on invalid deadline formats

### AR-05 - Docs-to-code inconsistency (Medium, P1)

**Evidence**

- prior docs overstated deployment maturity and external call guarantees
- repository state does not yet include all claimed delivery artifacts

**Impact**

- misleading expectations for adopters and contributors

**Recommended Remediation**

- maintain explicit "Verified Capabilities" and "Current Limitations" sections
- require doc updates in same PR as behavior changes

### AR-06 - Documentation quality defects (Medium, P1)

**Evidence**

- encoding artifacts and stale trailing sections were present in core docs

**Impact**

- reduced readability and trust in source-of-truth docs

**Recommended Remediation**

- normalize docs to UTF-8 safe content
- remove stale/duplicate narrative

### AR-07 - TODO to issue synchronization drift (Medium, P2)

**Evidence**

- TODO and issue generator are manually kept in sync

**Impact**

- roadmap drift between markdown backlog and issue tracker

**Recommended Remediation**

- define synchronization policy and add validation check script
- enforce issue-title traceability markers

## Traceability Table

| Finding | TODO item | GitHub issue title |
|---|---|---|
| AR-01 | Async network boundary refactor | `P0: Async network boundary refactor and non-blocking external calls` |
| AR-02 | Query contract and fallback transparency | `P0: Standardize error taxonomy and typed error envelope across endpoints` and `P1: Query grants contract cleanup (focus_area and fallback transparency)` |
| AR-03 | Typed Google response contract | `P1: Add typed response contract for manage_google_services` |
| AR-04 | OAuth/date safety hardening | `P1: Harden OAuth lifecycle handling and deadline date validation` |
| AR-05 | Docs alignment | `P1: Align README and TECHNICAL with implemented behavior` |
| AR-06 | Encoding/stale doc cleanup | `P1: Normalize documentation encoding and remove stale sections` |
| AR-07 | Backlog sync guardrails | `P2: Add TODO-to-issue synchronization guardrails` |

## Planned Public API Direction

- Add strict response schema for `/manage_google_services`.
- Add optional query response metadata: `data_source`, `fallback_used`.
- Define standard error envelope with machine-readable `code` and human-readable `message`.
- Resolve `focus_area` contract as implemented filter or remove it.

## Acceptance Criteria for Architecture Hardening

- strict endpoint contracts published and tested
- fallback behavior transparent in API responses
- no blocking network calls in hot async paths
- docs consistently reflect current implementation
- TODO and issue backlog remain traceably synchronized
