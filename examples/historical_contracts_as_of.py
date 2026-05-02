"""Find historical option contracts as of a given date.

Set ``CUTEMARKETS_API_KEY=cm_...`` and run:

    python examples/historical_contracts_as_of.py
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


def main() -> None:
    api_key = os.environ.get("CUTEMARKETS_API_KEY")
    if not api_key:
        raise SystemExit("Set CUTEMARKETS_API_KEY=cm_... before running this example.")

    underlying = os.environ.get("CUTEMARKETS_UNDERLYING", "MSFT").strip().upper()
    as_of = date.fromisoformat(os.environ.get("CUTEMARKETS_AS_OF", "2026-01-15"))
    expiry_floor = as_of + timedelta(days=7)
    expiry_cap = as_of + timedelta(days=45)

    with CuteMarkets(api_key=api_key) as client:
        page = client.options.contracts.list(
            underlying_ticker=underlying,
            as_of=as_of,
            expiration_date_gte=expiry_floor,
            expiration_date_lte=expiry_cap,
            limit=10,
        )
        print(
            f"[contracts.list] {underlying} as_of={as_of.isoformat()} "
            f"count={len(page.results)} request_id={page.request_id}"
        )
        if not page.results:
            print("No contracts matched the filter window.")
            return

        for contract in page.results[:5]:
            print(
                "  ",
                contract.ticker,
                contract.contract_type,
                contract.expiration_date,
                contract.strike_price,
            )

        sample = page.results[0]
        if not sample.ticker:
            print("First contract was missing a ticker; stopping.")
            return
        detail = client.options.contracts.get(sample.ticker, as_of=as_of)
        print("[contracts.get]")
        print(
            f"  ticker={detail.ticker} underlying={detail.underlying_ticker} "
            f"type={detail.contract_type} expiration={detail.expiration_date} "
            f"strike={detail.strike_price}"
        )


if __name__ == "__main__":
    main()
