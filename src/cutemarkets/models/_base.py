"""Base Pydantic model for every CuteMarkets response type.

All response models:

* Tolerate unknown fields via ``extra="allow"`` so new server fields do not
  break existing client code.
* Preserve the original JSON payload on :attr:`CuteBase.raw` so callers can
  always reach the unaltered response.
* Support both the short wire names (e.g. ``T``, ``p``, ``s`` on
  :class:`~cutemarkets.models.options.LastTrade`) and readable property
  aliases (``ticker``, ``price``, ``size``).
"""

from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, PrivateAttr, model_validator


class CuteBase(BaseModel):
    """Shared base for all CuteMarkets response models."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    _raw: Dict[str, Any] = PrivateAttr(default_factory=dict)

    @model_validator(mode="wrap")
    @classmethod
    def _capture_raw(cls, data: Any, handler: Any) -> "CuteBase":
        instance = handler(data)
        if isinstance(data, dict):
            instance._raw = data
        return instance

    @property
    def raw(self) -> Dict[str, Any]:
        """The untouched JSON payload this model was built from.

        Falls back to :meth:`model_dump` if the model was constructed without
        going through :meth:`model_validate` on a dict payload.
        """
        if self._raw:
            return self._raw
        return self.model_dump(by_alias=True, exclude_none=True)
