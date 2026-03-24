from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from ..contracts import (
    SignalProposal,
    SignalSide,
    TradeDataFreshness,
    TradeIntentPayload,
    TradeSignalInputs,
    utc_now,
)


def build_trade_intent_payload(
    *,
    signal: SignalProposal,
    watcher_session_id: str,
    macro_session_id: str,
    screener_session_id: str | None = None,
    price_timestamp: datetime | None = None,
    news_timestamp: datetime | None = None,
) -> dict[str, object]:
    intent = TradeIntentPayload(
        intent_id=f"intent-{uuid4()}",
        created_at=utc_now(),
        symbol=signal.symbol,
        side=SignalSide(signal.side.value),
        qty=1.0,
        type="market",
        limit_price=None,
        stop_price=signal.entry_zone.low,
        time_in_force="day",
        max_slippage_bps=25,
        max_risk_usd=100.0,
        signal_inputs=TradeSignalInputs(
            watcher_session_id=watcher_session_id,
            macro_session_id=macro_session_id,
            screener_session_id=screener_session_id,
        ),
        data_freshness=TradeDataFreshness(
            price_timestamp=price_timestamp or signal.available_at,
            news_timestamp=news_timestamp or signal.available_at,
        ),
        metadata={
            "source": "autoresearch",
            "market": signal.market.value,
            "as_of": signal.as_of.isoformat(),
            "confidence": signal.confidence,
            "thesis": signal.thesis,
            "target_logic": signal.target_logic,
            "provenance": list(signal.provenance),
        },
    )
    return intent.to_dict()
