import pytest

from grants_gov_api import GrantsGovAPI


@pytest.mark.asyncio
async def test_search_grants_uses_mock_fallback_when_empty(monkeypatch):
    api = GrantsGovAPI()

    async def fake_search_by_keyword(_keyword: str, limit: int = 20):
        return []

    monkeypatch.setattr(api, "_search_by_keyword", fake_search_by_keyword)

    result = await api.search_grants("energy", limit=1)

    assert len(result) == 1
    assert result[0]["opportunity_number"] == GrantsGovAPI.MOCK_GRANTS[0]["opportunity_number"]


@pytest.mark.asyncio
async def test_search_grants_deduplicates_and_sorts(monkeypatch):
    api = GrantsGovAPI()

    async def fake_search_by_keyword(_keyword: str, limit: int = 20):
        return [
            {"opportunity_number": "A1", "close_date": "December 20, 2026"},
            {"opportunity_number": "A1", "close_date": "December 20, 2026"},
            {"opportunity_number": "B1", "close_date": "December 10, 2026"},
        ]

    monkeypatch.setattr(api, "_search_by_keyword", fake_search_by_keyword)

    result = await api.search_grants("energy", limit=10)

    assert len(result) == 2
    assert result[0]["opportunity_number"] == "B1"
    assert result[1]["opportunity_number"] == "A1"
