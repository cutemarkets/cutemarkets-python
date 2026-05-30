"""``client.paper`` namespace for CuteMarkets paper trading."""

from __future__ import annotations

from typing import Any, AsyncIterator, Iterator, Optional

from .._pagination import AsyncPage, Page
from .._transport import DEFAULT_AUTH_KEY, AsyncTransport, Transport
from ..models.paper import (
    PaperAccount,
    PaperAccountPayload,
    PaperAccountSummary,
    PaperEquitySnapshot,
    PaperFill,
    PaperOrder,
    PaperPosition,
)


def _accounts_path(account_id: Optional[str] = None, suffix: str = "") -> str:
    base = "/v1/paper/accounts/"
    if not account_id:
        return base
    return f"{base}{account_id}/{suffix.lstrip('/')}"


class PaperAccountsResource:
    def __init__(self, transport: Transport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key

    def list(self, *, include_archived: Optional[bool] = None, **params: Any) -> Page[PaperAccount]:
        response = self._t.request(
            "GET",
            _accounts_path(),
            params={"include_archived": include_archived, **params},
            api_key=self._api_key,
        )
        return Page.from_response(
            response,
            transport=self._t,
            parser=PaperAccount.model_validate,
            api_key=self._api_key,
        )

    def iter_list(self, *, include_archived: Optional[bool] = None, **params: Any) -> Iterator[PaperAccount]:
        page = self.list(include_archived=include_archived, **params)
        yield from page.iter_all()

    def create(self, *, name: str = "Paper Account", initial_cash: Any = "100000") -> PaperAccountPayload:
        response = self._t.request(
            "POST",
            _accounts_path(),
            json={"name": name, "initial_cash": str(initial_cash)},
            api_key=self._api_key,
        )
        return PaperAccountPayload.model_validate(response.data)

    def get(self, account_id: str) -> PaperAccountPayload:
        response = self._t.request("GET", _accounts_path(account_id), api_key=self._api_key)
        return PaperAccountPayload.model_validate(response.data)

    def update(self, account_id: str, *, name: str) -> PaperAccountPayload:
        response = self._t.request(
            "PATCH",
            _accounts_path(account_id),
            json={"name": name},
            api_key=self._api_key,
        )
        return PaperAccountPayload.model_validate(response.data)

    def delete(self, account_id: str) -> None:
        self._t.request("DELETE", _accounts_path(account_id), api_key=self._api_key)
        return None

    def reset(
        self,
        account_id: str,
        *,
        confirm: bool = True,
        initial_cash: Optional[Any] = None,
        reason: str = "",
    ) -> PaperAccountPayload:
        payload: dict[str, Any] = {"confirm": confirm}
        if initial_cash is not None:
            payload["initial_cash"] = str(initial_cash)
        if reason:
            payload["reason"] = reason
        response = self._t.request(
            "POST",
            _accounts_path(account_id, "reset/"),
            json=payload,
            api_key=self._api_key,
        )
        return PaperAccountPayload.model_validate(response.data)

    def summary(self, account_id: str) -> PaperAccountSummary:
        response = self._t.request("GET", _accounts_path(account_id, "account/"), api_key=self._api_key)
        return PaperAccountSummary.model_validate(response.data)

    def portfolio_history(self, account_id: str) -> Page[PaperEquitySnapshot]:
        response = self._t.request(
            "GET",
            _accounts_path(account_id, "portfolio/history/"),
            api_key=self._api_key,
        )
        return Page.from_response(
            response,
            transport=self._t,
            parser=PaperEquitySnapshot.model_validate,
            api_key=self._api_key,
        )


class AsyncPaperAccountsResource:
    def __init__(self, transport: AsyncTransport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key

    async def list(self, *, include_archived: Optional[bool] = None, **params: Any) -> AsyncPage[PaperAccount]:
        response = await self._t.request(
            "GET",
            _accounts_path(),
            params={"include_archived": include_archived, **params},
            api_key=self._api_key,
        )
        return AsyncPage.from_response(
            response,
            transport=self._t,
            parser=PaperAccount.model_validate,
            api_key=self._api_key,
        )

    async def iter_list(self, *, include_archived: Optional[bool] = None, **params: Any) -> AsyncIterator[PaperAccount]:
        page = await self.list(include_archived=include_archived, **params)
        async for item in page.iter_all():
            yield item

    async def create(self, *, name: str = "Paper Account", initial_cash: Any = "100000") -> PaperAccountPayload:
        response = await self._t.request(
            "POST",
            _accounts_path(),
            json={"name": name, "initial_cash": str(initial_cash)},
            api_key=self._api_key,
        )
        return PaperAccountPayload.model_validate(response.data)

    async def get(self, account_id: str) -> PaperAccountPayload:
        response = await self._t.request("GET", _accounts_path(account_id), api_key=self._api_key)
        return PaperAccountPayload.model_validate(response.data)

    async def update(self, account_id: str, *, name: str) -> PaperAccountPayload:
        response = await self._t.request(
            "PATCH",
            _accounts_path(account_id),
            json={"name": name},
            api_key=self._api_key,
        )
        return PaperAccountPayload.model_validate(response.data)

    async def delete(self, account_id: str) -> None:
        await self._t.request("DELETE", _accounts_path(account_id), api_key=self._api_key)
        return None

    async def reset(
        self,
        account_id: str,
        *,
        confirm: bool = True,
        initial_cash: Optional[Any] = None,
        reason: str = "",
    ) -> PaperAccountPayload:
        payload: dict[str, Any] = {"confirm": confirm}
        if initial_cash is not None:
            payload["initial_cash"] = str(initial_cash)
        if reason:
            payload["reason"] = reason
        response = await self._t.request(
            "POST",
            _accounts_path(account_id, "reset/"),
            json=payload,
            api_key=self._api_key,
        )
        return PaperAccountPayload.model_validate(response.data)

    async def summary(self, account_id: str) -> PaperAccountSummary:
        response = await self._t.request("GET", _accounts_path(account_id, "account/"), api_key=self._api_key)
        return PaperAccountSummary.model_validate(response.data)

    async def portfolio_history(self, account_id: str) -> AsyncPage[PaperEquitySnapshot]:
        response = await self._t.request(
            "GET",
            _accounts_path(account_id, "portfolio/history/"),
            api_key=self._api_key,
        )
        return AsyncPage.from_response(
            response,
            transport=self._t,
            parser=PaperEquitySnapshot.model_validate,
            api_key=self._api_key,
        )


class PaperOrdersResource:
    def __init__(self, transport: Transport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key

    def list(self, account_id: str, *, status: Optional[str] = None, limit: Optional[int] = None, **params: Any) -> Page[PaperOrder]:
        response = self._t.request(
            "GET",
            _accounts_path(account_id, "orders/"),
            params={"status": status, "limit": limit, **params},
            api_key=self._api_key,
        )
        return Page.from_response(
            response,
            transport=self._t,
            parser=PaperOrder.model_validate,
            api_key=self._api_key,
        )

    def iter_list(self, account_id: str, **params: Any) -> Iterator[PaperOrder]:
        page = self.list(account_id, **params)
        yield from page.iter_all()

    def submit(
        self,
        account_id: str,
        *,
        symbol: str,
        qty: Any,
        side: str,
        type: str,
        time_in_force: str = "day",
        limit_price: Optional[Any] = None,
        client_order_id: str = "",
        position_intent: str = "",
        **extra: Any,
    ) -> PaperOrder:
        payload = {
            "symbol": symbol,
            "qty": str(qty),
            "side": side,
            "type": type,
            "time_in_force": time_in_force,
            **extra,
        }
        if limit_price is not None:
            payload["limit_price"] = str(limit_price)
        if client_order_id:
            payload["client_order_id"] = client_order_id
        if position_intent:
            payload["position_intent"] = position_intent
        response = self._t.request(
            "POST",
            _accounts_path(account_id, "orders/"),
            json=payload,
            api_key=self._api_key,
        )
        return PaperOrder.model_validate(response.data)

    def get(self, account_id: str, order_id: str) -> PaperOrder:
        response = self._t.request(
            "GET",
            _accounts_path(account_id, f"orders/{order_id}/"),
            api_key=self._api_key,
        )
        return PaperOrder.model_validate(response.data)

    def cancel(self, account_id: str, order_id: str) -> PaperOrder:
        response = self._t.request(
            "DELETE",
            _accounts_path(account_id, f"orders/{order_id}/"),
            api_key=self._api_key,
        )
        return PaperOrder.model_validate(response.data)

    def by_client_order_id(self, account_id: str, client_order_id: str) -> PaperOrder:
        response = self._t.request(
            "GET",
            _accounts_path(account_id, "orders:by_client_order_id"),
            params={"client_order_id": client_order_id},
            api_key=self._api_key,
        )
        return PaperOrder.model_validate(response.data)


class AsyncPaperOrdersResource:
    def __init__(self, transport: AsyncTransport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key

    async def list(self, account_id: str, *, status: Optional[str] = None, limit: Optional[int] = None, **params: Any) -> AsyncPage[PaperOrder]:
        response = await self._t.request(
            "GET",
            _accounts_path(account_id, "orders/"),
            params={"status": status, "limit": limit, **params},
            api_key=self._api_key,
        )
        return AsyncPage.from_response(
            response,
            transport=self._t,
            parser=PaperOrder.model_validate,
            api_key=self._api_key,
        )

    async def iter_list(self, account_id: str, **params: Any) -> AsyncIterator[PaperOrder]:
        page = await self.list(account_id, **params)
        async for item in page.iter_all():
            yield item

    async def submit(
        self,
        account_id: str,
        *,
        symbol: str,
        qty: Any,
        side: str,
        type: str,
        time_in_force: str = "day",
        limit_price: Optional[Any] = None,
        client_order_id: str = "",
        position_intent: str = "",
        **extra: Any,
    ) -> PaperOrder:
        payload = {
            "symbol": symbol,
            "qty": str(qty),
            "side": side,
            "type": type,
            "time_in_force": time_in_force,
            **extra,
        }
        if limit_price is not None:
            payload["limit_price"] = str(limit_price)
        if client_order_id:
            payload["client_order_id"] = client_order_id
        if position_intent:
            payload["position_intent"] = position_intent
        response = await self._t.request(
            "POST",
            _accounts_path(account_id, "orders/"),
            json=payload,
            api_key=self._api_key,
        )
        return PaperOrder.model_validate(response.data)

    async def get(self, account_id: str, order_id: str) -> PaperOrder:
        response = await self._t.request(
            "GET",
            _accounts_path(account_id, f"orders/{order_id}/"),
            api_key=self._api_key,
        )
        return PaperOrder.model_validate(response.data)

    async def cancel(self, account_id: str, order_id: str) -> PaperOrder:
        response = await self._t.request(
            "DELETE",
            _accounts_path(account_id, f"orders/{order_id}/"),
            api_key=self._api_key,
        )
        return PaperOrder.model_validate(response.data)

    async def by_client_order_id(self, account_id: str, client_order_id: str) -> PaperOrder:
        response = await self._t.request(
            "GET",
            _accounts_path(account_id, "orders:by_client_order_id"),
            params={"client_order_id": client_order_id},
            api_key=self._api_key,
        )
        return PaperOrder.model_validate(response.data)


class PaperResource:
    """Sync ``client.paper`` namespace."""

    def __init__(self, transport: Transport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key
        self.accounts = PaperAccountsResource(transport, api_key=api_key)
        self.orders = PaperOrdersResource(transport, api_key=api_key)

    def positions(self, account_id: str) -> Page[PaperPosition]:
        response = self._t.request("GET", _accounts_path(account_id, "positions/"), api_key=self._api_key)
        return Page.from_response(
            response,
            transport=self._t,
            parser=PaperPosition.model_validate,
            api_key=self._api_key,
        )

    def fills(self, account_id: str) -> Page[PaperFill]:
        response = self._t.request("GET", _accounts_path(account_id, "fills/"), api_key=self._api_key)
        return Page.from_response(
            response,
            transport=self._t,
            parser=PaperFill.model_validate,
            api_key=self._api_key,
        )

    def portfolio_history(self, account_id: str) -> Page[PaperEquitySnapshot]:
        return self.accounts.portfolio_history(account_id)

    def account(self, account_id: str) -> PaperAccountSummary:
        return self.accounts.summary(account_id)


class AsyncPaperResource:
    """Async ``client.paper`` namespace."""

    def __init__(self, transport: AsyncTransport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key
        self.accounts = AsyncPaperAccountsResource(transport, api_key=api_key)
        self.orders = AsyncPaperOrdersResource(transport, api_key=api_key)

    async def positions(self, account_id: str) -> AsyncPage[PaperPosition]:
        response = await self._t.request("GET", _accounts_path(account_id, "positions/"), api_key=self._api_key)
        return AsyncPage.from_response(
            response,
            transport=self._t,
            parser=PaperPosition.model_validate,
            api_key=self._api_key,
        )

    async def fills(self, account_id: str) -> AsyncPage[PaperFill]:
        response = await self._t.request("GET", _accounts_path(account_id, "fills/"), api_key=self._api_key)
        return AsyncPage.from_response(
            response,
            transport=self._t,
            parser=PaperFill.model_validate,
            api_key=self._api_key,
        )

    async def portfolio_history(self, account_id: str) -> AsyncPage[PaperEquitySnapshot]:
        return await self.accounts.portfolio_history(account_id)

    async def account(self, account_id: str) -> PaperAccountSummary:
        return await self.accounts.summary(account_id)


__all__ = ["PaperResource", "AsyncPaperResource"]
