from __future__ import annotations

import os
from datetime import date, timedelta

from cutemarkets import CuteMarkets


def main() -> None:
    client = CuteMarkets(stocks_api_key=os.environ.get("CUTEMARKETS_STOCKS_API_KEY"))
    ticker = os.environ.get("CUTEMARKETS_STOCK_TICKER", "AAPL").strip().upper()
    end = date.today()
    start = end - timedelta(days=5)
    try:
        snapshot = client.stocks.snapshot(ticker)
        print(f"[snapshot] ticker={ticker} raw_keys={sorted(snapshot.raw.keys())[:8]}")

        bars = client.stocks.aggs.range(ticker, 1, "day", start, end, adjusted=True, limit=10)
        for bar in bars:
            print(ticker, bar.timestamp, bar.open, bar.high, bar.low, bar.close)
    finally:
        client.close()


if __name__ == "__main__":
    main()
