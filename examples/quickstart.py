"""Minimal end-to-end quickstart for the CuteMarkets Python client.

Set ``CUTEMARKETS_API_KEY=cm_...`` in your environment (or a ``.env`` file
loaded by ``python-dotenv``) and run:

    python examples/quickstart.py
"""

from __future__ import annotations

import os
from datetime import date, timedelta

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from cutemarkets import CuteMarkets
from cutemarkets.errors import ForbiddenError


def main() -> None:
    api_key = os.environ.get("CUTEMARKETS_API_KEY")
    if not api_key:
        raise SystemExit(
            "Set CUTEMARKETS_API_KEY=cm_... in your environment before running."
        )

    client = CuteMarkets(api_key=api_key)

    health = client.status()
    print(f"[status] {health.status}")

    chain = client.options.chain("NFLX", limit=3)
    print(f"[chain] {len(chain)} contracts (request_id={chain.request_id})")
    if not chain.results:
        print("No contracts on NFLX, stopping early.")
        return

    sample = chain.results[0].details.ticker
    if sample is None:
        print("First contract missing ticker, stopping early.")
        return
    print(f"[chain] sample contract: {sample}")

    snap = client.options.snapshot("NFLX", sample)
    print(f"[snapshot] break_even_price={snap.break_even_price}")

    try:
        last = client.options.trades.last(sample)
        print(f"[last trade] price={last.price} size={last.size} ticker={last.ticker}")
    except ForbiddenError as exc:
        print(f"[last trade] forbidden: {exc.message}")

    today = date.today()
    prev = client.options.aggs.previous(sample)
    print(f"[previous day] close={prev.close} volume={prev.volume}")

    bars = client.options.aggs.range(
        sample, 1, "day", today - timedelta(days=30), today, limit=5
    )
    print(f"[aggs] {len(bars)} daily bars")
    for bar in bars:
        print(f"  {bar.timestamp}: o={bar.open} h={bar.high} l={bar.low} c={bar.close}")

    sma = client.options.indicators.sma(sample, timespan="day", window=20, limit=3)
    print(f"[sma] {len(sma.values)} points")

    client.close()


if __name__ == "__main__":
    main()
