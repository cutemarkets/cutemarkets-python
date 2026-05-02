"""Build a simple liquidity-aware options chain scanner.

Set ``CUTEMARKETS_API_KEY=cm_...`` and run:

    python examples/build_options_chain_scanner.py
"""

from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Iterable, List, Optional, Tuple

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from cutemarkets import ContractSnapshot, CuteMarkets


def spread_pct(contract: ContractSnapshot) -> Optional[float]:
    quote = contract.last_quote
    if quote is None or quote.bid is None or quote.ask is None:
        return None
    mid = (quote.bid + quote.ask) / 2.0
    if mid <= 0:
        return None
    return (quote.ask - quote.bid) / mid


def score_contracts(contracts: Iterable[ContractSnapshot]) -> List[Tuple[float, ContractSnapshot]]:
    ranked: List[Tuple[float, ContractSnapshot]] = []
    for contract in contracts:
        spread = spread_pct(contract)
        open_interest = float(contract.open_interest or 0.0)
        volume = float(contract.day.volume if contract.day and contract.day.volume is not None else 0.0)
        delta = abs(float(contract.greeks.delta or 0.0)) if contract.greeks else 0.0
        if spread is None or spread > 0.20:
            continue
        if open_interest < 100 or volume < 25:
            continue
        ranked.append((open_interest + (volume * 2.0) + (delta * 100.0), contract))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked


def main() -> None:
    api_key = os.environ.get("CUTEMARKETS_API_KEY")
    if not api_key:
        raise SystemExit("Set CUTEMARKETS_API_KEY=cm_... before running this example.")

    ticker = os.environ.get("CUTEMARKETS_UNDERLYING", "SPY").strip().upper()
    today = date.today()
    expiry_floor = today
    expiry_cap = today + timedelta(days=14)

    with CuteMarkets(api_key=api_key) as client:
        chain = client.options.chain(
            ticker,
            contract_type="call",
            expiration_date_gte=expiry_floor,
            expiration_date_lte=expiry_cap,
            limit=250,
        )
        ranked = score_contracts(chain.results)
        print(
            f"[chain] ticker={ticker} contracts={len(chain.results)} ranked={len(ranked)} "
            f"request_id={chain.request_id}"
        )
        for _, contract in ranked[:10]:
            details = contract.details
            quote = contract.last_quote
            spread = spread_pct(contract)
            if details is None or quote is None or spread is None:
                continue
            print(
                f"  {details.ticker} exp={details.expiration_date} strike={details.strike_price} "
                f"bid={quote.bid} ask={quote.ask} spread_pct={spread:.2%} "
                f"oi={contract.open_interest} volume={contract.day.volume if contract.day else None} "
                f"delta={contract.greeks.delta if contract.greeks else None}"
            )


if __name__ == "__main__":
    main()
