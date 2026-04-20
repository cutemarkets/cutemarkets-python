"""Resource tests for ``client.options.*``."""

from __future__ import annotations

import datetime as dt


def test_chain_returns_page_of_snapshots(make_client, recorder) -> None:
    payload = {
        "status": "OK",
        "request_id": "cm_chain",
        "results": [
            {
                "break_even_price": 100.025,
                "details": {
                    "contract_type": "call",
                    "exercise_style": "american",
                    "expiration_date": "2026-04-02",
                    "shares_per_contract": 100,
                    "strike_price": 100,
                    "ticker": "O:NFLX260402C00100000",
                },
                "greeks": {"delta": 0.024, "gamma": 0.022, "theta": -0.13, "vega": 0.0019},
                "implied_volatility": 0.695,
                "open_interest": 14078,
                "underlying_asset": {
                    "price": 94.79,
                    "ticker": "NFLX",
                    "timeframe": "DELAYED",
                },
            }
        ],
    }
    client = make_client({"/v1/options/chain/NFLX/": payload})
    page = client.options.chain(
        "NFLX",
        contract_type="call",
        strike_price_gte=90,
        strike_price_lte=110,
        limit=50,
    )
    assert len(page) == 1
    contract = page.results[0]
    assert contract.details.ticker == "O:NFLX260402C00100000"
    assert contract.greeks.delta == 0.024
    assert contract.underlying_asset.price == 94.79

    params = dict(recorder.last.url.params)
    assert params["contract_type"] == "call"
    assert params["strike_price.gte"] == "90"
    assert params["strike_price.lte"] == "110"
    assert params["limit"] == "50"


def test_snapshot_returns_single_object(make_client) -> None:
    payload = {
        "status": "OK",
        "request_id": "cm_snap",
        "results": {
            "break_even_price": 100.025,
            "details": {
                "contract_type": "call",
                "strike_price": 100,
                "ticker": "O:NFLX260402C00100000",
            },
        },
    }
    client = make_client({"/v1/options/snapshot/NFLX/O:NFLX260402C00100000/": payload})
    snap = client.options.snapshot("NFLX", "O:NFLX260402C00100000")
    assert snap.details.ticker == "O:NFLX260402C00100000"
    assert snap.break_even_price == 100.025


def test_contracts_list_and_get(make_client, recorder) -> None:
    list_payload = {
        "status": "OK",
        "request_id": "cm_cl",
        "results": [
            {
                "cfi": "OCASPS",
                "contract_type": "call",
                "exercise_style": "american",
                "expiration_date": "2026-04-02",
                "primary_exchange": "BATO",
                "shares_per_contract": 100,
                "strike_price": 40,
                "ticker": "O:NFLX260402C00040000",
                "underlying_ticker": "NFLX",
            }
        ],
    }
    detail_payload = {
        "status": "OK",
        "request_id": "cm_cd",
        "results": {
            "cfi": "OCASPS",
            "contract_type": "call",
            "strike_price": 75,
            "ticker": "O:NFLX260402C00075000",
            "underlying_ticker": "NFLX",
        },
    }
    client = make_client(
        {
            "/v1/options/contracts/": list_payload,
            "/v1/options/contracts/O:NFLX260402C00075000/": detail_payload,
        }
    )
    page = client.options.contracts.list(
        underlying_ticker="NFLX",
        expiration_date_gte="2026-04-01",
        limit=10,
    )
    assert page.results[0].strike_price == 40
    params = dict(recorder.last.url.params)
    assert params["expiration_date.gte"] == "2026-04-01"
    assert params["underlying_ticker"] == "NFLX"

    detail = client.options.contracts.get(
        "O:NFLX260402C00075000", as_of=dt.date(2026, 1, 15)
    )
    assert detail.strike_price == 75
    params_detail = dict(recorder.last.url.params)
    assert params_detail["as_of"] == "2026-01-15"


def test_trades_list_and_last(make_client) -> None:
    list_payload = {
        "status": "OK",
        "request_id": "cm_tl",
        "results": [
            {
                "conditions": [209],
                "exchange": 313,
                "id": "",
                "price": 20.7,
                "sequence_number": 2634406060,
                "sip_timestamp": 1775071411326665293,
                "size": 5,
                "decimal_size": "5.0",
            }
        ],
    }
    last_payload = {
        "status": "OK",
        "request_id": "cm_last",
        "results": {
            "T": "O:NFLX260410C00060000",
            "c": [233],
            "ds": "10.0",
            "p": 35.14,
            "q": 2765195189,
            "s": 10,
            "t": 1775072777652877667,
            "x": 302,
        },
    }
    client = make_client(
        {
            "/v1/options/trades/O:NFLX260402C00075000/": list_payload,
            "/v1/options/trades/O:NFLX260410C00060000/last/": last_payload,
        }
    )
    page = client.options.trades.list("O:NFLX260402C00075000", limit=10)
    assert page.results[0].price == 20.7
    assert page.results[0].decimal_size == "5.0"

    last = client.options.trades.last("O:NFLX260410C00060000")
    assert last.price == 35.14
    assert last.ticker == "O:NFLX260410C00060000"
    assert last.sip_timestamp == 1775072777652877667


def test_quotes_list(make_client) -> None:
    payload = {
        "status": "OK",
        "request_id": "cm_q",
        "results": [
            {
                "ask_exchange": 323,
                "ask_price": 0.28,
                "ask_size": 10,
                "bid_exchange": 316,
                "bid_price": 0.25,
                "bid_size": 1,
                "sequence_number": 789539218,
                "sip_timestamp": 1645119125346243600,
            }
        ],
    }
    client = make_client({"/v1/options/quotes/O:NFLX260402C00075000/": payload})
    page = client.options.quotes.list("O:NFLX260402C00075000")
    assert page.results[0].ask_price == 0.28
    assert page.results[0].bid_size == 1


def test_aggs_range(make_client, recorder) -> None:
    payload = {
        "ticker": "O:NFLX260402C00075000",
        "adjusted": True,
        "queryCount": 2,
        "resultsCount": 2,
        "count": 2,
        "status": "OK",
        "request_id": "cm_ag",
        "results": [
            {"c": 5.05, "h": 6.2, "l": 5, "n": 9, "o": 6.2, "t": 1770872400000, "v": 18, "vw": 5.2461},
            {"c": 5.45, "h": 5.54, "l": 5, "n": 33, "o": 5.5, "t": 1770958800000, "v": 642, "vw": 5.3322},
        ],
    }
    client = make_client(
        {
            "/v1/options/aggs/O:NFLX260402C00075000/1/day/2026-01-01/2026-04-01/": payload,
        }
    )
    page = client.options.aggs.range(
        "O:NFLX260402C00075000",
        1,
        "day",
        dt.date(2026, 1, 1),
        dt.date(2026, 4, 1),
        sort="desc",
        limit=10,
    )
    assert len(page) == 2
    assert page.results[0].close == 5.05
    assert page.results[0].trade_count == 9
    params = dict(recorder.last.url.params)
    assert params["sort"] == "desc"
    assert params["limit"] == "10"


def test_aggs_previous(make_client) -> None:
    payload = {
        "adjusted": True,
        "count": 1,
        "queryCount": 1,
        "resultsCount": 1,
        "status": "OK",
        "request_id": "cm_prev",
        "ticker": "O:NFLX260402C00075000",
        "results": [
            {
                "T": "O:NFLX260402C00075000",
                "c": 22.7,
                "h": 22.7,
                "l": 22.07,
                "n": 4,
                "o": 22.07,
                "t": 1775160000000,
                "v": 4,
                "vw": 22.42,
            }
        ],
    }
    client = make_client(
        {"/v1/options/aggs/O:NFLX260402C00075000/prev/": payload}
    )
    bar = client.options.aggs.previous("O:NFLX260402C00075000")
    assert bar.ticker == "O:NFLX260402C00075000"
    assert bar.close == 22.7
    assert bar.vwap == 22.42


def test_aggs_open_close_flat_payload(make_client) -> None:
    payload = {
        "afterHours": 21.98,
        "close": 21.98,
        "from": "2026-03-10",
        "high": 21.98,
        "low": 21.98,
        "open": 21.98,
        "preMarket": 21.98,
        "status": "OK",
        "symbol": "O:NFLX260402C00075000",
        "volume": 2,
        "request_id": "cm_oc",
    }
    client = make_client(
        {"/v1/options/open-close/O:NFLX260402C00075000/2026-03-10/": payload}
    )
    oc = client.options.aggs.open_close(
        "O:NFLX260402C00075000", dt.date(2026, 3, 10)
    )
    assert oc.symbol == "O:NFLX260402C00075000"
    assert oc.from_date == "2026-03-10"
    assert oc.pre_market == 21.98
    assert oc.after_hours == 21.98
    assert oc.raw == payload


def test_open_close_also_accessible_via_options(make_client) -> None:
    payload = {
        "status": "OK",
        "request_id": "cm_oc2",
        "symbol": "O:NFLX260402C00075000",
        "from": "2026-03-10",
        "close": 21.98,
    }
    client = make_client(
        {"/v1/options/open-close/O:NFLX260402C00075000/2026-03-10/": payload}
    )
    oc = client.options.open_close(
        "O:NFLX260402C00075000", dt.date(2026, 3, 10)
    )
    assert oc.close == 21.98
    assert oc.from_date == "2026-03-10"


def test_indicators_sma(make_client, recorder) -> None:
    payload = {
        "status": "OK",
        "request_id": "cm_sma",
        "results": {
            "values": [
                {"timestamp": 1775016000000, "value": 19.8},
                {"timestamp": 1774929600000, "value": 20.02},
            ]
        },
    }
    client = make_client(
        {"/v1/options/indicators/sma/O:NFLX260402C00075000/": payload}
    )
    result = client.options.indicators.sma(
        "O:NFLX260402C00075000", timespan="day", window=20, limit=10
    )
    assert len(result.values) == 2
    assert result.values[0].value == 19.8
    assert result.values[0].timestamp == 1775016000000
    params = dict(recorder.last.url.params)
    assert params["timespan"] == "day"
    assert params["window"] == "20"
    assert params["limit"] == "10"


def test_indicators_macd_has_signal_and_histogram(make_client) -> None:
    payload = {
        "status": "OK",
        "request_id": "cm_macd",
        "results": {
            "values": [
                {
                    "timestamp": 1775102400000,
                    "value": 1.579,
                    "signal": 1.743,
                    "histogram": -0.164,
                }
            ]
        },
    }
    client = make_client(
        {"/v1/options/indicators/macd/O:NFLX260402C00075000/": payload}
    )
    result = client.options.indicators.macd(
        "O:NFLX260402C00075000",
        timespan="day",
        short_window=12,
        long_window=26,
        signal_window=9,
    )
    v = result.values[0]
    assert v.value == 1.579
    assert v.signal == 1.743
    assert v.histogram == -0.164


def test_indicators_rsi_and_ema(make_client) -> None:
    sma_like = {
        "status": "OK",
        "request_id": "cm_x",
        "results": {"values": [{"timestamp": 1, "value": 50.0}]},
    }
    client = make_client(
        {
            "/v1/options/indicators/rsi/O:X/": sma_like,
            "/v1/options/indicators/ema/O:X/": sma_like,
        }
    )
    rsi = client.options.indicators.rsi("O:X", window=14)
    ema = client.options.indicators.ema("O:X", window=20)
    assert rsi.values[0].value == 50.0
    assert ema.values[0].value == 50.0
