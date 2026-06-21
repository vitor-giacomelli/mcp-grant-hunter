### [MEM-ARCH-003 | Per-Request OAuth Refresh Lifecycle for Google Services]

**Context**
- Follow-up implementation for urgent TODO item: OAuth lifecycle hardening.
- Added in this pass across `pydantic_models.py`, `google_services_manager.py`, `mcp_definition.yaml`, docs, and tests.

**Insight**
- `GoogleServicesInput` now supports optional refresh flow fields:
  - `refresh_token`, `client_id`, `client_secret`, `token_uri`.
- Validation guarantees:
  - `oauth_token` must be non-empty and whitespace-free.
  - If `refresh_token` is provided, both `client_id` and `client_secret` are mandatory.
- `GoogleServicesManager` now runs a per-request refresh attempt via `Credentials.refresh(Request())` when refresh fields are present.
- Refresh outcome is exposed in `GoogleServicesOutput`:
  - `oauth_status` (`ACCESS_TOKEN_ONLY`, `REFRESH_SUCCESS`, `REFRESH_FAILED`)
  - `token_refreshed` (bool)
- Refresh failure is non-fatal to preserve backward compatibility: service continues with provided access token and records warning in `errors`.

**Why it matters**
- Eliminates hard dependency on clients pre-refreshing access tokens before every call.
- Keeps existing access-token-only integrations working.
- Makes token lifecycle state observable to callers.

**Verification**
- Added tests:
  - `tests/test_google_services_manager.py`
  - new validation cases in `tests/test_pydantic_models.py`
- Full suite: `pytest tests -v` => `24 passed`.
- Syntax check: `python -m py_compile ...` => pass.

**Remaining Constraints**
- No persistent token vault or server-side session store yet.
- Refresh configuration is supplied per request (not centrally managed).

**Tags**
- oauth, google-services, auth-lifecycle, api-contract, validation, testing
