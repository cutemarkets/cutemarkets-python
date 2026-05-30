"""Resource tests for stock data and paper trading namespaces."""

from __future__ import annotations

import json


def test_product_scoped_keys_and_stock_routes(monkeypatch, make_client, recorder) -> None:
    monkeypatch.setenv("CUTEMARKETS_API_KEY", "cm_default")
    monkeypatch.setenv("CUTEMARKETS_STOCKS_API_KEY", "cm_stock_env")
    client = make_client(
        {
            "/v1/stocks/snapshot/AAPL/": {
                "status": "OK",
                "ticker": {"ticker": "AAPL", "lastTrade": {"p": 190.1}},
            },
            "/v1/stocks/aggs/AAPL/1/day/2026-05-01/2026-05-06/": {
                "status": "OK",
                "request_id": "cm_stock_aggs",
                "results": [{"T": "AAPL", "o": 190, "h": 195, "l": 189, "c": 194, "v": 1000, "t": 1}],
                "next_url": "https://api.cutemarkets.com/v1/stocks/aggs/AAPL/1/day/next",
            },
            "/v1/stocks/aggs/AAPL/1/day/next": {
                "status": "OK",
                "results": [{"T": "AAPL", "o": 194, "h": 196, "l": 193, "c": 195, "v": 1000, "t": 2}],
            },
        },
        api_key=None,
    )

    snap = client.stocks.snapshot("AAPL")
    assert snap.ticker == "AAPL"
    assert recorder.last_auth == "Bearer cm_stock_env"

    page = client.stocks.aggs.range("AAPL", 1, "day", "2026-05-01", "2026-05-06", limit=2)
    assert page.results[0].close == 194
    rows = list(page.iter_all())
    assert [row.close for row in rows] == [194, 195]
    assert recorder.last_auth == "Bearer cm_stock_env"


def test_explicit_api_key_overrides_product_env_for_stocks(monkeypatch, make_client, recorder) -> None:
    monkeypatch.setenv("CUTEMARKETS_STOCKS_API_KEY", "cm_stock_env")
    client = make_client(
        {"/v1/stocks/trades/AAPL/last/": {"status": "OK", "results": {"T": "AAPL", "p": 190.1}}},
        api_key="cm_explicit",
    )
    last = client.stocks.trades.last("AAPL")
    assert last.price == 190.1
    assert recorder.last_auth == "Bearer cm_explicit"


def test_product_specific_explicit_key_overrides_default(make_client, recorder) -> None:
    client = make_client(
        {"/v1/stocks/quotes/AAPL/last/": {"status": "OK", "results": {"T": "AAPL", "p": 190, "P": 191}}},
        api_key="cm_default",
        stocks_api_key="cm_stock_explicit",
    )
    quote = client.stocks.quotes.last("AAPL")
    assert quote.bid_price == 190
    assert recorder.last_auth == "Bearer cm_stock_explicit"


def test_paper_trading_routes_and_request_bodies(make_client, recorder) -> None:
    account_id = "11111111-1111-1111-1111-111111111111"
    order_id = "22222222-2222-2222-2222-222222222222"
    paper_client = make_client(
        {
            "/v1/paper/accounts/": {
                "account": {
                    "id": account_id,
                    "name": "agent-sandbox",
                    "cash": "100000.0000",
                    "generation": 1,
                },
                "summary": {"cash": "100000.0000", "equity": "100000.0000"},
            },
            f"/v1/paper/accounts/{account_id}/orders/": {
                "id": order_id,
                "symbol": "AAPL",
                "qty": "1.000000",
                "side": "buy",
                "type": "market",
                "status": "filled",
            },
            f"/v1/paper/accounts/{account_id}/orders/{order_id}/": {
                "id": order_id,
                "symbol": "AAPL",
                "status": "canceled",
            },
        },
        api_key="cm_default",
        paper_api_key="cm_paper",
    )
    created = paper_client.paper.accounts.create(name="agent-sandbox", initial_cash="100000")
    assert created.account.id == account_id
    assert recorder.last_auth == "Bearer cm_paper"
    assert json.loads(recorder.last.content)["name"] == "agent-sandbox"

    order = paper_client.paper.orders.submit(
        account_id,
        symbol="AAPL",
        qty="1",
        side="buy",
        type="market",
        client_order_id="agent-aapl-1",
    )
    assert order.status == "filled"
    assert json.loads(recorder.last.content)["client_order_id"] == "agent-aapl-1"

    canceled = paper_client.paper.orders.cancel(account_id, order_id)
    assert canceled.status == "canceled"
