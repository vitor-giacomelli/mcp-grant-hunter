# Memory Index - mcp-grant-hunter

Updated: 2026-03-27

## Retrieval Guide

- If task is about async throughput or MCP response contract behavior:
  - `2026-03-27-MEM-ARCH-001-async-contract-hardening.md`
- If task is about focus_area behavior, request IDs, or baseline observability logs:
  - `2026-03-27-MEM-ARCH-002-focus-area-observability.md`
- If task is about Google OAuth token refresh lifecycle in `/manage_google_services`:
  - `2026-03-27-MEM-ARCH-003-oauth-refresh-lifecycle.md`
- If task is about persisted server-side OAuth sessions (`/oauth_sessions`) and token reuse:
  - `2026-03-28-MEM-ARCH-004-oauth-session-persistence.md`
- If task is about GitHub issue automation, labels, or auth failures:
  - `2026-03-27-MEM-WORKFLOW-001-issue-automation-auth-labels.md`

## Quick Facts

- Runtime contract has changed: `ErrorEnvelope`, `GoogleServicesOutput`, and grants metadata fields are now in code and OpenAPI.
- Grants path is async (`httpx`), Google SDK path is still sync but offloaded in route with `asyncio.to_thread`.
- Tests currently passing: `pytest tests/ -v` => 12 passed.
- Issue automation counters are fixed: script reports `Created/Skipped/Failed` distinctly, with label preflight and missing-label skip warnings.
