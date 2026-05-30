"""Async surface: smoke-level parity with the sync client."""

from __future__ import annotations

import datetime as dt


async def test_async_chain_and_iter_chain(make_async_client) -> None:
    payload = {
        "status": "OK",
        "request_id": "cm_ac",
        "results": [
            {
                "break_even_price": 100.0,
                "details": {"ticker": "O:NFLX260402C00100000", "strike_price": 100},
            }
        ],
    }
    client = make_async_client({"/v1/options/chain/NFLX/": payload})
    page = await client.options.chain("NFLX", limit=5)
    assert len(page) == 1
    assert page.results[0].details.ticker == "O:NFLX260402C00100000"
    assert client.last_request_id == "cm_ac"
    assert client.last_rate_limit.plan == "Developer"

    rows = []
    async for contract in client.options.iter_chain("NFLX", limit=5):
        rows.append(contract)
    assert len(rows) == 1
    await client.aclose()


async def test_async_status_without_auth(
    monkeypatch, make_async_client
) -> None:
    monkeypatch.delenv("CUTEMARKETS_API_KEY", raising=False)
    client = make_async_client(
        {
            "/v1/status/": {
                "status": "ok",
                "request_id": "cm_ast",
                "services": {"api": {"status": "ok"}},
            }
        },
        api_key=None,
    )
    result = await client.status()
    assert result.is_ok
    await client.aclose()


async def test_async_aggs_range_and_previous(make_async_client) -> None:
    range_payload = {
        "status": "OK",
        "request_id": "cm_rg",
        "results": [
            {"c": 5.05, "o": 5.0, "t": 1000, "v": 10, "h": 5.1, "l": 4.9, "n": 2, "vw": 5.0},
        ],
    }
    prev_payload = {
        "status": "OK",
        "request_id": "cm_pv",
        "results": [
            {"c": 22.7, "o": 22.07, "T": "O:X", "t": 1775160000000, "v": 4, "h": 22.7, "l": 22.07, "n": 4, "vw": 22.42},
        ],
    }
    client = make_async_client(
        {
            "/v1/options/aggs/O:X/1/day/2026-01-01/2026-04-01/": range_payload,
            "/v1/options/aggs/O:X/prev/": prev_payload,
        }
    )
    page = await client.options.aggs.range(
        "O:X", 1, "day", dt.date(2026, 1, 1), dt.date(2026, 4, 1), limit=5
    )
    assert page.results[0].close == 5.05

    prev = await client.options.aggs.previous("O:X")
    assert prev.close == 22.7
    assert prev.ticker == "O:X"
    await client.aclose()


async def test_async_stocks_and_paper_namespaces(make_async_client, recorder) -> None:
    account_id = "11111111-1111-1111-1111-111111111111"
    client = make_async_client(
        {
            "/v1/stocks/tickers/AAPL/": {
                "status": "OK",
                "results": {"ticker": "AAPL", "name": "Apple Inc."},
            },
            "/v1/paper/accounts/": {
                "account": {"id": account_id, "name": "Async", "cash": "100000.0000"},
                "summary": {"cash": "100000.0000", "equity": "100000.0000"},
            },
        },
        api_key="cm_default",
        stocks_api_key="cm_stock",
        paper_api_key="cm_paper",
    )
    ticker = await client.stocks.tickers.get("AAPL")
    assert ticker.ticker == "AAPL"
    assert recorder.last_auth == "Bearer cm_stock"

    account = await client.paper.accounts.create(name="Async")
    assert account.account.id == account_id
    assert recorder.last_auth == "Bearer cm_paper"
    await client.aclose()
