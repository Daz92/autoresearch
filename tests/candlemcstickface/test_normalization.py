from importlib import import_module
from pathlib import Path


def test_normalizes_matching_preset_names_to_bounded_changes(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    normalization = import_module("autoresearch.candlemcstickface.normalization")

    proposal = {
        "proposal_id": "strategist-1",
        "generated_at": "2026-03-29T12:00:00Z",
        "agent": "market-strategist",
        "sources": [],
        "presets": [
            {
                "name": "Momentum (medium-term trend)",
                "rationale": "Tighten liquidity floor.",
                "min_market_cap": 3000000000,
                "max_results": 12,
                "conditions": [
                    {"type": "price_change", "period": "60d", "min_pct": 12}
                ],
            }
        ],
    }
    screener_rules = {
        "rules": [
            {
                "name": "Momentum (medium-term trend)",
                "rationale": "Base rationale.",
                "conditions": [
                    {"type": "price_change", "period": "60d", "min_pct": 12}
                ],
                "min_market_cap": 2000000000,
                "max_results": 15,
            }
        ]
    }

    result = normalization.normalize_market_strategist_proposal(
        proposal, screener_rules
    )

    assert result["changes"] == {
        "screener_rules.rules.0.rationale": "Tighten liquidity floor.",
        "screener_rules.rules.0.min_market_cap": 3000000000,
        "screener_rules.rules.0.max_results": 12,
    }


def test_rejects_condition_changes_for_v1_mutation_surface(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    normalization = import_module("autoresearch.candlemcstickface.normalization")

    proposal = {
        "proposal_id": "strategist-2",
        "generated_at": "2026-03-29T12:00:00Z",
        "agent": "market-strategist",
        "sources": [],
        "presets": [
            {
                "name": "Momentum (medium-term trend)",
                "rationale": "Base rationale.",
                "min_market_cap": 2000000000,
                "max_results": 15,
                "conditions": [{"type": "price_change", "period": "20d", "min_pct": 9}],
            }
        ],
    }
    screener_rules = {
        "rules": [
            {
                "name": "Momentum (medium-term trend)",
                "rationale": "Base rationale.",
                "conditions": [
                    {"type": "price_change", "period": "60d", "min_pct": 12}
                ],
                "min_market_cap": 2000000000,
                "max_results": 15,
            }
        ]
    }

    try:
        normalization.normalize_market_strategist_proposal(proposal, screener_rules)
    except ValueError as exc:
        assert str(exc) == "conditions_not_mutable:Momentum (medium-term trend)"
    else:
        raise AssertionError("expected ValueError")


def test_rejects_duplicate_canonical_rule_names(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    normalization = import_module("autoresearch.candlemcstickface.normalization")

    proposal = {
        "proposal_id": "strategist-3",
        "generated_at": "2026-03-29T12:00:00Z",
        "agent": "market-strategist",
        "sources": [],
        "presets": [
            {
                "name": "Momentum (medium-term trend)",
                "rationale": "Adjusted rationale.",
                "conditions": [
                    {"type": "price_change", "period": "60d", "min_pct": 12}
                ],
                "min_market_cap": 2000000000,
                "max_results": 15,
            }
        ],
    }
    screener_rules = {
        "rules": [
            {
                "name": "Momentum (medium-term trend)",
                "rationale": "Base rationale.",
                "conditions": [
                    {"type": "price_change", "period": "60d", "min_pct": 12}
                ],
                "min_market_cap": 2000000000,
                "max_results": 15,
            },
            {
                "name": "Momentum (medium-term trend)",
                "rationale": "Duplicate rule.",
                "conditions": [
                    {"type": "price_change", "period": "60d", "min_pct": 12}
                ],
                "min_market_cap": 2000000000,
                "max_results": 15,
            },
        ]
    }

    try:
        normalization.normalize_market_strategist_proposal(proposal, screener_rules)
    except ValueError as exc:
        assert str(exc) == "duplicate_rule_name:Momentum (medium-term trend)"
    else:
        raise AssertionError("expected ValueError")
