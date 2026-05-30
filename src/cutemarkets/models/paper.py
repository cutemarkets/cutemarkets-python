"""Response models for ``/v1/paper/...`` endpoints."""

from __future__ import annotations

from typing import Optional

from ._base import CuteBase


class PaperAccount(CuteBase):
    id: Optional[str] = None
    name: Optional[str] = None
    status: Optional[str] = None
    currency: Optional[str] = None
    initial_cash: Optional[str] = None
    cash: Optional[str] = None
    generation: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    reset_at: Optional[str] = None


class PaperAccountSummary(CuteBase):
    equity: Optional[str] = None
    cash: Optional[str] = None
    market_value: Optional[str] = None
    initial_cash: Optional[str] = None
    realized_pl: Optional[str] = None
    unrealized_pl: Optional[str] = None
    drawdown: Optional[str] = None
    closed_trades: Optional[int] = None
    winning_trades: Optional[int] = None
    win_rate: Optional[str] = None


class PaperAccountPayload(CuteBase):
    account: Optional[PaperAccount] = None
    summary: Optional[PaperAccountSummary] = None


class PaperOrder(CuteBase):
    id: Optional[str] = None
    client_order_id: Optional[str] = None
    symbol: Optional[str] = None
    asset_class: Optional[str] = None
    qty: Optional[str] = None
    filled_qty: Optional[str] = None
    side: Optional[str] = None
    type: Optional[str] = None
    time_in_force: Optional[str] = None
    limit_price: Optional[str] = None
    status: Optional[str] = None
    position_intent: Optional[str] = None
    order_class: Optional[str] = None
    extended_hours: Optional[bool] = None
    average_fill_price: Optional[str] = None
    filled_avg_price: Optional[str] = None
    rejected_reason: Optional[str] = None
    submitted_at: Optional[str] = None
    updated_at: Optional[str] = None
    filled_at: Optional[str] = None
    canceled_at: Optional[str] = None
    expired_at: Optional[str] = None
    rejected_at: Optional[str] = None


class PaperPosition(CuteBase):
    id: Optional[str] = None
    symbol: Optional[str] = None
    asset_class: Optional[str] = None
    qty: Optional[str] = None
    avg_entry_price: Optional[str] = None
    market_price: Optional[str] = None
    market_value: Optional[str] = None
    cost_basis: Optional[str] = None
    unrealized_pl: Optional[str] = None
    unrealized_plpc: Optional[str] = None
    realized_pl: Optional[str] = None
    updated_at: Optional[str] = None


class PaperFill(CuteBase):
    id: Optional[str] = None
    order_id: Optional[str] = None
    symbol: Optional[str] = None
    asset_class: Optional[str] = None
    side: Optional[str] = None
    qty: Optional[str] = None
    price: Optional[str] = None
    gross_amount: Optional[str] = None
    realized_pl: Optional[str] = None
    market_timestamp: Optional[str] = None
    created_at: Optional[str] = None


class PaperEquitySnapshot(CuteBase):
    timestamp: Optional[str] = None
    equity: Optional[str] = None
    cash: Optional[str] = None
    market_value: Optional[str] = None
    realized_pl: Optional[str] = None
    unrealized_pl: Optional[str] = None


__all__ = [
    "PaperAccount",
    "PaperAccountSummary",
    "PaperAccountPayload",
    "PaperOrder",
    "PaperPosition",
    "PaperFill",
    "PaperEquitySnapshot",
]
