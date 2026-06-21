### [MEM-ARCH-004 | Server-Side OAuth Session Persistence (No Dashboard)]

**Context**
- User requested proceeding with persistent token/session lifecycle, explicitly no dashboard work.
- Implemented in this pass across API, models, store module, OpenAPI, docs, and tests.

**Insight**
- Added SQLite-backed session store module: `oauth_session_store.py`.
- Added endpoints:
  - `POST /oauth_sessions` to persist OAuth credentials and return `session_id`.
  - `DELETE /oauth_sessions/{session_id}` to remove session.
- `GoogleServicesInput` now supports either:
  - direct `oauth_token`, or
  - `oauth_session_id` (session-backed execution).
- `/manage_google_services` resolves credentials from session when `oauth_session_id` is provided and token is omitted.
- After execution, refreshed access token is persisted back to session store via `update_access_token`.
- Added explicit 404 path for missing sessions (`OAUTH_SESSION_NOT_FOUND`).

**Why it matters**
- Removes requirement to send raw OAuth credentials on every call.
- Enables reusable server-side auth sessions for repeated operations.
- Maintains backward compatibility with existing direct-token clients.

**Verification**
- `pytest tests -v` => `31 passed`.
- `python -m py_compile main.py oauth_session_store.py google_services_manager.py pydantic_models.py` => pass.

**Remaining Boundaries**
- No encryption-at-rest for stored secrets yet.
- No external secret manager/KMS integration yet.
- No UI/dashboard work was started (by request).

**Tags**
- oauth, session-store, sqlite, api-contract, persistence, testing
