# Grant Hunter MCP

Grant Hunter MCP is a FastAPI-based Model Context Protocol (MCP) service for grant discovery and pitch drafting.

## Verified Capabilities

- `POST /query_grants`
  - Searches Grants.gov by keyword.
  - Uses async `httpx` call path with retry/backoff.
  - Deduplicates by opportunity number.
  - Sorts by close date.
  - Falls back to mock grants if upstream lookup fails, with response metadata (`fallback_used`, `data_source`).
- `POST /generate_pitch`
  - Generates a draft pitch using Gemini (`gemini-2.0-flash` then `gemini-2.0-flash-lite`).
  - Falls back to a deterministic template when generation fails or no API key is set.
- `POST /manage_google_services`
  - Creates a Gmail draft and a Calendar event from request inputs.
  - Returns a typed response contract (`GoogleServicesOutput`).
  - Supports `DEMO_MODE=TRUE` to simulate success.
- `GET /health`
  - Basic health endpoint.

## Current Limitations

- Partial async migration:
  - Grants lookup is async.
  - Google API SDK calls are sync and currently executed via route-level thread offload.
- Contract drift:
  - `focus_area` is accepted by `/query_grants` input but not used in filtering.
- OAuth lifecycle:
  - Raw OAuth token is passed by client per request; refresh/token exchange lifecycle is not managed server-side.
- Date safety:
  - Deadline dates are now validated; accepted formats are `%B %d, %Y` or `%Y-%m-%d`.
- Delivery posture:
  - Test suite and CI are planned but not yet implemented.
  - Docker usage is documented as roadmap; no Dockerfile is currently present in this repository.

## Architecture Docs

- [TECHNICAL.md](TECHNICAL.md): current architecture and component behavior.
- [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md): structured architecture review, risk matrix, and remediation backlog.
- [TODO.md](TODO.md): prioritized roadmap and issue-linked backlog.

## Setup (Local)

### Prerequisites

- Python 3.11+
- Gemini API key for AI pitch generation

### Install

```bash
pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
```

Set at least:

- `GEMINI_API_KEY` (required for live AI generation)

Optional:

- `MCP_SERVER_URL`
- `LOG_LEVEL`
- `DEMO_MODE`

### Run

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Docs:

- `http://localhost:8000/docs`

## API Reference

### `GET /health`

Returns service health status.

### `POST /query_grants`

Request:

```json
{
  "keyword": "clean energy",
  "max_results": 20,
  "focus_area": "renewable energy"
}
```

Response includes:

- `fallback_used`: `true` when fallback data is used
- `data_source`: `grants_gov` or `mock_fallback`

### `POST /generate_pitch`

Request:

```json
{
  "startup_name": "CleanTech Solutions",
  "focus_area": "Renewable Energy",
  "grant_title": "Clean Energy Innovation Grant"
}
```

### `POST /manage_google_services`

Request:

```json
{
  "grant_title": "Clean Energy Innovation Grant",
  "deadline_date": "December 15, 2025",
  "oauth_token": "oauth_access_token"
}
```

## Error Contract

Error responses are standardized with:

```json
{
  "code": "MACHINE_READABLE_CODE",
  "message": "Human readable message",
  "details": { "optional": "context" }
}
```

## Issue Automation

The repository includes automatic TODO issue creation:

- Workflow: `.github/workflows/create-todo-issues.yml`
- Script: `scripts/create_todo_issues.py`

Run manually via GitHub Actions `workflow_dispatch` or on push to `main` when TODO/script changes.

## Security Notes

- Never commit `.env`.
- Avoid logging tokens or generated sensitive content.
- Input validation is enforced through Pydantic models.

## Contributing

1. Review `TODO.md` and `ARCHITECTURE_REVIEW.md`.
2. Keep behavior and docs in sync.
3. Add tests for new behavior whenever possible.
4. Do not commit secrets.
