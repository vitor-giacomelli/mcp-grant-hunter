# StartupFundingAgent - Production-Grade MCP
### *From Zero to Funding Pitch in 60 Seconds*

**StartupFundingAgent** (also known as **Grant Hunter MCP**) is an enterprise-ready Model Context Protocol (MCP) server designed to autonomously hunt for non-dilutive funding, generate winning pitches using advanced AI frameworks, and seamlessly integrate with Google Workspace for execution.

---

## 📖 Table of Contents

- [Core Features](#-core-features)
- [Architecture](#️-architectural-excellence)
- [Security & Resilience](#️-security--resilience-pillars)
- [Technical Stack](#️-technical-stack)
- [Setup Instructions](#-setup-instructions)
- [API Reference](#-api-reference)
- [Environment Variables](#-environment-variables)
- [Project Structure](#-project-structure)
- [MCP Integration](#-mcp-integration)
- [Development](#-development)
- [Contributing](#-contributing)
- [Future Roadmap](#-v2-scope-future-roadmap)

---

## 🚀 Core Features

This MCP exposes three powerful, production-hardened endpoints:

### 1. `/query_grants` - Intelligent Grant Discovery
*   **Real-Time Search**: Direct integration with Grants.gov API.
*   **Smart Filtering**: Deduplicates and sorts opportunities by deadline.
*   **Keyword-Based Discovery**: Search funding opportunities with flexible keyword matching.
*   **Resilient**: Implements a **5x Retry Policy with Exponential Backoff** to handle government API instability.

### 2. `/generate_pitch` - AI-Powered Pitch Architect
*   **Gemini Integration**: Leverages Google's Gemini 2.0 Flash for high-speed, high-quality generation.
*   **150-Word Precision**: Generates compelling, concise funding pitches optimized for grant applications.
*   **Triple-Horizon Framework**: Enforces a strict prompt structure (Acute Pain Point, Technical Deviation, Macro-Economic Lock) to maximize scoring potential.
*   **Graceful Fallback**: Automatic template fallback ensures business continuity even if AI services are disrupted.

### 3. `/manage_google_services` - Secure Execution
*   **Gmail Integration**: Auto-drafts personalized emails to grant officers.
*   **Calendar Sync**: Automatically adds hard deadlines to your Google Calendar.
*   **Least Privilege**: Operates with ephemeral OAuth tokens passed securely at runtime.

---

## 🏗️ Architectural Excellence

We have evolved the legacy Flask MVP into a **Containerized FastAPI MCP Server**, representing a paradigm shift in reliability and scalability.

*   **Microservices-Ready**: Stateless architecture designed for orchestration.
*   **Type-Safe**: Fully typed Python codebase for maintainability.
*   **Dockerized**: "Write Once, Run Anywhere" deployment.

---

## 🛡️ Security & Resilience Pillars

We treat security and reliability as first-class citizens, not afterthoughts.

### 1. Lethal Trifecta Mitigation (Security)
*   **Zero Hardcoded Secrets**: All API keys and Client IDs are sourced strictly from `os.environ`.
*   **Ephemeral Tokens**: OAuth tokens are consumed via request body and never stored persistently.
*   **Secure Configuration**: Comprehensive `.gitignore` ensures no secrets are committed.

### 2. Network Resilience (Reliability)
*   **Production AgentOps Standard**: We overrode the legacy `MAX_RETRY_ATTEMPTS=2` policy.
*   **5x Retry Loop**: All external API calls (Grants.gov, Google Services) implement a robust 5-attempt retry mechanism with exponential backoff to survive transient network failures (5xx/429).

### 3. Input Validation (Safety)
*   **Strict Pydantic Schemas**: Every endpoint is protected by rigorous data models (`GrantsQueryInput`, `PitchGenerateInput`, etc.).
*   **Injection Prevention**: Validated inputs prevent XSS and injection attacks before they reach business logic.

### 4. Logging Hygiene
*   **No PII in Logs**: Email bodies and pitch drafts are never logged.
*   **Configurable Log Level**: Set `LOG_LEVEL=INFO` for production; `DEBUG` for development.

---

## 🛠️ Technical Stack

*   **Runtime**: Python 3.11 (Slim Docker Image)
*   **Framework**: FastAPI (High-performance Async I/O)
*   **Server**: Uvicorn (Standard ASGI)
*   **AI**: Google Generative AI (Gemini 2.0 Flash)
*   **Integration**: Google API Client (Gmail, Calendar)
*   **Validation**: Pydantic v2

---

## ⚡ Setup Instructions

Get the agent running in seconds.

### Prerequisites

- Docker (recommended) OR Python 3.11+
- A Gemini API key (get one at [Google AI Studio](https://aistudio.google.com/app/apikey))
- (Optional) Google OAuth credentials for Google Services integration

### 1. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

**Required variables:**
- `GEMINI_API_KEY`: Your Google Gemini API key

### 2. Build the Container

```bash
docker build -t grant-hunter-mcp .
```

### 3. Run the Agent

```bash
docker run -p 8080:8080 --env-file .env grant-hunter-mcp
```

### 4. Verify

Access the auto-generated OpenAPI documentation:
`http://localhost:8080/docs`

### Alternative: Run Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`.

---

## 📚 API Reference

### Health Check

```
GET /health
```

Returns server health status.

---

### POST `/query_grants`

Search for grant opportunities.

**Request Body:**
```json
{
  "keyword": "clean energy",
  "max_results": 20,
  "focus_area": "renewable energy"
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "DE-FOA-0003001",
      "title": "AI-Driven Clean Energy Optimization SBIR",
      "agency": "Department of Energy",
      "close_date": "December 15, 2025",
      "status": "Open",
      "data_status": "COMPLETE"
    }
  ],
  "total_count": 1,
  "execution_time_ms": 1250.5
}
```

---

### POST `/generate_pitch`

Generate an AI-powered funding pitch.

**Request Body:**
```json
{
  "startup_name": "CleanTech Solutions",
  "focus_area": "Renewable Energy",
  "grant_title": "Clean Energy Innovation Grant"
}
```

**Response:**
```json
{
  "pitch_draft": "...",
  "model_used": "gemini-2.0-flash",
  "status": "SUCCESS"
}
```

---

### POST `/manage_google_services`

Create Gmail draft and Calendar event for grant deadlines.

**Request Body:**
```json
{
  "grant_title": "Clean Energy Innovation Grant",
  "deadline_date": "December 15, 2025",
  "oauth_token": "your_oauth_access_token"
}
```

**Response:**
```json
{
  "gmail_status": "SUCCESS",
  "calendar_status": "SUCCESS",
  "draft_link": "https://mail.google.com/...",
  "event_link": "https://calendar.google.com/...",
  "errors": []
}
```

---

## 🔐 Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key | - |
| `GEMINI_MODEL` | No | Gemini model to use | `gemini-2.0-flash` |
| `LOG_LEVEL` | No | Logging level | `INFO` |
| `DEMO_MODE` | No | Enable demo mode (skips real API calls) | `FALSE` |

See `.env.example` for a complete list of available variables.

---

## 📁 Project Structure

```
mcp/
├── main.py                     # FastAPI application entry point
├── grants_gov_api.py           # Grants.gov API integration
├── pitch_generator.py          # AI pitch generation with Gemini
├── google_services_manager.py  # Gmail and Calendar integration
├── pydantic_models.py          # Input/output data models
├── mcp_definition.yaml         # MCP server definition
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
└── README.md                   # This file
```

---

## 🔌 MCP Integration

This server follows the Model Context Protocol specification. Use the `mcp_definition.yaml` file to configure your MCP client.

### Using with Claude Desktop

1. Update `mcp_definition.yaml` with your server URL
2. Add the MCP server to your Claude Desktop configuration
3. Start using grant discovery and pitch generation in conversations

---

## 🧪 Development

### Running Tests

> [!WARNING]
> The `tests` directory is currently pending implementation. Please refer to `TODO.md` for the roadmap on adding unit and integration tests.

```bash
# Future command
# pytest tests/ -v
```

### Linting

```bash
flake8 . --max-line-length=79
mypy . --strict
```

### Security Notes

- **Never commit `.env` files** - Contains sensitive API keys
- **OAuth tokens are ephemeral** - Passed at runtime, never stored
- **All inputs validated** - Using Pydantic models with strict validation
- **No hardcoded secrets** - All credentials loaded from environment variables

---

## 🤝 Contributing

1. Check `TODO.md` for prioritized tasks
2. Follow the existing code style
3. Ensure all tests pass before submitting PRs
4. Never commit secrets or API keys

---

## License

- [ ] **Tests**: Add unit tests for `grants_gov_api.py`.

## Strategic Audit (2026-01-31)
- **Status**: Production / Refined.
- **Novelty**: 9/10. Autonomous funding agent.
- **Relation**: This appears to be the *clean* MCP-only version, distinct from the hybrid `grant-hunter-mcp` (Batch 9).
- **Recommendation**: Promote this as the canonical MCP implementation.
