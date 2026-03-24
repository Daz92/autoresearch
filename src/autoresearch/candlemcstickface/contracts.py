from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PromotionOutcome(str, Enum):
    PROMOTE = "promote"
    HOLD = "hold"
    REVERT = "revert"
    INVALID = "invalid"


@dataclass(frozen=True)
class WatcherContract:
    session_id: str
    generated_at: str
    agent: str
    asset: str
    price: float
    price_timestamp: str
    alerts: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScannerCandidateContract:
    symbol: str
    setup: str
    conviction: str
    catalyst: str
    discovered_at: str


@dataclass(frozen=True)
class StockScannerContract:
    session_id: str
    generated_at: str
    agent: str
    candidates: tuple[ScannerCandidateContract, ...] = ()


@dataclass(frozen=True)
class HeadlineContract:
    text: str
    source: str
    sentiment: str
    published_at: str


@dataclass(frozen=True)
class MacroDistillerContract:
    session_id: str
    generated_at: str
    agent: str
    asset: str
    sentiment: str
    confidence: float
    key_headlines: tuple[HeadlineContract, ...] = ()
    relevance_score: float = 0.0


__all__ = [
    "HeadlineContract",
    "MacroDistillerContract",
    "PromotionOutcome",
    "ScannerCandidateContract",
    "StockScannerContract",
    "WatcherContract",
]
