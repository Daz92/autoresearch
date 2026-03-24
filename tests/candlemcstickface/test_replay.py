from importlib import import_module
from pathlib import Path


def test_replay_is_stable_for_same_bundle_and_rules(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    bundle_mod = import_module("autoresearch.candlemcstickface.bundle")
    replay_mod = import_module("autoresearch.candlemcstickface.replay")

    payload = {
        "market_path": {"closes": [100.0, 103.0, 105.5]},
        "decision": {"asset": "SOL/USD"},
    }
    rules = {"screener_rules.rules.0.max_results": 20}

    bundle = bundle_mod.build_bundle(payload)
    first = replay_mod.replay_bundle(bundle, candidate_rules=rules)
    second = replay_mod.replay_bundle(bundle, candidate_rules=rules)

    assert first == second


def test_replay_payload_matches_bundle_replay(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    bundle_mod = import_module("autoresearch.candlemcstickface.bundle")
    replay_mod = import_module("autoresearch.candlemcstickface.replay")

    payload = {
        "market_path": {"closes": [10.0, 9.5, 11.0]},
        "decision": {"asset": "BTC/USD"},
    }
    rules = {"screener_rules.rules.0.min_price": 8.0}

    from_payload = replay_mod.replay_payload(payload, candidate_rules=rules)
    from_bundle = replay_mod.replay_bundle(
        bundle_mod.build_bundle(payload),
        candidate_rules=rules,
    )

    assert from_payload == from_bundle


def test_replay_decision_hold_when_rules_empty(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    bundle_mod = import_module("autoresearch.candlemcstickface.bundle")
    replay_mod = import_module("autoresearch.candlemcstickface.replay")

    payload = {
        "market_path": {"closes": [1.0, 2.0]},
    }

    result = replay_mod.replay_bundle(
        bundle_mod.build_bundle(payload),
        candidate_rules={},
    )

    assert result.decision == "hold"
    assert result.score == 1.0
