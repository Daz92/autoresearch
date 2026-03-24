from pathlib import Path
from importlib import import_module


def test_eval_package_imports(eval_package) -> None:
    assert eval_package.__name__ == "autoresearch.candlemcstickface"
    assert eval_package.__package__ == "autoresearch.candlemcstickface"


def test_eval_package_uses_src_scaffold(
    eval_package, autoresearch_src_root: Path
) -> None:
    assert (
        Path(eval_package.__file__).resolve()
        == autoresearch_src_root / "autoresearch" / "candlemcstickface" / "__init__.py"
    )


def test_promotion_outcome_enum_contains_invalid(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    contracts = import_module("autoresearch.candlemcstickface.contracts")

    assert contracts.PromotionOutcome.INVALID.value == "invalid"


def test_watcher_contract_preserves_required_fields(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    contracts = import_module("autoresearch.candlemcstickface.contracts")

    contract = contracts.WatcherContract(
        session_id="watcher-abc-123",
        generated_at="2026-03-24T12:00:00Z",
        agent="watcher",
        asset="SOL/USD",
        price=123.45,
        price_timestamp="2026-03-24T11:59:00Z",
        alerts=("volume_spike", "approaching_resistance"),
    )

    assert contract.agent == "watcher"
    assert contract.asset == "SOL/USD"
    assert contract.alerts == ("volume_spike", "approaching_resistance")
