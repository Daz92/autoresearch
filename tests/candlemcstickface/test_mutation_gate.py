from importlib import import_module
from pathlib import Path


def test_rejects_mutation_of_non_allowlisted_fields(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    mutation_gate = import_module("autoresearch.candlemcstickface.mutation_gate")

    proposal = {"changes": {"risk.max_daily_loss": 1000}}

    result = mutation_gate.check_mutation_eligibility(proposal)

    assert result.allowed is False
    assert result.reasons == ("rejected:field_not_allowlisted:risk.max_daily_loss",)
    assert result.eligible_fields == ()


def test_allows_allowlisted_screener_rules_fields(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    mutation_gate = import_module("autoresearch.candlemcstickface.mutation_gate")

    proposal = {
        "changes": {
            "screener_rules.rules.0.max_results": 15,
            "screener_rules.rules.1.min_market_cap": 1000000000,
        }
    }

    result = mutation_gate.check_mutation_eligibility(proposal)

    assert result.allowed is True
    assert result.reasons == ()
    assert result.eligible_fields == (
        "screener_rules.rules.0.max_results",
        "screener_rules.rules.1.min_market_cap",
    )


def test_rejects_mixed_allowed_and_non_allowlisted_fields(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    mutation_gate = import_module("autoresearch.candlemcstickface.mutation_gate")

    proposal = {
        "changes": {
            "screener_rules.rules.0.max_results": 15,
            "risk.max_daily_loss": 1000,
        }
    }

    result = mutation_gate.check_mutation_eligibility(proposal)

    assert result.allowed is False
    assert result.reasons == ("rejected:field_not_allowlisted:risk.max_daily_loss",)
    assert result.eligible_fields == ("screener_rules.rules.0.max_results",)


def test_rejects_missing_or_empty_changes(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    mutation_gate = import_module("autoresearch.candlemcstickface.mutation_gate")

    missing_result = mutation_gate.check_mutation_eligibility({})
    empty_result = mutation_gate.check_mutation_eligibility({"changes": {}})

    assert missing_result.allowed is False
    assert missing_result.reasons == ("invalid:changes_missing_or_not_mapping",)

    assert empty_result.allowed is False
    assert empty_result.reasons == ("invalid:no_changes_proposed",)


def test_rejects_unknown_allowlisted_path(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    mutation_gate = import_module("autoresearch.candlemcstickface.mutation_gate")

    proposal = {
        "changes": {
            "screener_rules.rules.0.unapproved_field": 5,
        }
    }

    result = mutation_gate.check_mutation_eligibility(proposal)

    assert result.allowed is False
    assert result.reasons == (
        "rejected:field_not_allowlisted_path:screener_rules.rules.0.unapproved_field",
    )


def test_rejects_rule_name_mutation(monkeypatch, autoresearch_src_root: Path) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    mutation_gate = import_module("autoresearch.candlemcstickface.mutation_gate")

    proposal = {
        "changes": {
            "screener_rules.rules.0.name": "Momentum v2",
        }
    }

    result = mutation_gate.check_mutation_eligibility(proposal)

    assert result.allowed is False
    assert result.reasons == (
        "rejected:field_not_allowlisted_path:screener_rules.rules.0.name",
    )


def test_rejects_noncanonical_path_even_with_string_leaf(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    mutation_gate = import_module("autoresearch.candlemcstickface.mutation_gate")

    proposal = {
        "changes": {
            "screener_rules.foo.bar.name": "momentum-v2",
        }
    }

    result = mutation_gate.check_mutation_eligibility(proposal)

    assert result.allowed is False
    assert result.reasons == (
        "rejected:field_not_allowlisted_path:screener_rules.foo.bar.name",
    )


def test_rejects_out_of_bounds_numeric_change(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    mutation_gate = import_module("autoresearch.candlemcstickface.mutation_gate")

    proposal = {
        "changes": {
            "screener_rules.rules.0.max_results": 0,
        }
    }

    result = mutation_gate.check_mutation_eligibility(proposal)

    assert result.allowed is False
    assert result.reasons == (
        "rejected:out_of_bounds:screener_rules.rules.0.max_results",
    )


def test_rejects_infeasible_price_range(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    mutation_gate = import_module("autoresearch.candlemcstickface.mutation_gate")

    proposal = {
        "changes": {
            "screener_rules.rules.0.min_price": 200.0,
            "screener_rules.rules.0.max_price": 100.0,
        }
    }

    result = mutation_gate.check_mutation_eligibility(proposal)

    assert result.allowed is False
    assert "rejected:infeasible:min_price_gt_max_price" in result.reasons


def test_rejects_infeasible_price_range_on_nonzero_rule_index(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    mutation_gate = import_module("autoresearch.candlemcstickface.mutation_gate")

    proposal = {
        "changes": {
            "screener_rules.rules.1.min_price": 210.0,
            "screener_rules.rules.1.max_price": 200.0,
        }
    }

    result = mutation_gate.check_mutation_eligibility(proposal)

    assert result.allowed is False
    assert "rejected:infeasible:min_price_gt_max_price" in result.reasons
