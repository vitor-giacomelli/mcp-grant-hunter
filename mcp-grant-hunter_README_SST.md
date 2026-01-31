# StartupFundingAgent (mcp-grant-hunter)

## A. Project Overview
**StartupFundingAgent** is an enterprise-grade Model Context Protocol (MCP) server designed to autonomously discover non-dilutive funding and generate high-probability pitch drafts. It automates the "Hunt" phase of fundraising by integrating government data sources with advanced AI generation.

**Intended Use Cases:**
*   **Startup Founders:** Finding SBIR/STTR grants without manual searching.
*   **Grant Writers:** Generating first drafts of pitch narratives.
*   **Accelerators:** providing automated deal-flow tools to cohorts.

**Current Maturity:** Production / Enterprise Ready.

## B. Technical Overview
**Functionality:**
A Dockerized FastAPI server exposing MCP tools for:
1.  `query_grants`: Real-time search of Grants.gov (with retry logic).
2.  `generate_pitch`: Gemini 2.0 Flash-powered drafting.
3.  `manage_google_services`: Gmail/Calendar orchestration.

**Architecture:**
*   **Core:** Python 3.11, FastAPI.
*   **AI:** Google Gemini 2.0 Flash (`google-generativeai`).
*   **Resilience:** Exponential backoff (5x retries) for external APIs.
*   **Security:** Ephemeral OAuth tokens, extensive Pydantic validation.

**How to Run:**
1.  `docker build -t grant-hunter-mcp .`
2.  `docker run -p 8080:8080 --env-file .env grant-hunter-mcp`

## C. Decision Context
**Why this exists:**
Grant discovery is fragmented and pitch writing is repetitive ("Blank Page" syndrome).
**Chosen Path:**
MCP Architecture was chosen to facilitate seamless integration with AI Chat Interfaces (Claude Desktop, etc.), allowing users to "Chat with the Grant Database."

## D. Constraints & Non-Goals
*   **No PII Storage:** Stateless by design; logs are sanitized.
*   **Government API Limits:** Dependent on Grants.gov uptime/rate limits.

## E. Signal Value
Proves competence in:
*   **Resilient Systems:** Implementing "Lethal Trifecta Mitigation" (Security, Reliability, Safety).
*   **AI Integration:** Structured prompting with "Triple-Horizon Framework" for consistent outputs.
*   **Containerization:** Production-ready Docker setups.

## F. Project Classification
*   **Category:** MCP Server / Automation Tool.
*   **Intended Audience:** Founders, Grant Professionals.
*   **Strategic Role:** Commercial Product / Utility.

## G. Disclosure Level
*   **Public-safe:** ✅ Yes.
*   **Can be mentioned:** Yes.
*   **Requires NDA:** No.

## H. Lifecycle Intent
*   **Condition for Completion:** Functional Grants.gov integration + Pitch Gen (Achieved).
*   **Next States:**
    *   V2: Async Network Layer (`httpx`).
    *   Expansion to Brazilian Grant sources.

## I. TODO / Technical Debt
**Technical Debt:**
*   **Sync Blocking:** Currently uses `requests`; needs migration to `httpx` for high concurrency.
*   **Testing:** Test suite is pending implementation.

**Missing Implementation:**
*   [ ] **Dashboard:** Next.js UI for visual pipeline management.
*   [ ] **RBAC:** Multi-user support.
*   [ ] **Analytics:** Success rate tracking.

## J. Architecture Diagram

```mermaid
graph TD
    Client[MCP Client (Claude/Agent)] -->|Request| FastAPI

    subgraph Grant Hunter MCP
        FastAPI -->|Route| Tools

        Tools -->|Query| GrantAPI[Grants.gov]
        Tools -->|Draft| Gemini[Gemini 2.0]
        Tools -->|Action| Google[Google Workspace]
    end

    GrantAPI -->|Retry Logic| Tools
    Gemini -->|Structured Output| Tools
    Google -->|Draft/Event| UserAcct[User Account]
```
