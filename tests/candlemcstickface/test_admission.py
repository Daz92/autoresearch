from importlib import import_module
from pathlib import Path


def test_rejects_watcher_payload_without_price_timestamp(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    admission = import_module("autoresearch.candlemcstickface.admission")

    payload = {
        "session_id": "watcher-abc",
        "generated_at": "2026-03-24T00:00:00Z",
        "agent": "watcher",
        "asset": "SOL/USD",
        "price": 100.0,
    }

    result = admission.admit_watcher_payload(payload)

    assert result.status == "invalid"
    assert "missing:price_timestamp" in result.reasons


def test_accepts_complete_watcher_payload(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    admission = import_module("autoresearch.candlemcstickface.admission")

    payload = {
        "session_id": "watcher-abc",
        "generated_at": "2026-03-24T00:05:00Z",
        "agent": "watcher",
        "asset": "SOL/USD",
        "price": 100.0,
        "price_timestamp": "2026-03-24T00:04:30Z",
        "alerts": ["volume_spike"],
    }

    result = admission.admit_watcher_payload(payload)

    assert result.status == "complete"
    assert result.reasons == ()
    assert result.quality_score == 1.0


def test_marks_stale_payload_as_degraded(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    admission = import_module("autoresearch.candlemcstickface.admission")

    payload = {
        "session_id": "watcher-abc",
        "generated_at": "2026-03-24T00:10:01Z",
        "agent": "watcher",
        "asset": "SOL/USD",
        "price": 100.0,
        "price_timestamp": "2026-03-24T00:00:00Z",
        "alerts": ["volume_spike"],
    }

    result = admission.admit_watcher_payload(payload)

    assert result.status == "degraded"
    assert "freshness:stale_price_data" in result.reasons


def test_marks_alerts_missing_as_insufficient(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    admission = import_module("autoresearch.candlemcstickface.admission")

    payload = {
        "session_id": "watcher-abc",
        "generated_at": "2026-03-24T00:05:00Z",
        "agent": "watcher",
        "asset": "SOL/USD",
        "price": 100.0,
        "price_timestamp": "2026-03-24T00:04:30Z",
    }

    result = admission.admit_watcher_payload(payload)

    assert result.status == "insufficient"
    assert "insufficient:alerts_missing" in result.reasons


def test_rejects_agent_mismatch_as_invalid(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    admission = import_module("autoresearch.candlemcstickface.admission")

    payload = {
        "session_id": "watcher-abc",
        "generated_at": "2026-03-24T00:05:00Z",
        "agent": "not-watcher",
        "asset": "SOL/USD",
        "price": 100.0,
        "price_timestamp": "2026-03-24T00:04:30Z",
        "alerts": ["volume_spike"],
    }

    result = admission.admit_watcher_payload(payload)

    assert result.status == "invalid"
    assert "inconsistent:agent_mismatch" in result.reasons
