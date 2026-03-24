from __future__ import annotations

from abc import ABC, abstractmethod

from ..contracts import MarketSnapshot, SignalProposal


class SignalPlugin(ABC):
    family = "signal-agent"

    @abstractmethod
    def generate_signal(self, snapshot: MarketSnapshot) -> SignalProposal:
        raise NotImplementedError
