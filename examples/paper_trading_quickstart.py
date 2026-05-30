from __future__ import annotations

import os

from cutemarkets import CuteMarkets


def main() -> None:
    client = CuteMarkets(paper_api_key=os.environ.get("CUTEMARKETS_PAPER_API_KEY"))
    try:
        accounts = client.paper.accounts.list()
        account = accounts.results[0] if accounts.results else None
        if account is None or not account.id:
            created = client.paper.accounts.create(name="python-sdk-sandbox", initial_cash="100000")
            account = created.account
        if account is None or not account.id:
            raise SystemExit("Could not resolve a paper trading account.")

        order = client.paper.orders.submit(
            account.id,
            symbol=os.environ.get("CUTEMARKETS_PAPER_SYMBOL", "AAPL").strip().upper(),
            qty=os.environ.get("CUTEMARKETS_PAPER_QTY", "1"),
            side="buy",
            type="market",
            time_in_force="day",
            client_order_id=os.environ.get("CUTEMARKETS_PAPER_CLIENT_ORDER_ID", "python-sdk-demo-1"),
        )
        summary = client.paper.account(account.id)
        print(f"[paper] account={account.id} order={order.id} status={order.status} equity={summary.equity}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
