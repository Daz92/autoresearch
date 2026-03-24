from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def parse_timestamp(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


class Market(str, Enum):
    US_EQUITIES = "us_equities"
    CRYPTO = "crypto"


class SignalSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class PromotionState(str, Enum):
    ADVANCE = "advance"
    HOLD = "hold"
    REJECT = "reject"
    INVALID = "invalid"


@dataclass(frozen=True)
class EntryZone:
    low: float | None
    high: float | None

    def __post_init__(self) -> None:
        if self.low is not None and self.high is not None and self.low > self.high:
            raise ValueError("entry zone low cannot be greater than high")


@dataclass(frozen=True)
class TimeProvenance:
    market: Market
    symbol: str
    as_of: datetime
    available_at: datetime
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol is required")
        if not self.provenance:
            raise ValueError("provenance is required")
        object.__setattr__(self, "as_of", parse_timestamp(self.as_of))
        object.__setattr__(self, "available_at", parse_timestamp(self.available_at))


@dataclass(frozen=True)
class MarketSnapshot:
    market: Market
    symbol: str
    as_of: datetime
    available_at: datetime
    price: float
    provenance: tuple[str, ...]
    features: Mapping[str, Any] = field(default_factory=dict)
    tradable: bool = True

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol is required")
        if self.price <= 0:
            raise ValueError("price must be positive")
        if not self.provenance:
            raise ValueError("provenance is required")
        object.__setattr__(self, "as_of", parse_timestamp(self.as_of))
        object.__setattr__(self, "available_at", parse_timestamp(self.available_at))

    @property
    def time(self) -> TimeProvenance:
        return TimeProvenance(
            market=self.market,
            symbol=self.symbol,
            as_of=self.as_of,
            available_at=self.available_at,
            provenance=self.provenance,
        )


@dataclass(frozen=True)
class SignalProposal:
    market: Market
    symbol: str
    as_of: datetime
    available_at: datetime
    side: SignalSide
    confidence: float
    thesis: str
    entry_zone: EntryZone
    invalidation: str
    target_logic: str
    provenance: tuple[str, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol is required")
        if not self.thesis:
            raise ValueError("thesis is required")
        if not self.invalidation:
            raise ValueError("invalidation is required")
        if not self.target_logic:
            raise ValueError("target_logic is required")
        if not self.provenance:
            raise ValueError("provenance is required")
        object.__setattr__(self, "confidence", _clamp(self.confidence, 0.0, 1.0))
        object.__setattr__(self, "as_of", parse_timestamp(self.as_of))
        object.__setattr__(self, "available_at", parse_timestamp(self.available_at))

    @property
    def time(self) -> TimeProvenance:
        return TimeProvenance(
            market=self.market,
            symbol=self.symbol,
            as_of=self.as_of,
            available_at=self.available_at,
            provenance=self.provenance,
        )


@dataclass(frozen=True)
class MetricBundle:
    return_pct: float = 0.0
    drawdown: float = 0.0
    hit_rate: float = 0.0
    turnover: float = 0.0
    cost_sensitivity: float = 0.0
    regime_stability: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not -1.0 <= self.return_pct <= 10.0:
            raise ValueError("return_pct must be in [-1, 10]")
        for field_name in (
            "drawdown",
            "hit_rate",
            "turnover",
            "cost_sensitivity",
            "regime_stability",
        ):
            value = getattr(self, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be in [0, 1]")


@dataclass(frozen=True)
class PromotionDecision:
    state: PromotionState
    score: float | None
    score_version: str
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class TradeSignalInputs:
    watcher_session_id: str
    macro_session_id: str
    screener_session_id: str | None = None


@dataclass(frozen=True)
class TradeDataFreshness:
    price_timestamp: datetime
    news_timestamp: datetime

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "price_timestamp", parse_timestamp(self.price_timestamp)
        )
        object.__setattr__(self, "news_timestamp", parse_timestamp(self.news_timestamp))


@dataclass(frozen=True)
class TradeIntentPayload:
    intent_id: str
    created_at: datetime
    symbol: str
    side: SignalSide
    qty: float
    type: str
    limit_price: float | None
    stop_price: float | None
    time_in_force: str
    max_slippage_bps: int
    max_risk_usd: float
    signal_inputs: TradeSignalInputs
    data_freshness: TradeDataFreshness
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.intent_id:
            raise ValueError("intent_id is required")
        if not self.symbol:
            raise ValueError("symbol is required")
        if self.qty <= 0:
            raise ValueError("qty must be positive")
        if self.max_slippage_bps < 0:
            raise ValueError("max_slippage_bps must be >= 0")
        if self.max_risk_usd <= 0:
            raise ValueError("max_risk_usd must be positive")
        object.__setattr__(self, "created_at", parse_timestamp(self.created_at))

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "created_at": self.created_at.isoformat(),
            "symbol": self.symbol,
            "side": self.side.value,
            "qty": self.qty,
            "type": self.type,
            "limit_price": self.limit_price,
            "stop_price": self.stop_price,
            "time_in_force": self.time_in_force,
            "max_slippage_bps": self.max_slippage_bps,
            "max_risk_usd": self.max_risk_usd,
            "signal_inputs": {
                "watcher_session_id": self.signal_inputs.watcher_session_id,
                "macro_session_id": self.signal_inputs.macro_session_id,
                "screener_session_id": self.signal_inputs.screener_session_id,
            },
            "data_freshness": {
                "price_timestamp": self.data_freshness.price_timestamp.isoformat(),
                "news_timestamp": self.data_freshness.news_timestamp.isoformat(),
            },
            "metadata": dict(self.metadata),
        }
