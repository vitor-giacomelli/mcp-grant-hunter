### [MEM-ARCH-002 | Focus-Area Filtering + Request-ID Observability Baseline]

**Context**
- Task: update docs and implement urgent TODO backlog fixes after architecture hardening pass.
- Files touched: `main.py`, `grants_gov_api.py`, `pydantic_models.py`, `tests/test_main.py`, `tests/test_pitch_generator.py`, `tests/test_pydantic_models.py`, `README.md`, `TECHNICAL.md`, `TODO.md`.

**Insight**
- `/query_grants` now applies `focus_area` filtering (substring match over title/description/category/agency), removing prior schema-behavior drift.
- API now has request-level correlation id middleware:
  - injects `x-request-id` in every response.
  - logs request completion with method/path/status/duration.
- Grants.gov external call telemetry baseline added in `grants_gov_api.py`:
  - logs per-attempt status and duration.
  - logs timeout/http/unexpected error durations.
- Query endpoint error mapping is explicit (`QUERY_GRANTS_UPSTREAM_FAILURE`, `QUERY_GRANTS_MAPPING_FAILURE`) instead of broad fallback masking.
- OAuth hardening increment: `oauth_token` validator now rejects empty/whitespace-containing token payloads early.

**Why it matters**
- Restores contract integrity for `focus_area` without changing endpoint shape.
- Improves operational debugging and traceability with minimal architecture change.
- Prevents silent failure masking and catches invalid OAuth inputs before SDK calls.

**Verification**
- `pytest tests -v` => `19 passed`.
- `python -m py_compile main.py grants_gov_api.py google_services_manager.py pydantic_models.py pitch_generator.py scripts/create_todo_issues.py` => pass.

**Remaining High-Signal Gaps**
- OAuth lifecycle is still client-managed (no server-side refresh/token exchange flow yet).
- Observability still lacks dashboard/query cookbook and aggregated metrics backend.

**Tags**
- architecture, api-contract, observability, oauth, testing, fastapi
