from importlib import import_module
from pathlib import Path


def test_append_registry_record_creates_append_only_log(
    monkeypatch, autoresearch_src_root: Path, tmp_path: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    contracts = import_module("autoresearch.candlemcstickface.contracts")
    registry = import_module("autoresearch.candlemcstickface.registry")

    path = tmp_path / "registry.json"

    first = registry.append_registry_record(
        path,
        bundle_hash="bundle-a",
        outcome=contracts.PromotionOutcome.HOLD,
        score_delta=0.1,
        details={"reason": "insufficient"},
        created_at="2026-03-24T12:00:00Z",
    )
    second = registry.append_registry_record(
        path,
        bundle_hash="bundle-b",
        outcome=contracts.PromotionOutcome.PROMOTE,
        score_delta=1.2,
        details={"reason": "winner"},
        created_at="2026-03-24T12:05:00Z",
    )

    loaded = registry.load_registry(path)

    assert len(loaded) == 2
    assert loaded[0].experiment_id == first.experiment_id
    assert loaded[1].experiment_id == second.experiment_id
    assert loaded[0].outcome == contracts.PromotionOutcome.HOLD
    assert loaded[1].outcome == contracts.PromotionOutcome.PROMOTE


def test_load_registry_handles_missing_file(
    monkeypatch, autoresearch_src_root: Path, tmp_path: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    registry = import_module("autoresearch.candlemcstickface.registry")

    records = registry.load_registry(tmp_path / "missing.json")

    assert records == ()
