from pydantic import ValidationError

from pydantic_models import GoogleServicesInput, GrantsQueryOutput


def test_google_services_input_accepts_supported_deadline_formats():
    first = GoogleServicesInput(
        grant_title="Grant A",
        deadline_date="December 15, 2026",
        oauth_token="token"
    )
    second = GoogleServicesInput(
        grant_title="Grant B",
        deadline_date="2026-12-15",
        oauth_token="token"
    )

    assert first.deadline_date == "December 15, 2026"
    assert second.deadline_date == "2026-12-15"


def test_google_services_input_accepts_session_id_without_oauth_token():
    payload = GoogleServicesInput(
        grant_title="Grant Session",
        deadline_date="2026-12-15",
        oauth_session_id="session-123",
    )
    assert payload.oauth_session_id == "session-123"
    assert payload.oauth_token is None


def test_google_services_input_rejects_invalid_deadline_date():
    try:
        GoogleServicesInput(
            grant_title="Grant C",
            deadline_date="15/12/2026",
            oauth_token="token"
        )
        assert False, "Expected ValidationError for invalid deadline_date"
    except ValidationError as exc:
        assert "deadline_date must match" in str(exc)


def test_grants_query_output_defaults_metadata_fields():
    payload = GrantsQueryOutput(
        results=[],
        total_count=0,
        execution_time_ms=1.0
    )
    assert payload.fallback_used is False
    assert payload.data_source == "grants_gov"


def test_google_services_input_rejects_whitespace_oauth_token():
    try:
        GoogleServicesInput(
            grant_title="Grant D",
            deadline_date="2026-12-15",
            oauth_token="bad token value",
        )
        assert False, "Expected ValidationError for invalid oauth_token"
    except ValidationError as exc:
        assert "oauth_token cannot contain whitespace" in str(exc)


def test_google_services_input_requires_token_or_session_id():
    try:
        GoogleServicesInput(
            grant_title="Grant Missing Auth",
            deadline_date="2026-12-15",
        )
        assert False, "Expected ValidationError when no auth source is provided"
    except ValidationError as exc:
        assert "Either oauth_token or oauth_session_id must be provided" in str(exc)


def test_google_services_input_requires_client_credentials_for_refresh_token():
    try:
        GoogleServicesInput(
            grant_title="Grant E",
            deadline_date="2026-12-15",
            oauth_token="token",
            refresh_token="refresh-token",
        )
        assert False, "Expected ValidationError when refresh_token has no client credentials"
    except ValidationError as exc:
        assert "client_id and client_secret are required" in str(exc)


def test_google_services_input_accepts_refresh_token_flow_fields():
    payload = GoogleServicesInput(
        grant_title="Grant F",
        deadline_date="2026-12-15",
        oauth_token="token",
        refresh_token="refresh-token",
        client_id="client-id",
        client_secret="client-secret",
    )
    assert payload.token_uri == "https://oauth2.googleapis.com/token"
