"""Resource tests for ``client.tickers``."""

from __future__ import annotations


def test_search_returns_page(make_client, recorder) -> None:
    client = make_client(
        {
            "/v1/tickers/search/": {
                "status": "OK",
                "request_id": "cm_ts",
                "results": [
                    {"symbol": "NFLX", "name": "NetFlix Inc"},
                ],
            }
        }
    )
    page = client.tickers.search(query="NFLX", limit=8)
    assert page.results[0].symbol == "NFLX"
    assert page.results[0].name == "NetFlix Inc"
    assert dict(recorder.last.url.params) == {"query": "NFLX", "limit": "8"}


def test_expirations_returns_envelope_with_ticker(make_client) -> None:
    payload = {
        "status": "OK",
        "request_id": "cm_ex",
        "ticker": "NFLX",
        "results": ["2026-04-02", "2026-04-10", "2026-04-17"],
    }
    client = make_client({"/v1/tickers/expirations/NFLX/": payload})
    result = client.tickers.expirations("NFLX")
    assert result.ticker == "NFLX"
    assert result.results == ["2026-04-02", "2026-04-10", "2026-04-17"]
    assert result.raw == payload
