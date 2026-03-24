from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ....contracts import Market, MarketSnapshot, parse_timestamp


@dataclass(frozen=True)
class CryptoAdapter:
    market: Market = Market.CRYPTO

    def normalize(self, payload: Mapping[str, Any]) -> MarketSnapshot:
        as_of = parse_timestamp(payload["as_of"])
        available_at = (
            parse_timestamp(payload["available_at"])
            if "available_at" in payload
            else as_of
        )
        symbol = str(payload["symbol"]).upper().replace("-", "/")
        return MarketSnapshot(
            market=self.market,
            symbol=symbol,
            as_of=as_of,
            available_at=available_at,
            price=float(payload["price"]),
            provenance=tuple(payload.get("provenance", ("adapter:crypto",))),
            features=dict(payload.get("features", {})),
            tradable=bool(payload.get("tradable", True)),
        )
