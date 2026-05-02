"""Estimate implied move from the ATM straddle.

This example intentionally does not source an earnings calendar. You provide
the reference event date and the script chooses the nearest listed expiration
at or after that date.

Set ``CUTEMARKETS_API_KEY=cm_...`` and run:

    python examples/earnings_implied_move.py
"""

from __future__ import annotations

import os
from datetime import date
from typing import Iterable, Optional, Tuple

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from cutemarkets import ContractSnapshot, CuteMarkets


def midpoint(contract: ContractSnapshot) -> Optional[float]:
    quote = contract.last_quote
    if quote is None or quote.bid is None or quote.ask is None:
        return None
    return (quote.bid + quote.ask) / 2.0


def select_atm_pair(
    contracts: Iterable[ContractSnapshot],
    *,
    spot: float,
) -> Optional[Tuple[ContractSnapshot, ContractSnapshot]]:
    calls = [
        contract
        for contract in contracts
        if contract.details and contract.details.contract_type == "call" and contract.details.strike_price is not None
    ]
    puts = [
        contract
        for contract in contracts
        if contract.details and contract.details.contract_type == "put" and contract.details.strike_price is not None
    ]
    if not calls or not puts:
        return None

    calls.sort(key=lambda contract: abs(float(contract.details.strike_price) - spot))
    puts.sort(key=lambda contract: abs(float(contract.details.strike_price) - spot))

    best_call = calls[0]
    call_strike = float(best_call.details.strike_price)
    same_strike_puts = [
        contract
        for contract in puts
        if contract.details and contract.details.strike_price == call_strike
    ]
    best_put = same_strike_puts[0] if same_strike_puts else puts[0]
    return best_call, best_put


def main() -> None:
    api_key = os.environ.get("CUTEMARKETS_API_KEY")
    if not api_key:
        raise SystemExit("Set CUTEMARKETS_API_KEY=cm_... before running this example.")

    underlying = os.environ.get("CUTEMARKETS_UNDERLYING", "MSFT").strip().upper()
    event_day = date.fromisoformat(os.environ.get("CUTEMARKETS_EVENT_DATE", "2026-04-29"))

    with CuteMarkets(api_key=api_key) as client:
        expirations = client.tickers.expirations(underlying).results
        expiry = next((value for value in expirations if value >= event_day.isoformat()), None)
        if expiry is None:
            raise SystemExit(f"No listed expiration was found on or after {event_day.isoformat()}.")

        chain = client.options.chain(underlying, expiration_date=expiry, limit=250)
        if not chain.results:
            raise SystemExit(f"No contracts returned for {underlying} at {expiry}.")

        first_spot = chain.results[0].underlying_asset.price if chain.results[0].underlying_asset else None
        if first_spot is None:
            raise SystemExit("Underlying spot price was missing from the option chain snapshot.")

        pair = select_atm_pair(chain.results, spot=float(first_spot))
        if pair is None:
            raise SystemExit("Could not identify an ATM call/put pair.")
        call_contract, put_contract = pair
        call_mid = midpoint(call_contract)
        put_mid = midpoint(put_contract)
        if call_mid is None or put_mid is None:
            raise SystemExit("ATM pair did not have complete bid/ask data.")

        straddle_mid = call_mid + put_mid
        implied_move_pct = straddle_mid / float(first_spot)
        print(f"[earnings] underlying={underlying} event_day={event_day.isoformat()} expiry={expiry}")
        print(f"  spot={float(first_spot):.2f}")
        print(
            f"  call={call_contract.details.ticker} put={put_contract.details.ticker} "
            f"strike={call_contract.details.strike_price}"
        )
        print(f"  straddle_mid={straddle_mid:.2f}")
        print(f"  implied_move_abs={straddle_mid:.2f}")
        print(f"  implied_move_pct={implied_move_pct:.2%}")


if __name__ == "__main__":
    main()
