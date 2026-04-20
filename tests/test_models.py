"""Model-specific behaviour: ``.raw`` preservation, shorthand property aliases."""

from __future__ import annotations

from cutemarkets.models import Aggregate, LastTrade, OpenClose


def test_last_trade_aliases_match_abbreviated_keys() -> None:
    payload = {
        "T": "O:NFLX260410C00060000",
        "c": [233],
        "ds": "10.0",
        "i": "",
        "p": 35.14,
        "q": 2765195189,
        "s": 10,
        "t": 1775072777652877667,
        "x": 302,
        "extra_field_from_api": "hello",
    }
    lt = LastTrade.model_validate(payload)

    assert lt.T == "O:NFLX260410C00060000"
    assert lt.ticker == "O:NFLX260410C00060000"
    assert lt.price == 35.14
    assert lt.size == 10.0
    assert lt.sip_timestamp == 1775072777652877667
    assert lt.exchange == 302
    assert lt.conditions == [233]
    assert lt.sequence_number == 2765195189
    assert lt.decimal_size == "10.0"

    assert lt.raw == payload
    assert lt.raw["extra_field_from_api"] == "hello"


def test_aggregate_property_aliases() -> None:
    payload = {
        "o": 6.2,
        "h": 6.2,
        "l": 5.0,
        "c": 5.05,
        "v": 18,
        "vw": 5.2461,
        "t": 1770872400000,
        "n": 9,
    }
    bar = Aggregate.model_validate(payload)
    assert bar.open == 6.2
    assert bar.high == 6.2
    assert bar.low == 5.0
    assert bar.close == 5.05
    assert bar.volume == 18.0
    assert bar.vwap == 5.2461
    assert bar.timestamp == 1770872400000
    assert bar.trade_count == 9
    assert bar.raw == payload


def test_open_close_flat_envelope_with_from_alias() -> None:
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
        "request_id": "cm_a1b2",
    }
    oc = OpenClose.model_validate(payload)
    assert oc.symbol == "O:NFLX260402C00075000"
    assert oc.from_date == "2026-03-10"
    assert oc.pre_market == 21.98
    assert oc.after_hours == 21.98
    assert oc.status == "OK"
    assert oc.request_id == "cm_a1b2"
    assert oc.raw == payload
