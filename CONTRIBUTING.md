# Contributing to Grant Hunter MCP

Thank you for your interest in contributing. This guide explains what belongs in this repository, what does not, and how to submit changes.

## Repository Role

This repository contains the **public MCP server** for Grant Hunter. It exposes a set of HTTP endpoints that MCP-compatible clients can call for grant discovery, pitch generation, and Google Workspace integration.

This is **not** the full Grant Hunter product. The private product layer—including the user-facing UI, workflow orchestration, and end-user authentication—lives in a separate private repository. See [Non-Goals](#non-goals) for a full list of out-of-scope items.

## What Belongs Here

Pull requests that fit this repository must target one or more of the following:

| Area | Examples |
|---|---|
| MCP endpoint behavior | New routes, input/output schema changes, error handling |
| External API integrations | Grants.gov search, Gemini pitch generation, Google Workspace actions |
| Pydantic models | Input/output/error schema definitions in `pydantic_models.py` |
| Fallback and resilience logic | Mock data, retry/backoff, template pitch fallback |
| Documentation | README, TECHNICAL, ARCHITECTURE_REVIEW, this file |
| Tests | Unit and integration tests for MCP endpoints and components |
| GitHub Actions and scripts | Workflows in `.github/` and scripts in `scripts/` |

## Non-Goals

The following are **out of scope** for this public repository:

- User-facing UI or frontend components
- End-to-end product workflows that span the private product layer
- User account management, billing, or tenancy logic
- Full OAuth2 token lifecycle service (tracked as a future roadmap item; the current server accepts per-request tokens)
- Kubernetes/Helm deployment templates (tracked in roadmap)
- Any private product business logic not directly related to MCP endpoints

If your change touches one of these areas, it belongs in the private product repository instead.

## Getting Started

1. **Fork** the repository and create a feature branch from `main`.
2. **Install dependencies** and configure your environment:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Set GEMINI_API_KEY and other variables as needed
   ```
3. **Read the relevant docs** before coding:
   - [README.md](README.md) — verified capabilities and API reference
   - [TECHNICAL.md](TECHNICAL.md) — component architecture and data flow
   - [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md) — known risks and remediation backlog
   - [TODO.md](TODO.md) — prioritized roadmap and open items

## Submitting a Pull Request

- Keep PRs focused. One logical change per PR is preferred.
- Update documentation in the same PR as behavior changes. Do not let docs drift from code.
- Add or update tests for any new or modified behavior.
- Never commit secrets (`.env`, API keys, OAuth tokens).
- Reference the related issue number in your PR description (e.g., `Closes #42`).

## Code Style

- Python 3.11+
- Follow existing patterns for Pydantic model definitions and FastAPI route structure.
- Input validation belongs in Pydantic models, not route handlers.
- Prefer async code paths. Blocking I/O in route handlers is tracked as a known issue (AR-01).

## Questions

Open a GitHub issue or start a discussion if you are unsure whether a change belongs in this repository.
