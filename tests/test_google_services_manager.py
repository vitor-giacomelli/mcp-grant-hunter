from google_services_manager import GoogleServicesManager
from pydantic_models import GoogleServicesInput


def test_build_credentials_access_token_only():
    manager = GoogleServicesManager()
    input_data = GoogleServicesInput(
        grant_title="Grant",
        deadline_date="2026-12-15",
        oauth_token="access-token",
    )

    _, meta = manager._build_credentials(input_data)

    assert meta["oauth_status"] == "ACCESS_TOKEN_ONLY"
    assert meta["token_refreshed"] is False
    assert meta["oauth_error"] is None


def test_build_credentials_refresh_success(monkeypatch):
    class FakeCredentials:
        def __init__(self, token, refresh_token, token_uri, client_id, client_secret):
            self.token = token

        def refresh(self, _request):
            self.token = "new-access-token"

    monkeypatch.setattr("google_services_manager.Credentials", FakeCredentials)
    monkeypatch.setattr("google_services_manager.Request", lambda: object())

    manager = GoogleServicesManager()
    input_data = GoogleServicesInput(
        grant_title="Grant",
        deadline_date="2026-12-15",
        oauth_token="old-access-token",
        refresh_token="refresh-token",
        client_id="client-id",
        client_secret="client-secret",
    )

    creds, meta = manager._build_credentials(input_data)

    assert creds.token == "new-access-token"
    assert meta["oauth_status"] == "REFRESH_SUCCESS"
    assert meta["token_refreshed"] is True
    assert meta["oauth_error"] is None


def test_build_credentials_refresh_failure(monkeypatch):
    class FakeCredentials:
        def __init__(self, token, refresh_token, token_uri, client_id, client_secret):
            self.token = token

        def refresh(self, _request):
            raise RuntimeError("refresh failed")

    monkeypatch.setattr("google_services_manager.Credentials", FakeCredentials)
    monkeypatch.setattr("google_services_manager.Request", lambda: object())

    manager = GoogleServicesManager()
    input_data = GoogleServicesInput(
        grant_title="Grant",
        deadline_date="2026-12-15",
        oauth_token="old-access-token",
        refresh_token="refresh-token",
        client_id="client-id",
        client_secret="client-secret",
    )

    creds, meta = manager._build_credentials(input_data)

    assert creds.token == "old-access-token"
    assert meta["oauth_status"] == "REFRESH_FAILED"
    assert meta["token_refreshed"] is False
    assert meta["oauth_error"] is not None
