"""CuteMarkets Python client.

Public entry points:

* :class:`CuteMarkets` — synchronous client.
* :class:`AsyncCuteMarkets` — asynchronous client.

Response types (typed :mod:`pydantic` models) and exceptions live under
:mod:`cutemarkets.models` and :mod:`cutemarkets.errors` respectively.
"""

from ._pagination import AsyncPage, Page, aiter_pages, iter_pages
from ._version import __version__
from .async_client import AsyncCuteMarkets
from .client import CuteMarkets
from .errors import (
    APIError,
    AuthenticationError,
    BadRequestError,
    ConfigurationError,
    CuteMarketsError,
    ForbiddenError,
    InvalidPageTokenError,
    LookbackExceededError,
    NotFoundError,
    RateLimitError,
    TransportError,
)
from .models import (
    Aggregate,
    Contract,
    ContractDetails,
    ContractSnapshot,
    CuteBase,
    DayBar,
    EmbeddedLastTrade,
    ExpirationsResponse,
    Greeks,
    IndicatorResult,
    IndicatorUnderlying,
    IndicatorValue,
    LastQuote,
    LastTrade,
    MacdResult,
    MacdValue,
    OpenClose,
    Quote,
    RateLimitInfo,
    ServiceStatus,
    SystemStatus,
    TickerSearchResult,
    Trade,
    UnderlyingAsset,
)

__all__ = [
    "__version__",
    "CuteMarkets",
    "AsyncCuteMarkets",
    "Page",
    "AsyncPage",
    "iter_pages",
    "aiter_pages",
    "CuteMarketsError",
    "ConfigurationError",
    "TransportError",
    "APIError",
    "BadRequestError",
    "InvalidPageTokenError",
    "AuthenticationError",
    "ForbiddenError",
    "LookbackExceededError",
    "NotFoundError",
    "RateLimitError",
    "CuteBase",
    "RateLimitInfo",
    "ServiceStatus",
    "SystemStatus",
    "Aggregate",
    "Contract",
    "ContractDetails",
    "ContractSnapshot",
    "DayBar",
    "EmbeddedLastTrade",
    "Greeks",
    "LastQuote",
    "LastTrade",
    "OpenClose",
    "Quote",
    "Trade",
    "UnderlyingAsset",
    "IndicatorResult",
    "IndicatorUnderlying",
    "IndicatorValue",
    "MacdResult",
    "MacdValue",
    "ExpirationsResponse",
    "TickerSearchResult",
]
