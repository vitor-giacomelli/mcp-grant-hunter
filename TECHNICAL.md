# Technical Documentation - Grant Hunter MCP

## Architecture Overview

Grant Hunter MCP is a FastAPI service exposing MCP-compatible endpoints for:

- grant discovery via Grants.gov
- pitch generation via Gemini
- Google Workspace actions (Gmail draft + Calendar event)

Current runtime characteristics:

- API server: FastAPI + Uvicorn
- Validation: Pydantic models
- Grants lookup: async `httpx` with retry/backoff
- Google services: synchronous Google API client libraries
- Request observability: request-id middleware and structured external-call logs
- OAuth session persistence: SQLite-backed server-side session store

## System Diagram

The diagram below shows the **public MCP server** (this repository) and its relationship to external APIs and the private product layer.

```mermaid
graph TD
    subgraph Private["Private Product (separate repo)"]
        UI[User-Facing UI]
        Orchestrator[Workflow Orchestrator]
    end

    subgraph MCP["Grant Hunter MCP — this public repo"]
        Server[FastAPI Server]
        Q[/query_grants]
        P[/generate_pitch]
        G[/manage_google_services]
        Mock[Mock Grants Fallback]
        PitchTemplate[Template Pitch Fallback]

        Server --> Q
        Server --> P
        Server --> G
        Q --> Mock
        P --> PitchTemplate
    end

    Client[External MCP Client] -->|HTTP| Server
    UI -->|HTTP| Server
    Orchestrator -->|HTTP| Server

    Q --> GrantsGov[Grants.gov API]
    P --> Gemini[Gemini Models]
    G --> GoogleWS[Gmail and Calendar APIs]
```

**Boundary notes:**

- Everything inside the *Grant Hunter MCP* box is in this public repository.
- The *Private Product* box represents a separate private repository not covered here.
- External MCP clients interact directly with the public MCP server over HTTP.
- See [CONTRIBUTING.md](CONTRIBUTING.md) for what belongs in each repository.

## Component Analysis

### 1) `grants_gov_api.py`

Responsibilities:

- keyword search against Grants.gov
- retry/backoff for selected failure conditions
- deduplication, sorting, formatting
- mock fallback return when lookup path fails

Notes:

- uses async HTTP client (`httpx.AsyncClient`)
- currently mixes fetch + transform responsibilities in a single flow

### 2) `pitch_generator.py`

Responsibilities:

- construct generation prompt
- call Gemini primary/fallback models
- return deterministic fallback template on failure

Notes:

- prompt template is in-code (not externalized)
- predictable fallback keeps endpoint available when model calls fail

### 3) `google_services_manager.py`

Responsibilities:

- create Gmail draft
- create Calendar event
- return operation status payload

Notes:

- request carries raw OAuth access token
- optional per-request server-side refresh is supported when request includes
  `refresh_token`, `client_id`, and `client_secret`
- refresh result is surfaced in response as `oauth_status` and `token_refreshed`
- date parsing now enforces explicit formats (`%B %d, %Y` or `%Y-%m-%d`)
- response shape is typed via `GoogleServicesOutput`

### 4) `oauth_session_store.py`

Responsibilities:

- persist OAuth credentials server-side in SQLite
- provide create/get/update/delete operations keyed by `session_id`
- support access token updates after refresh

## Data Flow

### `/query_grants`

1. Input validated by `GrantsQueryInput`.
2. Async Grants.gov call performed.
3. Data deduplicated/sorted/formatted.
4. On failure/empty path, mock fallback may be returned with explicit metadata (`fallback_used`, `data_source`).
5. Optional `focus_area` is applied as a text filter against title/description/category/agency fields.

### `/generate_pitch`

1. Input validated by `PitchGenerateInput`.
2. Prompt assembled.
3. Gemini primary model call; fallback model on failure.
4. Deterministic template fallback if model path fails.

### `/manage_google_services`

1. Input validated by `GoogleServicesInput`.
2. Token converted to credentials.
3. Optional server-side token refresh attempted when refresh credentials are provided.
4. Gmail draft and Calendar event calls attempted.
5. Aggregated typed status payload returned (`GoogleServicesOutput`).
6. If session-backed execution is used, refreshed access token is persisted back to session store.

### `/oauth_sessions`

1. Input validated by `OAuthSessionCreateInput`.
2. Credentials persisted in session store.
3. `session_id` returned for later use in `/manage_google_services`.

## Verified Capabilities

- Endpoint routing and basic validation are in place.
- Grant search retry/backoff logic exists for Grants.gov path.
- Graceful fallback is implemented for grant query and pitch generation.
- Demo mode exists for Google services simulation.
- Response correlation IDs (`x-request-id`) are included for traceability.
- Server-side OAuth sessions can be created and deleted via API.

## Current Limitations

- Google service SDK calls are blocking and currently offloaded at route-level.
- Query `focus_area` filtering is text-based only and does not provide semantic ranking.
- Error envelope has been introduced in routes, but full endpoint-level consistency still needs dedicated tests.
- Session store currently uses local SQLite; no encryption-at-rest or external KMS integration.
- CI workflow is still pending.

## Security Model

Current controls:

- typed input validation via Pydantic
- no token persistence by design
- environment variable based secret loading

Gaps tracked in roadmap:

- standard error envelope and explicit failure taxonomy
- stronger token handling lifecycle
- better observability for operational/security events

## Related Documents

- [README.md](README.md)
- [TODO.md](TODO.md)
- [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md)
- [mcp_definition.yaml](mcp_definition.yaml)
