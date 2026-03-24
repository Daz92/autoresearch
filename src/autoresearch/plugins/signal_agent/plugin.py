from __future__ import annotations

from dataclasses import dataclass

from ...contracts import EntryZone, MarketSnapshot, SignalProposal, SignalSide
from ..base import SignalPlugin


@dataclass(frozen=True)
class SignalAgentPlugin(SignalPlugin):
    min_confidence: float = 0.60

    def generate_signal(self, snapshot: MarketSnapshot) -> SignalProposal:
        side = SignalSide.BUY if snapshot.price > 0 else SignalSide.SELL
        confidence = max(self.min_confidence, 0.75 if snapshot.tradable else 0.50)
        return SignalProposal(
            market=snapshot.market,
            symbol=snapshot.symbol,
            as_of=snapshot.as_of,
            available_at=snapshot.available_at,
            side=side,
            confidence=confidence,
            thesis=f"{snapshot.market.value} baseline signal from normalized snapshot",
            entry_zone=EntryZone(low=snapshot.price * 0.99, high=snapshot.price * 1.01),
            invalidation="Price breaks below setup support band",
            target_logic="Take profit in two increments at 1R and 2R",
            provenance=tuple(snapshot.provenance) + ("plugin:signal-agent",),
            metadata={"plugin_family": self.family},
        )
