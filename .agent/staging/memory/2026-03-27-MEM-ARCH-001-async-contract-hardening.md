### [MEM-ARCH-001 | Async + Contract Hardening Baseline]

**Context**
- Implemented urgent architecture items from TODO/architecture review.
- Files changed across runtime, schema, and docs.

**Insight**
- Async grants integration is active:
  - `grants_gov_api.py`: `async def search_grants`, `httpx.AsyncClient`, async retry sleeps.
  - `main.py`: `await grants_api.search_grants(...)`.
- Response contract upgrades:
  - `pydantic_models.py`: `ErrorEnvelope`, `GoogleServicesOutput`.
  - `GrantsQueryOutput` now includes `fallback_used` and `data_source`.
  - `main.py` routes now emit envelope-based error payloads on defined failure paths.
- Google route non-blocking control:
  - `main.py` uses `await asyncio.to_thread(google_services_manager.execute_services, input_data)`.
- Deadline validation is strict:
  - `GoogleServicesInput` validator accepts only `%B %d, %Y` or `%Y-%m-%d`.
  - Service no longer silently falls back to current date on parse failures.
- Contract parity aligned in `mcp_definition.yaml` and docs (`README.md`, `TECHNICAL.md`).

**Why it matters**
- Future contributors should not reintroduce blocking grants calls or remove fallback/source metadata.
- Client integrations can now rely on stable typed envelopes and Google response structure.

**Verification Snapshot**
- `python -m py_compile main.py grants_gov_api.py google_services_manager.py pydantic_models.py` -> pass
- `pytest tests/ -v` -> 12 passed

**Changed Files**
- `main.py`
- `grants_gov_api.py`
- `google_services_manager.py`
- `pydantic_models.py`
- `mcp_definition.yaml`
- `README.md`
- `TECHNICAL.md`
- `requirements.txt`
- `tests/conftest.py`
- `tests/test_main.py`
- `tests/test_grants_api.py`
- `tests/test_pydantic_models.py`

**Tags**
- architecture, async, contract, mcp, fastapi, validation, tests
