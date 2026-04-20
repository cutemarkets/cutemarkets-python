"""``/v1/options/snapshot/{underlying}/{option_contract}/`` — one contract."""

from __future__ import annotations

from ..._transport import AsyncTransport, Transport
from ...models.options import ContractSnapshot
from .._base import _parse_single, quote_path


def _path(underlying: str, option_contract: str) -> str:
    return f"/v1/options/snapshot/{quote_path(underlying)}/{quote_path(option_contract)}/"


class SnapshotResource:
    """Sync single-contract snapshot resource.

    See [docs/option-contract-snapshot.md](https://cutemarkets.com/docs/option-contract-snapshot).
    """

    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def __call__(self, underlying: str, option_contract: str) -> ContractSnapshot:
        """Fetch the snapshot for one option contract.

        ``underlying`` must match the root symbol of ``option_contract``.
        """
        response = self._t.request("GET", _path(underlying, option_contract))
        return _parse_single(response.data, ContractSnapshot.model_validate)


class AsyncSnapshotResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def __call__(self, underlying: str, option_contract: str) -> ContractSnapshot:
        response = await self._t.request("GET", _path(underlying, option_contract))
        return _parse_single(response.data, ContractSnapshot.model_validate)


__all__ = ["SnapshotResource", "AsyncSnapshotResource"]
