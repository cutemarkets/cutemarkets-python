"""End-to-end smoke test against the live CuteMarkets API.

Requires ``CUTEMARKETS_API_KEY=cm_...`` in ``.env`` (or the environment).

The test hits one minimal call against every endpoint group (keeping
``limit`` values small to stay Free-plan friendly), prints the HTTP status
and ``request_id`` for each call, and tolerates ``ForbiddenError`` on
``quotes`` because it requires an Expert Plan subscription.

It re-runs a subset of calls through :class:`AsyncCuteMarkets` to confirm
the async surface also works end-to-end.
"""

from __future__ import annotations

import asyncio
import os
import time
import traceback
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Callable, List, Optional, Tuple

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from cutemarkets import AsyncCuteMarkets, CuteMarkets
from cutemarkets.errors import (
    APIError,
    CuteMarketsError,
    ForbiddenError,
    LookbackExceededError,
    NotFoundError,
    RateLimitError,
)


PACE = 7.0  # seconds between Free-plan calls (10/min cap = 6s minimum)


@dataclass
class Result:
    name: str
    ok: bool
    note: str = ""


def _preview(value: Any) -> str:
    text = repr(value)
    return text if len(text) <= 140 else text[:140] + "..."


def _run(name: str, fn: Callable[[], Any], results: List[Result]) -> Any:
    print(f"\n-- {name} --")
    try:
        value = fn()
        ok_note = ""
        if hasattr(value, "request_id") and value.request_id:
            ok_note += f"request_id={value.request_id} "
        if hasattr(value, "rate_limit") and value.rate_limit and value.rate_limit.plan:
            ok_note += f"plan={value.rate_limit.plan} "
        preview_target = getattr(value, "results", value)
        if isinstance(preview_target, list) and preview_target:
            first = preview_target[0]
            first_preview = getattr(first, "raw", first)
            print(f"  OK {ok_note}first={_preview(first_preview)}")
        else:
            print(f"  OK {ok_note}{_preview(preview_target)}")
        results.append(Result(name, True, ok_note.strip()))
        return value
    except ForbiddenError as exc:
        if name == "quotes.list":
            print(f"  SKIP (expected 403): {exc.message}")
            results.append(Result(name, True, f"403 forbidden (plan-gated): {exc.code}"))
            return None
        print(f"  FAIL ForbiddenError: {exc}")
        results.append(Result(name, False, f"403 {exc.code}: {exc.message}"))
        return None
    except LookbackExceededError as exc:
        print(f"  SKIP (lookback): {exc.message}")
        results.append(Result(name, True, f"lookback_exceeded: {exc.message}"))
        return None
    except RateLimitError as exc:
        print(f"  FAIL 429 {exc.message}; sleeping 30s before continuing")
        results.append(Result(name, False, f"429 {exc.message}"))
        time.sleep(30)
        return None
    except APIError as exc:
        print(f"  FAIL APIError {exc}")
        results.append(Result(name, False, str(exc)))
        return None
    except CuteMarketsError as exc:
        print(f"  FAIL {type(exc).__name__}: {exc}")
        results.append(Result(name, False, str(exc)))
        return None
    except Exception as exc:  # noqa: BLE001 - surface anything unexpected
        print(f"  FAIL unexpected {type(exc).__name__}: {exc}")
        traceback.print_exc()
        results.append(Result(name, False, f"{type(exc).__name__}: {exc}"))
        return None


def _pick_sample_contract(chain_page: Any) -> Optional[str]:
    if not chain_page or not chain_page.results:
        return None
    for item in chain_page.results:
        details = getattr(item, "details", None)
        if details and details.ticker:
            return details.ticker
    return None


def _recent_weekday(today: date) -> date:
    """Return the most recent weekday strictly before ``today``."""
    day = today - timedelta(days=1)
    while day.weekday() >= 5:
        day -= timedelta(days=1)
    return day


def _pace() -> None:
    time.sleep(PACE)


def run_sync(api_key: str) -> Tuple[List[Result], Optional[str]]:
    results: List[Result] = []
    client = CuteMarkets(api_key=api_key, max_retries=0)

    _run("status", client.status, results)
    _pace()

    _run(
        "tickers.search",
        lambda: client.tickers.search(query="NFLX", limit=2),
        results,
    )
    _pace()

    _run(
        "tickers.expirations",
        lambda: client.tickers.expirations("NFLX"),
        results,
    )
    _pace()

    chain = _run(
        "options.chain",
        lambda: client.options.chain("NFLX", limit=2),
        results,
    )
    _pace()

    sample = _pick_sample_contract(chain)
    if sample is None:
        print("\nNo sample contract available on NFLX; skipping per-contract calls.")
        client.close()
        return results, None
    print(f"\nUsing sample contract: {sample}")

    _run(
        "options.snapshot",
        lambda: client.options.snapshot("NFLX", sample),
        results,
    )
    _pace()

    _run(
        "options.contracts.list",
        lambda: client.options.contracts.list(
            underlying_ticker="NFLX", limit=2
        ),
        results,
    )
    _pace()

    _run(
        "options.contracts.get",
        lambda: client.options.contracts.get(sample),
        results,
    )
    _pace()

    _run(
        "options.trades.list",
        lambda: client.options.trades.list(sample, limit=2),
        results,
    )
    _pace()

    _run(
        "options.trades.last",
        lambda: client.options.trades.last(sample),
        results,
    )
    _pace()

    _run(
        "quotes.list",
        lambda: client.options.quotes.list(sample, limit=2),
        results,
    )
    _pace()

    today = date.today()
    _run(
        "aggs.range",
        lambda: client.options.aggs.range(
            sample,
            1,
            "day",
            today - timedelta(days=90),
            today,
            limit=2,
        ),
        results,
    )
    _pace()

    _run(
        "aggs.previous",
        lambda: client.options.aggs.previous(sample),
        results,
    )
    _pace()

    # open-close data doesn't exist for every (contract, weekday) pair; walk
    # backwards a few recent weekdays before giving up, and treat a final
    # 404 as "endpoint works, no data" rather than a client bug.
    open_close_done = False
    target = _recent_weekday(today)
    for _ in range(5):
        try:
            value = client.options.aggs.open_close(sample, target)
            print(f"\n-- aggs.open_close ({target.isoformat()}) --")
            print(f"  OK close={value.close} open={value.open}")
            results.append(Result("aggs.open_close", True, f"date={target.isoformat()}"))
            open_close_done = True
            break
        except NotFoundError:
            target = _recent_weekday(target)
            _pace()
            continue
        except APIError as exc:
            print(f"\n-- aggs.open_close --\n  FAIL APIError {exc}")
            results.append(Result("aggs.open_close", False, str(exc)))
            open_close_done = True
            break
    if not open_close_done:
        note = f"no open-close data for {sample} in the last few weekdays"
        print(f"\n-- aggs.open_close --\n  SKIP {note}")
        results.append(Result("aggs.open_close", True, note))
    _pace()

    for kind in ("sma", "ema", "rsi"):
        method = getattr(client.options.indicators, kind)
        _run(
            f"indicators.{kind}",
            lambda method=method: method(
                sample, timespan="day", window=20, limit=2
            ),
            results,
        )
        _pace()

    _run(
        "indicators.macd",
        lambda: client.options.indicators.macd(
            sample,
            timespan="day",
            short_window=12,
            long_window=26,
            signal_window=9,
            limit=2,
        ),
        results,
    )
    _pace()

    client.close()
    return results, sample


async def run_async(api_key: str, sample: Optional[str]) -> List[Result]:
    results: List[Result] = []
    async with AsyncCuteMarkets(api_key=api_key, max_retries=0) as client:

        async def _awaitable(name: str, coro) -> Any:
            print(f"\n-- async {name} --")
            try:
                value = await coro
                print(f"  OK request_id={getattr(value, 'request_id', None)}")
                results.append(Result(f"async {name}", True))
                return value
            except ForbiddenError as exc:
                note = f"403 {exc.code}: {exc.message}"
                print(f"  SKIP {note}")
                results.append(Result(f"async {name}", True, note))
                return None
            except APIError as exc:
                print(f"  FAIL APIError {exc}")
                results.append(Result(f"async {name}", False, str(exc)))
                return None

        await _awaitable("status", client.status())
        await asyncio.sleep(PACE)
        await _awaitable("tickers.search", client.tickers.search(query="NFLX", limit=2))
        await asyncio.sleep(PACE)
        if sample:
            await _awaitable(
                "options.trades.last", client.options.trades.last(sample)
            )
    return results


def main() -> int:
    api_key = os.environ.get("CUTEMARKETS_API_KEY")
    if not api_key:
        raise SystemExit(
            "Set CUTEMARKETS_API_KEY=cm_... in your environment or .env file."
        )
    if not api_key.startswith("cm_"):
        print(f"WARNING: API key does not start with 'cm_' (got {api_key[:4]}...)")

    print("=== CuteMarkets live smoke test ===\n")
    print(f"Pacing: {PACE}s between calls (Free plan cap is 10 req/min)")

    sync_results, sample = run_sync(api_key)

    print("\n=== Async smoke ===")
    async_results = asyncio.run(run_async(api_key, sample))

    results = sync_results + async_results
    failures = [r for r in results if not r.ok]

    print("\n=== Summary ===")
    for r in results:
        status = "PASS" if r.ok else "FAIL"
        suffix = f" — {r.note}" if r.note else ""
        print(f"  {status:4} {r.name}{suffix}")

    print(f"\n{len(results) - len(failures)}/{len(results)} checks passed.")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
