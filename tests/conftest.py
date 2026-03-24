from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def pytest_sessionstart(session: pytest.Session) -> None:
    if str(SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(SRC_ROOT))


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def fixed_time() -> datetime:
    return datetime(2026, 3, 23, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_metrics():
    contracts = __import__("autoresearch.contracts", fromlist=["MetricBundle"])
    MetricBundle = contracts.MetricBundle

    return MetricBundle(
        return_pct=0.30,
        drawdown=0.12,
        hit_rate=0.61,
        turnover=0.30,
        cost_sensitivity=0.22,
        regime_stability=0.71,
    )


@pytest.fixture
def sample_signal(fixed_time: datetime):
    contracts = __import__(
        "autoresearch.contracts",
        fromlist=["EntryZone", "Market", "SignalProposal", "SignalSide"],
    )
    EntryZone = contracts.EntryZone
    Market = contracts.Market
    SignalProposal = contracts.SignalProposal
    SignalSide = contracts.SignalSide

    return SignalProposal(
        market=Market.CRYPTO,
        symbol="BTC/USD",
        as_of=fixed_time,
        available_at=fixed_time,
        side=SignalSide.BUY,
        confidence=0.81,
        thesis="Momentum breakout with clean structure",
        entry_zone=EntryZone(low=86000.0, high=87000.0),
        invalidation="Close below 85000",
        target_logic="Scale at 1R and 2R",
        provenance=("test:fixture",),
    )
