"""Unit tests for query-parameter coercion and URL building."""

from __future__ import annotations

import datetime as dt
from enum import Enum

import pytest

from cutemarkets._transport import (
    _rewrite_range_key,
    build_url,
    resolve_api_key,
    serialize_params,
)


class ContractType(str, Enum):
    CALL = "call"
    PUT = "put"


@pytest.mark.parametrize(
    "given, expected",
    [
        ("strike_price_gte", "strike_price.gte"),
        ("strike_price_gt", "strike_price.gt"),
        ("strike_price_lte", "strike_price.lte"),
        ("strike_price_lt", "strike_price.lt"),
        ("expiration_date_gte", "expiration_date.gte"),
        ("timestamp_lt", "timestamp.lt"),
        ("underlying_ticker_gte", "underlying_ticker.gte"),
        ("underlying_ticker", "underlying_ticker"),
        ("strike_price", "strike_price"),
        ("limit", "limit"),
    ],
)
def test_rewrite_range_key(given: str, expected: str) -> None:
    assert _rewrite_range_key(given) == expected


def test_serialize_params_drops_none() -> None:
    assert serialize_params({"a": 1, "b": None, "c": "x"}) == [("a", "1"), ("c", "x")]


def test_serialize_params_coerces_types() -> None:
    params = serialize_params(
        {
            "adjusted": True,
            "expired": False,
            "as_of": dt.date(2026, 1, 15),
            "ts": dt.datetime(2026, 1, 15, 9, 30, 0),
            "contract_type": ContractType.CALL,
            "limit": 10,
            "vol": 1.5,
        }
    )
    d = dict(params)
    assert d["adjusted"] == "true"
    assert d["expired"] == "false"
    assert d["as_of"] == "2026-01-15"
    assert d["ts"] == "2026-01-15"
    assert d["contract_type"] == "call"
    assert d["limit"] == "10"
    assert d["vol"] == "1.5"


def test_serialize_params_range_rewrites() -> None:
    params = dict(
        serialize_params(
            {
                "strike_price_gte": 90,
                "strike_price_lte": 110,
                "expiration_date_gt": dt.date(2026, 1, 1),
            }
        )
    )
    assert params == {
        "strike_price.gte": "90",
        "strike_price.lte": "110",
        "expiration_date.gt": "2026-01-01",
    }


def test_serialize_params_list_value() -> None:
    params = serialize_params({"conditions": [1, 2, 3]})
    assert params == [("conditions", "1"), ("conditions", "2"), ("conditions", "3")]


def test_build_url_joins_base_and_path() -> None:
    assert build_url("https://api.cutemarkets.com", "/v1/status/") == (
        "https://api.cutemarkets.com/v1/status/"
    )
    assert build_url("https://api.cutemarkets.com/", "v1/status/") == (
        "https://api.cutemarkets.com/v1/status/"
    )


def test_resolve_api_key_prefers_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CUTEMARKETS_API_KEY", "cm_env")
    assert resolve_api_key("cm_explicit") == "cm_explicit"


def test_resolve_api_key_falls_back_to_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CUTEMARKETS_API_KEY", "cm_env")
    assert resolve_api_key(None) == "cm_env"


def test_resolve_api_key_returns_none_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CUTEMARKETS_API_KEY", raising=False)
    assert resolve_api_key(None) is None
