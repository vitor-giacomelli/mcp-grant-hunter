# Project Roadmap & Technical Debt

This document tracks the known technical debt, planned improvements, and future roadmap for the **StartupFundingAgent** (Grant Hunter MCP).

---

## 🚨 High Priority (Technical Debt)

### 1. Testing Infrastructure (CRITICAL)
- [ ] **Create `tests/` directory**: The project currently lacks a dedicated test suite.
- [ ] **Unit Tests**:
    - [ ] `tests/test_grants_api.py`: Test `search_grants` with mocked responses.
    - [ ] `tests/test_pitch_generator.py`: Test prompt construction and fallback logic.
    - [ ] `tests/test_pydantic_models.py`: Verify validation rules.
- [ ] **Integration Tests**:
    - [ ] `tests/test_main.py`: Test FastAPI endpoints using `TestClient`.

### 2. Code Refactoring
- [ ] **Refactor `grants_gov_api.py`**:
    - [ ] The `search_grants` method is doing too much (searching, deduplicating, sorting, formatting). Break this down into smaller, testable private methods.
    - [ ] Move `MOCK_GRANTS` constant to a separate `mock_data.py` file to declutter the API logic.
- [ ] **Refactor `pitch_generator.py`**:
    - [ ] Extract the prompt template into a separate text file or constant for easier editing.

---

## 🚀 Future Implementations (V2 Roadmap)

### 1. Architecture & Performance
- [ ] **Async Network Layer**: Migrate from `requests` (synchronous) to `httpx` (asynchronous) in `grants_gov_api.py`. This is crucial for handling high concurrency in a production environment.
- [ ] **Caching**: Implement Redis or in-memory caching for grant search results to reduce API calls and improve latency.

### 2. Features
- [ ] **Full OAuth2 Flow**: Implement a dedicated authentication service to handle the full OAuth2 lifecycle (token exchange, refresh tokens) instead of relying on manual token passing.
- [ ] **Brazil Expansion**: Add support for Brazilian grant sources (Transferegov, Sebrae, FAPESP) as per the "Brazil Grant Hunter" initiative.
- [ ] **User Interface**: Build a React/Next.js dashboard to visualize the grant pipeline and allow for easier interaction than the raw MCP interface.

### 3. DevOps
- [ ] **CI/CD Pipeline**: Set up GitHub Actions for automated testing and Docker image building.
- [ ] **Helm Charts**: Create Helm charts for Kubernetes deployment.

---

## 💡 Suggestions / Nice-to-Have

- [ ] **Grant Matching Engine**: Implement a more sophisticated matching algorithm (using vector embeddings) to match startups with grants based on semantic similarity, rather than just keywords.
- [ ] **Multi-Language Support**: Localize the pitch generation to support other languages (Spanish, Portuguese, French).
