"""Inspect historical quote quality for one option contract.

Historical options quotes require an Expert plan. If your key does not have
access, the SDK raises ``ForbiddenError`` and this example exits cleanly.

Set ``CUTEMARKETS_API_KEY=cm_...`` and run:

    python examples/quote_quality_filter.py
"""

from __future__ import annotations

import os
from statistics import median
from typing import List

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
        raise SystemExit("Set CUTEMARKETS_API_KEY=cm_... before running this example.")

    option_ticker = os.environ.get("CUTEMARKETS_OPTION_TICKER", "O:SPY260417C00580000").strip().upper()

    with CuteMarkets(api_key=api_key) as client:
        try:
            page = client.options.quotes.list(option_ticker, limit=50)
        except ForbiddenError as exc:
            raise SystemExit(f"Quote history is unavailable on this plan: {exc.message}") from exc

    spreads: List[float] = []
    mids: List[float] = []
    for quote in page.results:
        if quote.bid_price is None or quote.ask_price is None:
            continue
        mid = (quote.bid_price + quote.ask_price) / 2.0
        if mid <= 0:
            continue
        mids.append(mid)
        spreads.append((quote.ask_price - quote.bid_price) / mid)

    if not spreads:
        print(f"[quotes] {option_ticker} returned no usable bid/ask pairs.")
        return

    print(f"[quotes] ticker={option_ticker} count={len(spreads)} request_id={page.request_id}")
    print(f"  median_mid={median(mids):.4f}")
    print(f"  median_spread_pct={median(spreads):.2%}")
    print(f"  max_spread_pct={max(spreads):.2%}")
    print(f"  usable_under_10pct={sum(1 for value in spreads if value <= 0.10)}")


if __name__ == "__main__":
    main()
