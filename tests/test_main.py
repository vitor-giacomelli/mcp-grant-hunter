from fastapi.testclient import TestClient

from main import (
    app,
    grants_api,
    google_services_manager,
    pitch_generator,
    oauth_session_store,
)


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


def test_query_grants_returns_error_envelope_on_search_error(monkeypatch):
    async def fake_search_grants(_keyword: str, limit: int = 20):
        raise RuntimeError("upstream unavailable")

    monkeypatch.setattr(grants_api, "search_grants", fake_search_grants)

    response = client.post(
        "/query_grants",
        json={"keyword": "energy", "max_results": 1}
    )

    assert response.status_code == 502
    body = response.json()
    assert body["code"] == "QUERY_GRANTS_UPSTREAM_FAILURE"
    assert "message" in body


def test_query_grants_sets_fallback_metadata_for_mock_results(monkeypatch):
    async def fake_search_grants(_keyword: str, limit: int = 20):
        return [
            {
                "opportunity_number": "DE-FOA-0003001",
                "title": "Mock Grant",
                "agency": "DOE",
                "close_date": "December 15, 2025",
            }
        ]

    monkeypatch.setattr(grants_api, "search_grants", fake_search_grants)

    response = client.post(
        "/query_grants",
        json={"keyword": "energy", "max_results": 1}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["fallback_used"] is True
    assert body["data_source"] == "mock_fallback"


def test_query_grants_applies_focus_area_filter(monkeypatch):
    async def fake_search_grants(_keyword: str, limit: int = 20):
        return [
            {
                "opportunity_number": "R1",
                "title": "Renewable Grid Optimization Grant",
                "agency": "Agency",
                "close_date": "December 01, 2026",
                "description": "Solar and wind support",
                "category": "Energy",
            },
            {
                "opportunity_number": "A1",
                "title": "AI for Education",
                "agency": "Agency",
                "close_date": "December 02, 2026",
                "description": "K-12 improvements",
                "category": "Education",
            },
        ]

    monkeypatch.setattr(grants_api, "search_grants", fake_search_grants)

    response = client.post(
        "/query_grants",
        json={
            "keyword": "grant",
            "max_results": 5,
            "focus_area": "renewable",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total_count"] == 1
    assert body["results"][0]["id"] == "R1"


def test_request_id_is_added_to_response_header():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("x-request-id")


def test_create_oauth_session_endpoint(monkeypatch):
    monkeypatch.setattr(
        oauth_session_store,
        "create_session",
        lambda oauth_token, refresh_token, client_id, client_secret, token_uri, label: {
            "session_id": "abc123",
            "created_at": "2026-03-28T00:00:00+00:00",
            "label": label,
        },
    )

    response = client.post(
        "/oauth_sessions",
        json={
            "oauth_token": "access-token",
            "label": "default",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == "abc123"
    assert body["label"] == "default"


def test_delete_oauth_session_endpoint_not_found(monkeypatch):
    monkeypatch.setattr(oauth_session_store, "delete_session", lambda _sid: False)
    response = client.delete("/oauth_sessions/not-found")
    assert response.status_code == 404
    assert response.json()["code"] == "OAUTH_SESSION_NOT_FOUND"


def test_manage_google_services_resolves_session_and_updates_token(monkeypatch):
    monkeypatch.setattr(
        oauth_session_store,
        "get_session",
        lambda _sid: {
            "oauth_token": "stored-access-token",
            "refresh_token": "stored-refresh-token",
            "client_id": "stored-client-id",
            "client_secret": "stored-client-secret",
            "token_uri": "https://oauth2.googleapis.com/token",
        },
    )

    updated = {"called": False}

    def fake_update_access_token(_sid, _token):
        updated["called"] = True
        return True

    monkeypatch.setattr(
        oauth_session_store,
        "update_access_token",
        fake_update_access_token,
    )

    def fake_execute_services(input_data):
        assert input_data.oauth_token == "stored-access-token"
        return {
            "gmail_status": "SUCCESS",
            "calendar_status": "SUCCESS",
            "errors": [],
            "oauth_status": "REFRESH_SUCCESS",
            "token_refreshed": True,
            "resolved_oauth_token": "new-access-token",
        }

    monkeypatch.setattr(
        google_services_manager,
        "execute_services",
        fake_execute_services,
    )

    response = client.post(
        "/manage_google_services",
        json={
            "grant_title": "Grant",
            "deadline_date": "2026-12-31",
            "oauth_session_id": "session-1",
        },
    )
    assert response.status_code == 200
    assert updated["called"] is True
    body = response.json()
    assert body["oauth_status"] == "REFRESH_SUCCESS"


def test_manage_google_services_session_not_found_returns_404(monkeypatch):
    monkeypatch.setattr(oauth_session_store, "get_session", lambda _sid: None)
    response = client.post(
        "/manage_google_services",
        json={
            "grant_title": "Grant",
            "deadline_date": "2026-12-31",
            "oauth_session_id": "missing-session",
        },
    )
    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "OAUTH_SESSION_NOT_FOUND"


def test_generate_pitch_value_error_returns_400(monkeypatch):
    def fake_generate_pitch(_input_data):
        raise ValueError("invalid prompt input")

    monkeypatch.setattr(pitch_generator, "generate_pitch", fake_generate_pitch)

    response = client.post(
        "/generate_pitch",
        json={
            "startup_name": "A",
            "focus_area": "B",
            "grant_title": "C",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["code"] == "PITCH_INPUT_ERROR"
    assert "message" in body


def test_generate_pitch_unhandled_error_returns_502(monkeypatch):
    def fake_generate_pitch(_input_data):
        raise RuntimeError("provider failure")

    monkeypatch.setattr(pitch_generator, "generate_pitch", fake_generate_pitch)

    response = client.post(
        "/generate_pitch",
        json={
            "startup_name": "A",
            "focus_area": "B",
            "grant_title": "C",
        },
    )

    assert response.status_code == 502
    body = response.json()
    assert body["code"] == "PITCH_GENERATION_FAILURE"
    assert "message" in body


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


def test_manage_google_services_value_error_returns_400(monkeypatch):
    def fake_execute_services(_input_data):
        raise ValueError("invalid token payload")

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

    assert response.status_code == 400
    body = response.json()
    assert body["code"] == "GOOGLE_SERVICES_INPUT_ERROR"
    assert "message" in body
