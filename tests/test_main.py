from fastapi.testclient import TestClient

from main import app, grants_api, google_services_manager


client = TestClient(app)


def test_query_grants_response_contains_metadata(monkeypatch):
    async def fake_search_grants(_keyword: str, limit: int = 20):
        return [
            {
                "opportunity_number": "REAL-1",
                "title": "Real Grant",
                "agency": "Agency",
                "close_date": "December 01, 2026",
            }
        ]

    monkeypatch.setattr(grants_api, "search_grants", fake_search_grants)

    response = client.post(
        "/query_grants",
        json={"keyword": "energy", "max_results": 5}
    )

    assert response.status_code == 200
    body = response.json()
    assert "fallback_used" in body
    assert "data_source" in body
    assert body["fallback_used"] is False
    assert body["data_source"] == "grants_gov"


def test_manage_google_services_invalid_date_returns_422():
    response = client.post(
        "/manage_google_services",
        json={
            "grant_title": "Grant",
            "deadline_date": "31/12/2026",
            "oauth_token": "token",
        },
    )
    assert response.status_code == 422


def test_manage_google_services_critical_failure_returns_error_envelope(monkeypatch):
    def fake_execute_services(_input_data):
        return {"status": "CRITICAL_FAILURE", "error": "boom"}

    monkeypatch.setattr(
        google_services_manager,
        "execute_services",
        fake_execute_services
    )

    response = client.post(
        "/manage_google_services",
        json={
            "grant_title": "Grant",
            "deadline_date": "2026-12-31",
            "oauth_token": "token",
        },
    )

    assert response.status_code == 502
    body = response.json()
    assert body["code"] == "GOOGLE_SERVICES_CRITICAL_FAILURE"
    assert "message" in body
