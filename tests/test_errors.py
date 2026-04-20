"""Error-hierarchy mapping and end-to-end error surfacing."""

from __future__ import annotations

import pytest

from cutemarkets.errors import (
    APIError,
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    InvalidPageTokenError,
    LookbackExceededError,
    NotFoundError,
    RateLimitError,
    error_from_response,
)


@pytest.mark.parametrize(
    "status, code, expected",
    [
        (400, "bad_request", BadRequestError),
        (400, "invalid_page_token", InvalidPageTokenError),
        (401, "unauthorized", AuthenticationError),
        (403, "forbidden", ForbiddenError),
        (403, "lookback_exceeded", LookbackExceededError),
        (404, "not_found", NotFoundError),
        (429, "rate_limit_exceeded", RateLimitError),
        (500, None, APIError),
    ],
)
def test_error_mapping(status: int, code: str | None, expected: type) -> None:
    payload = {
        "status": "ERROR",
        "request_id": "cm_err",
        "error": {"code": code, "message": "bad"},
    }
    exc = error_from_response(status, payload)
    assert isinstance(exc, expected)
    assert exc.status_code == status
    assert exc.code == code
    assert exc.request_id == "cm_err"


def test_error_message_without_body() -> None:
    exc = error_from_response(500, None)
    assert isinstance(exc, APIError)
    assert "HTTP 500" in str(exc)


def test_api_error_surface_through_client(make_client) -> None:
    client = make_client(
        {
            "/v1/options/quotes/O:TEST/": (
                403,
                {
                    "status": "ERROR",
                    "request_id": "cm_403",
                    "error": {
                        "code": "forbidden",
                        "message": "This endpoint requires a Expert Plan subscription.",
                    },
                },
            )
        }
    )
    with pytest.raises(ForbiddenError) as exc_info:
        client.options.quotes.list("O:TEST")
    err = exc_info.value
    assert err.status_code == 403
    assert err.code == "forbidden"
    assert err.request_id == "cm_403"
    assert "Expert Plan" in err.message


def test_lookback_exceeded_is_selected_over_generic_forbidden(make_client) -> None:
    client = make_client(
        {
            "/v1/options/contracts/": (
                403,
                {
                    "status": "ERROR",
                    "request_id": "cm_lb",
                    "error": {
                        "code": "lookback_exceeded",
                        "message": "Your Free plan allows up to 3 years of historical lookback.",
                    },
                },
            )
        }
    )
    with pytest.raises(LookbackExceededError):
        client.options.contracts.list(underlying_ticker="SPY", as_of="2020-01-01")
