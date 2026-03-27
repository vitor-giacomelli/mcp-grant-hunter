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
