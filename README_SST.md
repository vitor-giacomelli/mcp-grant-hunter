# StartupFundingAgent (Grant Hunter MCP) — Single Source of Truth

## 0. Context Bridge

- **Vault Path:** `C:\obsidian\Logs`
- **Documentation Home:** [00_Home](file:///c:/obsidian/Logs/00_Home) | [Schema](file:///c:/obsidian/Logs/00_Home/Bimodal_Vault_Schema_Dictionary.md)
- **Vault Link:** `[[04_Projects/Project_MCP_Grant_Hunter]]` *(create if missing)*
- **Research Branch:** Validates "Production-Grade MCP" and "Resilient API Retry" patterns. Demonstrates autonomous funding workflows.

---

## A. Project Overview

**StartupFundingAgent** (repo `mcp-grant-hunter`) is a Model Context Protocol (MCP) server that exposes three tools for grant discovery and pitch prep: query Grants.gov, draft a pitch via Gemini, and create Gmail drafts/Calendar events for deadlines. It is a FastAPI service packaged for Docker; data is fetched live from Grants.gov with retry and falls back to mock data on failure.

## B. Technical Overview

What it does:
- `POST /query_grants`: keyword search against Grants.gov via `requests` with 5x exponential backoff; formats and truncates results; returns mock grants if the API fails or is empty.
- `POST /generate_pitch`: uses Google `genai` client (Gemini 2.0 Flash by default, fallback to 2.0 Flash Lite) and a Triple-Horizon prompt; falls back to a deterministic template if no API key or both calls fail.
- `POST /manage_google_services`: accepts a raw OAuth token, creates a Gmail draft + Calendar event; `DEMO_MODE=TRUE` short-circuits external calls and returns canned links.

Tech stack:
- Python 3.11, FastAPI, Uvicorn; Pydantic v2 models for input/output validation; `requests` for Grants.gov; Google `genai` + Gmail/Calendar client libraries.
- Env handling: `.env` file is loaded from the script directory (Path(__file__).parent/.env); `GEMINI_API_KEY` required for live pitches.
- Deployment: Dockerfile uses `python:3.11-slim`; local run via `pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8000`.

## C. Decision Context (SST-critical)

- MCP chosen so agent clients (Claude Desktop, etc.) can call the server as a tool provider without bespoke SDKs.
- FastAPI selected for typed request models and generated OpenAPI; endpoints are `async` but external calls are synchronous today.
- Mock fallback and DEMO_MODE exist to keep the loop working when Grants.gov or Google access is unavailable during demos.

## D. Constraints & Non-Goals

- No persistence, accounts, or RBAC; OAuth tokens are supplied per request and never refreshed or stored.
- Network is synchronous (`requests`); no background jobs, queues, or caching.
- No rate limiting, auditing, or detailed error taxonomy; Google errors are surfaced as strings.
- Tests are absent; CI/CD not configured.

## E. Signal Value

- Shows an MCP server combining gov-data search, LLM generation, and Google Workspace side-effects with schema validation and retry/backoff.
- Documents fallbacks (mock grants, template pitch, DEMO_MODE) for degraded environments.

## F. Project Classification

- Category: MCP backend service (grant discovery + pitch drafting)
- Audience: founders, grant writers, agent integrators
- Strategic role: agent-ready backend for funding workflows

## G. Disclosure Level

- Public-safe: ✅ (no secrets committed)
- Can be mentioned: Yes; NDA: No; Transferable: Yes

## H. Lifecycle Intent

- Current state: functional MCP MVP; sync network; no tests; manual OAuth token handling.
- Done means: async/httpx network, tests in place, CI, optional UI, token lifecycle handled, and resilience validated without relying on DEMO/mocks for normal runs.

## I. TODO / Technical Debt (non-speculative)

- Add unit/integration tests (FastAPI endpoints, Grants.gov search, pitch generator, Google manager with mocks).
- Migrate Grants.gov client to `httpx` with async calls; consider caching recent searches.
- Harden Google flows: token refresh, clearer error mapping, per-request validation of date parsing.
- CI/CD: GitHub Actions for lint/test/build; Docker publish.
- Optional: expand data sources (e.g., Transferegov), add React/Next.js dashboard for users who avoid MCP clients.

## J. Architecture Diagram

```mermaid
graph TD
    Client[MCP Client] -->|HTTP/SSE| API[FastAPI Server]

    subgraph Tools
        API -->|/query_grants| Grants[GrantsGovAPI (requests + retry)]
        API -->|/generate_pitch| Gemini[Gemini (genai client)]
        API -->|/manage_google_services| Google[Google Workspace SDKs]
    end

    Grants -->|Fallback| Mock[Mock Grants]
    Gemini -->|Fallback| Template[Template Pitch]
    Google -->|DEMO_MODE| Demo[Simulated success]
```
