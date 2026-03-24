from datetime import datetime, timezone


def _load(module_name: str):
    return __import__(module_name, fromlist=["*"])


def test_rejects_artifact_without_available_at() -> None:
    ensure_time_order = _load("autoresearch.provenance").ensure_time_order

    artifact = {
        "market": "crypto",
        "symbol": "BTC/USD",
        "as_of": "2026-03-23T12:00:00Z",
        "provenance": ["unit-test"],
    }
    result = ensure_time_order(artifact)
    assert result.is_valid is False
    assert "available_at" in result.errors[0]


def test_promotion_state_enum_contains_invalid() -> None:
    PromotionState = _load("autoresearch.contracts").PromotionState

    assert PromotionState.INVALID.value == "invalid"


def test_accepts_valid_artifact() -> None:
    ensure_time_order = _load("autoresearch.provenance").ensure_time_order

    artifact = {
        "market": "us_equities",
        "symbol": "AAPL",
        "as_of": "2026-03-23T12:00:00Z",
        "available_at": "2026-03-23T12:00:01Z",
        "provenance": ["feed:polygon"],
    }
    result = ensure_time_order(artifact)
    assert result.is_valid is True
    assert result.artifact is not None


def test_rejects_when_available_at_precedes_as_of() -> None:
    contracts = _load("autoresearch.contracts")
    Market = contracts.Market
    TimeProvenance = contracts.TimeProvenance
    ensure_time_order = _load("autoresearch.provenance").ensure_time_order

    as_of = datetime(2026, 3, 23, 12, 0, tzinfo=timezone.utc)
    artifact = TimeProvenance(
        market=Market.CRYPTO,
        symbol="BTC/USD",
        as_of=as_of,
        available_at=as_of.replace(minute=59, hour=11),
        provenance=("feed:unit",),
    )
    result = ensure_time_order(artifact)
    assert result.is_valid is False
    assert "available_at" in result.errors[0]
