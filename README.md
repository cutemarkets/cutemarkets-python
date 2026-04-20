# cutemarkets

The official Python client for the [CuteMarkets](https://cutemarkets.com) options market-data API.

`cutemarkets` wraps every documented endpoint of the [CuteMarkets v1 REST API](https://cutemarkets.com/docs) in a namespaced, typed, Pythonic interface. Sync and async clients share the same method surface, response models are `pydantic` v2 classes that preserve the raw payload on `.raw`, every list endpoint ships with both one-page and auto-paginating variants, and every error path maps to a specific exception class so you can handle plan gating, rate limiting, and missing resources cleanly.

---

## Table of contents

1. [Features](#features)
2. [Installation](#installation)
3. [Quick start](#quick-start)
4. [Authentication](#authentication)
5. [Client options](#client-options)
6. [Resource reference](#resource-reference)
7. [Models](#models)
8. [Pagination](#pagination)
9. [Filters and range queries](#filters-and-range-queries)
10. [Dates, enums, booleans](#dates-enums-booleans)
11. [Errors](#errors)
12. [Rate limits](#rate-limits)
13. [Async usage](#async-usage)
14. [Recipes](#recipes)
15. [Testing your integration](#testing-your-integration)
16. [Versioning and compatibility](#versioning-and-compatibility)
17. [Development](#development)
18. [License](#license)

---

## Features

- Sync (`CuteMarkets`) and async (`AsyncCuteMarkets`) clients with identical surfaces.
- Namespaced methods that mirror the docs: `client.options.chain(...)`, `client.options.aggs.range(...)`, `client.options.indicators.sma(...)`, `client.tickers.search(...)`, ...
- Typed `pydantic` v2 models for every response, with `.raw` preserving the original JSON so new server fields never block you.
- Short-name preservation on abbreviated wire payloads (`LastTrade.T/p/s/...`, `Aggregate.o/h/l/c/v/vw/t/n`) plus readable property aliases (`.ticker`, `.price`, `.open`, `.close`, ...).
- One-shot `list(...)` returns a `Page[T]` (`results`, `next_url`, `request_id`, `rate_limit`, `.next()`). Auto-paginating `iter_list(...)` / `iter_*(...)` generators walk every page for you.
- Automatic date / datetime / bool / Enum coercion and underscore-to-dot rewriting for range filters (`strike_price_gte=100` → `strike_price.gte=100`).
- Typed exception hierarchy (`AuthenticationError`, `ForbiddenError`, `LookbackExceededError`, `NotFoundError`, `RateLimitError`, ...) selected from the `error.code` envelope field.
- Rate-limit header introspection via `page.rate_limit` and `client.last_rate_limit` (coming soon).
- Opt-in exponential-backoff retries on 429, 5xx, and transient network errors.
- Custom `httpx.Client` / `httpx.AsyncClient` / `httpx.BaseTransport` injection for testing.

---

## Installation

```bash
pip install cutemarkets
```

Requires Python 3.9 or newer. The only runtime dependencies are [`httpx`](https://www.python-httpx.org/) and [`pydantic`](https://docs.pydantic.dev/).

Development extras:

```bash
pip install "cutemarkets[dev]"
```

---

## Quick start

```python
from cutemarkets import CuteMarkets

client = CuteMarkets(api_key="cm_...")

chain = client.options.chain("NFLX", limit=5)
for contract in chain:
    print(contract.details.ticker, contract.break_even_price, contract.greeks.delta if contract.greeks else None)

print("request id:", chain.request_id)
print("remaining this minute:", chain.rate_limit.remaining_minute)
```

Async equivalent:

```python
import asyncio
from cutemarkets import AsyncCuteMarkets

async def main():
    async with AsyncCuteMarkets(api_key="cm_...") as client:
        chain = await client.options.chain("NFLX", limit=5)
        for contract in chain:
            print(contract.details.ticker)

asyncio.run(main())
```

---

## Authentication

API keys are prefixed `cm_...` and are passed as a Bearer token on the `Authorization` header.

Three ways to provide your key, evaluated in this order:

1. Constructor argument:
   ```python
   client = CuteMarkets(api_key="cm_...")
   ```
2. `CUTEMARKETS_API_KEY` environment variable:
   ```bash
   export CUTEMARKETS_API_KEY=cm_xxxxxxxxxxxxxxxx
   ```
   ```python
   client = CuteMarkets()  # auto-picks up the env var
   ```
3. Runtime setter:
   ```python
   client.set_api_key("cm_...")
   ```

Get a free key at [cutemarkets.com/signup](https://cutemarkets.com/signup). Every request's `request_id` is echoed back in responses and errors, so include it in support conversations.

### Unauthenticated endpoint

`client.status()` hits `/v1/status/` and does **not** require an API key. It works even before you configure credentials, so it's handy for readiness probes.

---

## Client options

```python
CuteMarkets(
    api_key: str | None = None,
    *,
    base_url: str = "https://api.cutemarkets.com",
    timeout: float = 30.0,
    max_retries: int = 2,
    headers: dict[str, str] | None = None,
    transport: httpx.BaseTransport | None = None,
    http_client: httpx.Client | None = None,
)
```

| Argument | Purpose |
| --- | --- |
| `api_key` | Override or supply the API key. Overrides `CUTEMARKETS_API_KEY`. |
| `base_url` | Point the client at a different host (e.g. a staging or proxy URL). |
| `timeout` | Per-request timeout in seconds (applies to connect + read). |
| `max_retries` | Retry attempts on 429, 5xx, and transient network errors. `0` disables retries. |
| `headers` | Extra headers merged onto every request (useful for tracing or proxy auth). |
| `transport` | Pass an `httpx.MockTransport` (or any `httpx.BaseTransport`) for tests. |
| `http_client` | Bring your own `httpx.Client` when you want custom transport, event hooks, or connection pooling. |

`AsyncCuteMarkets` accepts the same kwargs, with `transport: httpx.AsyncBaseTransport` and `http_client: httpx.AsyncClient`.

Both classes support the context-manager protocol:

```python
with CuteMarkets(api_key="cm_...") as client:
    ...

async with AsyncCuteMarkets(api_key="cm_...") as client:
    ...
```

---

## Resource reference

Every method below links to the matching page under [`docs/`](docs/). Every response is a `pydantic` model — dotted attribute access, `.model_dump()` for a dict, `.raw` for the untouched payload.

### `client.status()`

Poll the public health endpoint. No API key required.

```python
status = client.status()
status.status            # "ok" or "degraded"
status.is_ok             # bool
status.services["api"].status
status.services["database"].latency_ms
```

### `client.tickers.search(query=..., limit=...)`

[docs/ticker-search.md](docs/ticker-search.md)

```python
for row in client.tickers.search(query="NFLX", limit=8):
    print(row.symbol, row.name)
```

### `client.tickers.expirations(ticker)`

[docs/expirations.md](docs/expirations.md)

```python
exp = client.tickers.expirations("NFLX")
exp.results  # ["2026-04-02", "2026-04-10", ...]
```

### `client.options.chain(ticker, **filters)`

[docs/option-chain.md](docs/option-chain.md)

Returns a `Page[ContractSnapshot]`. Accepts `strike_price`, `expiration_date`, `contract_type`, the range filters (`strike_price_gte`, `expiration_date_lt`, ...), `sort`, `order`, `limit`, and `page`.

```python
chain = client.options.chain(
    "NFLX",
    contract_type="call",
    strike_price_gte=90,
    strike_price_lte=110,
    sort="strike_price",
    order="asc",
    limit=50,
)
for c in chain:
    print(c.details.ticker, c.break_even_price, c.implied_volatility)
```

`client.options.iter_chain("NFLX", ...)` auto-follows `next_url`.

### `client.options.snapshot(underlying, option_contract)`

[docs/option-contract-snapshot.md](docs/option-contract-snapshot.md)

```python
snap = client.options.snapshot("NFLX", "O:NFLX260410C00060000")
snap.greeks.delta
snap.underlying_asset.price
```

### `client.options.contracts.list(**filters)` / `.get(options_ticker, as_of=None)` / `.iter_list(**filters)`

[docs/contracts.md](docs/contracts.md)

```python
# Paged list
page = client.options.contracts.list(
    underlying_ticker="NFLX",
    expiration_date_gte="2026-04-01",
    limit=1000,
)

# Walk every contract across pages
for c in client.options.contracts.iter_list(underlying_ticker="NFLX"):
    print(c.ticker)

# Detail for one contract, optionally as-of a historical date
from datetime import date
detail = client.options.contracts.get("O:NFLX260402C00075000", as_of=date(2026, 1, 15))
```

### `client.options.trades.list(ticker, **filters)` / `.last(ticker)` / `.iter_list(...)`

[docs/trades.md](docs/trades.md)

```python
# Historical trades
page = client.options.trades.list(
    "O:NFLX260402C00075000",
    timestamp_gte="2026-03-01",
    timestamp_lte="2026-03-31",
    sort="timestamp",
    order="desc",
    limit=1000,
)

# Compact "last trade" shape (abbreviated keys + readable aliases)
last = client.options.trades.last("O:NFLX260410C00060000")
last.price       # property alias for last.p
last.size        # property alias for last.s
last.ticker      # property alias for last.T
last.raw         # the untouched {"T": ..., "p": ..., "s": ..., ...}
```

### `client.options.quotes.list(ticker, **filters)` / `.iter_list(...)` — Expert Plan only

[docs/quotes.md](docs/quotes.md)

Non-Expert keys receive HTTP 403, surfaced as `ForbiddenError`:

```python
from cutemarkets.errors import ForbiddenError

try:
    quotes = client.options.quotes.list("O:NFLX260402C00075000", limit=500)
except ForbiddenError as exc:
    print("upgrade required:", exc.message)
```

### `client.options.aggs.range(ticker, multiplier, timespan, from_date, to_date, **opts)`

[docs/aggregates.md](docs/aggregates.md)

```python
from datetime import date
page = client.options.aggs.range(
    "O:NFLX260402C00075000",
    multiplier=1,
    timespan="day",
    from_date=date(2026, 1, 1),
    to_date=date(2026, 4, 1),
    adjusted=True,
    sort="desc",
    limit=1000,
)
for bar in page:
    print(bar.timestamp, bar.open, bar.high, bar.low, bar.close, bar.volume)
```

`client.options.aggs.iter_range(...)` auto-follows `next_url`.

### `client.options.aggs.previous(ticker, adjusted=None)`

```python
prev = client.options.aggs.previous("O:NFLX260402C00075000")
print(prev.close, prev.vwap, prev.trade_count)
```

### `client.options.aggs.open_close(ticker, date, adjusted=None)` / `client.options.open_close(...)`

Note: grouped under `aggs` for discoverability, but the underlying route is `/v1/options/open-close/...`. The payload is **flat** (no `results` envelope).

```python
from datetime import date
oc = client.options.aggs.open_close("O:NFLX260402C00075000", date(2026, 3, 10))
oc.open, oc.close, oc.high, oc.low, oc.volume
oc.pre_market            # property alias for oc.preMarket
oc.after_hours           # property alias for oc.afterHours
oc.from_date             # property alias for the reserved-keyword "from"
```

### `client.options.indicators.sma(ticker, ...)` / `.ema(...)` / `.macd(...)` / `.rsi(...)`

[docs/indicators-sma.md](docs/indicators-sma.md), [docs/indicators-ema.md](docs/indicators-ema.md), [docs/indicators-macd.md](docs/indicators-macd.md), [docs/indicators-rsi.md](docs/indicators-rsi.md)

```python
sma = client.options.indicators.sma(
    "O:NFLX260402C00075000",
    timespan="day",
    window=20,
    series_type="close",
    limit=100,
)
for point in sma.values:
    print(point.timestamp, point.value)

macd = client.options.indicators.macd(
    "O:NFLX260402C00075000",
    timespan="day",
    short_window=12,
    long_window=26,
    signal_window=9,
)
for point in macd.values:
    print(point.timestamp, point.value, point.signal, point.histogram)
```

Pass `expand_underlying=True` to populate `result.underlying` with the aggregate bars used in the calculation, plus an absolute URL to the same contract's aggregates range.

---

## Models

Every response model:

- Inherits from `cutemarkets.CuteBase` (a `pydantic.BaseModel` with `extra="allow"`).
- Preserves the untouched JSON payload on `.raw`, so new or undocumented fields are always reachable:
  ```python
  lt = client.options.trades.last("O:NFLX260410C00060000")
  lt.raw["future_field_we_didnt_know_about"]
  ```
- Supports `.model_dump(by_alias=True)` / `.model_dump_json()` for round-tripping.
- Keeps abbreviated wire keys as the primary field names (matching the docs) and exposes readable property aliases:
  - `LastTrade`: `T/p/s/t/x/c/y/f/r/i/q/e/z/ds` → `ticker/price/size/sip_timestamp/exchange/conditions/participant_timestamp/trf_timestamp/trf_id/trade_id/sequence_number/correction/tape/decimal_size`.
  - `Aggregate`: `o/h/l/c/v/vw/t/n` → `open/high/low/close/volume/vwap/timestamp/trade_count`.
- `OpenClose` is a flat envelope (no `results` key): the top-level payload *is* the model. `from` is mapped to `from_date` because `from` is a Python keyword.

---

## Pagination

`Page[T]` holds one server page plus the metadata needed to fetch more:

```python
page = client.options.contracts.list(underlying_ticker="NFLX", limit=1000)

page.results       # list[Contract]
page.next_url      # full URL for the next page, or None
page.request_id    # server-assigned request id
page.rate_limit    # RateLimitInfo parsed from headers
page.has_next      # bool
next_page = page.next()   # refetches next_url verbatim with the same Authorization

# Walk every item across every page:
for contract in page.iter_all():
    ...
```

Every list endpoint also ships an `iter_<name>(...)` generator that does the pagination for you from the first request:

```python
for contract in client.options.contracts.iter_list(underlying_ticker="NFLX"):
    ...
```

The client follows `next_url` verbatim, with the same `Authorization` header. Don't reconstruct the URL yourself.

---

## Filters and range queries

Range filters in the CuteMarkets API use a `<field>.<op>` naming convention (`strike_price.gte=100`). Python doesn't allow dots in keyword arguments, so this client accepts an underscore spelling and rewrites it server-side:

| You write | Sent on the wire |
| --- | --- |
| `strike_price_gte=100` | `strike_price.gte=100` |
| `strike_price_lt=500` | `strike_price.lt=500` |
| `expiration_date_gte="2026-04-01"` | `expiration_date.gte=2026-04-01` |
| `timestamp_lte=1770872400000` | `timestamp.lte=1770872400000` |

You can combine them freely:

```python
client.options.chain(
    "NFLX",
    contract_type="call",
    strike_price_gte=90,
    strike_price_lte=110,
    expiration_date_gte="2026-04-01",
    expiration_date_lt="2026-07-01",
    sort="strike_price",
    order="asc",
    limit=100,
)
```

Any kwarg whose name does **not** end in `_gte` / `_gt` / `_lte` / `_lt` is passed through verbatim. That way future API filters work without a client upgrade.

---

## Dates, enums, booleans

Values are auto-coerced to what the API expects:

| Python value | Wire form |
| --- | --- |
| `datetime.date(2026, 1, 15)` | `"2026-01-15"` |
| `datetime.datetime(2026, 1, 15, 9, 30)` | `"2026-01-15"` |
| `True` / `False` | `"true"` / `"false"` |
| `MyEnum.VALUE` (subclass of `enum.Enum`) | `.value` then coerced |
| `list[int]` / `tuple[str, ...]` | emitted as repeated `key=value&key=value` |
| `None` | dropped — useful for defaulting to server behavior |

Millisecond / nanosecond timestamps should be passed as `int` (or a decimal string); the client does not guess the unit. Timestamp filters (`timestamp`, `timestamp_gte`, ...) accept either a date or an int/string Unix timestamp depending on the endpoint — see the doc page linked in each resource section.

---

## Errors

All exceptions inherit from `cutemarkets.CuteMarketsError`.

```
CuteMarketsError
├── ConfigurationError        # missing API key, bad settings
├── TransportError            # network / timeout / connection error
└── APIError                  # any non-2xx response from the API
    ├── BadRequestError       # 400 bad_request
    │   └── InvalidPageTokenError
    ├── AuthenticationError   # 401 unauthorized
    ├── ForbiddenError        # 403 forbidden
    │   └── LookbackExceededError
    ├── NotFoundError         # 404 not_found
    └── RateLimitError        # 429 rate_limit_exceeded
```

The specific subclass is chosen by HTTP status and the `error.code` field from the response envelope:

| HTTP | `error.code` | Exception |
| --- | --- | --- |
| 400 | `bad_request` | `BadRequestError` |
| 400 | `invalid_page_token` | `InvalidPageTokenError` |
| 401 | `unauthorized` | `AuthenticationError` |
| 403 | `forbidden` | `ForbiddenError` |
| 403 | `lookback_exceeded` | `LookbackExceededError` |
| 404 | `not_found` | `NotFoundError` |
| 429 | `rate_limit_exceeded` | `RateLimitError` |

Every `APIError` exposes:

- `status_code` (HTTP status)
- `code` (machine-readable code from the envelope)
- `message` (human-readable message)
- `request_id` (for support)
- `response` (the decoded JSON body, for diagnostics)
- `rate_limit` (`RateLimitInfo` parsed from headers)

```python
from cutemarkets.errors import LookbackExceededError, RateLimitError, ForbiddenError

try:
    client.options.contracts.list(underlying_ticker="SPY", as_of="2015-01-01")
except LookbackExceededError as exc:
    print(f"{exc.code}: {exc.message} (request_id={exc.request_id})")

try:
    client.options.quotes.list("O:SPY260402C00500000")
except ForbiddenError as exc:
    print(f"Upgrade required: {exc.message}")
```

---

## Rate limits

Free keys are capped at 10 requests/minute; Developer and Expert plans are unlimited. Each response includes rate-limit headers that this client parses into a `RateLimitInfo` object:

```python
page = client.options.chain("NFLX", limit=5)
page.rate_limit.plan                # "Free" | "Developer" | "Expert"
page.rate_limit.limit_minute        # "10" or "unlimited"
page.rate_limit.remaining_minute    # int
page.rate_limit.limit_day
page.rate_limit.remaining_day
```

The same object is attached to `APIError.rate_limit` on failures, so you can inspect remaining quota after a 429.

When `max_retries` is non-zero the client retries 429 responses (as well as 5xx and transient network errors) with exponential backoff — but note that retries share the same plan quota, so aggressive retries on Free keys can compound 429s. For Free keys you usually want `max_retries=0` and your own backoff.

---

## Async usage

`AsyncCuteMarkets` mirrors the sync surface; methods that perform I/O are `async def` and iterators are async:

```python
import asyncio
from cutemarkets import AsyncCuteMarkets

async def main():
    async with AsyncCuteMarkets(api_key="cm_...") as client:
        status = await client.status()
        chain = await client.options.chain("NFLX", limit=5)
        async for contract in client.options.iter_chain("NFLX", limit=5):
            print(contract.details.ticker)

        last = await client.options.trades.last("O:NFLX260410C00060000")
        print(last.price)

asyncio.run(main())
```

Async pagination:

```python
page = await client.options.contracts.list(underlying_ticker="NFLX", limit=1000)
async for contract in page.iter_all():
    ...
```

Don't share a single `AsyncCuteMarkets` across event loops.

---

## Recipes

### Fetch the full option chain across pages

```python
calls = []
for contract in client.options.iter_chain("NFLX", contract_type="call", limit=100):
    calls.append(contract)
```

### Build a daily OHLC series and compare to the previous day

```python
from datetime import date, timedelta

ticker = "O:NFLX260402C00075000"
today = date.today()

bars = list(
    client.options.aggs.iter_range(
        ticker, 1, "day", today - timedelta(days=365), today, sort="asc"
    )
)
prev = client.options.aggs.previous(ticker)
print(f"last daily close: {bars[-1].close}, previous session close: {prev.close}")
```

### Pull the last trade for every contract in a chain

```python
for contract in client.options.iter_chain("NFLX", contract_type="call", limit=100):
    last = client.options.trades.last(contract.details.ticker)
    print(contract.details.strike_price, last.price)
```

### Stream tick-level trades for a day

```python
for trade in client.options.trades.iter_list(
    "O:NFLX260402C00075000",
    timestamp_gte="2026-03-10",
    timestamp_lt="2026-03-11",
    sort="timestamp",
    order="asc",
    limit=10000,
):
    ...
```

### Detect an SMA/EMA crossover

```python
sma = client.options.indicators.sma(ticker, timespan="day", window=50, limit=200)
ema = client.options.indicators.ema(ticker, timespan="day", window=20, limit=200)

sma_by_ts = {p.timestamp: p.value for p in sma.values}
for p in ema.values:
    s = sma_by_ts.get(p.timestamp)
    if s is not None and p.value is not None:
        print(p.timestamp, "above" if p.value > s else "below")
```

### Resolve an expiration + strike to a contract ticker

```python
page = client.options.chain(
    "NFLX",
    expiration_date="2026-04-10",
    strike_price=60,
    contract_type="call",
    limit=1,
)
if page.results:
    print(page.results[0].details.ticker)
```

---

## Testing your integration

Every network call goes through `httpx`, so you can swap in an `httpx.MockTransport` for unit tests:

```python
import httpx
from cutemarkets import CuteMarkets

def handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/v1/status/":
        return httpx.Response(200, json={"status": "ok", "request_id": "cm_test", "services": {}})
    return httpx.Response(404, json={"status": "ERROR", "error": {"code": "not_found", "message": "x"}})

client = CuteMarkets(api_key="cm_test", transport=httpx.MockTransport(handler))
assert client.status().is_ok
```

The test suite in this repo uses the same pattern via a `make_client` fixture — see [`tests/conftest.py`](tests/conftest.py) for a worked example.

---

## Versioning and compatibility

- SemVer: minor versions may add new resources and fields; breaking changes bump the major.
- Supports Python 3.9, 3.10, 3.11, 3.12, 3.13.
- Requires `pydantic>=2.6` (pydantic v1 is not supported).
- Requires `httpx>=0.27`.

---

## Development

```bash
git clone https://github.com/cutemarkets/cutemarkets-python
cd cutemarkets-python
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

pytest
ruff check src tests
mypy src
```

### Running the live smoke test

```bash
cp .env.example .env
# fill in CUTEMARKETS_API_KEY=cm_...
python examples/smoke_test.py
```

The smoke test runs one minimal call against every resource group against `https://api.cutemarkets.com`, spaced out to stay within the Free plan's 10 req/min limit. It tolerates `ForbiddenError` on `quotes` (Expert Plan only) so Free / Developer keys can still use it.

---

## License

MIT - see [LICENSE](LICENSE).
