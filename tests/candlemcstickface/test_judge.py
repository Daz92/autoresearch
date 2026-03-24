from importlib import import_module
from pathlib import Path


def test_candidate_is_invalid_when_holdout_missing(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    judge = import_module("autoresearch.candlemcstickface.judge")

    result = judge.judge_candidate(
        baseline={"pnl": 1.0, "drawdown": 0.2, "trades": 5},
        mutant={"pnl": 2.0, "drawdown": 0.1, "trades": 5},
        holdout=None,
    )

    assert result.outcome.value == "invalid"
    assert result.reasons == ("invalid:holdout_missing",)


def test_promotes_when_mutant_and_holdout_clear_gates(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    judge = import_module("autoresearch.candlemcstickface.judge")

    result = judge.judge_candidate(
        baseline={"pnl": 5.0, "drawdown": 0.2, "trades": 4},
        mutant={"pnl": 6.5, "drawdown": 0.15, "trades": 6},
        holdout={"pnl": 5.5, "drawdown": 0.15, "trades": 3},
    )

    assert result.outcome.value == "promote"
    assert result.reasons == ()


def test_holds_when_holdout_not_confirmed(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    judge = import_module("autoresearch.candlemcstickface.judge")

    result = judge.judge_candidate(
        baseline={"pnl": 5.0, "drawdown": 0.2, "trades": 4},
        mutant={"pnl": 6.0, "drawdown": 0.1, "trades": 4},
        holdout={"pnl": 4.5, "drawdown": 0.1, "trades": 2},
    )

    assert result.outcome.value == "hold"
    assert result.reasons == ("hold:holdout_pnl_not_confirmed",)


def test_reverts_when_drawdown_worse_than_baseline(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    judge = import_module("autoresearch.candlemcstickface.judge")

    result = judge.judge_candidate(
        baseline={"pnl": 5.0, "drawdown": 0.2, "trades": 4},
        mutant={"pnl": 6.0, "drawdown": 0.3, "trades": 4},
        holdout={"pnl": 5.5, "drawdown": 0.15, "trades": 2},
    )

    assert result.outcome.value == "revert"
    assert result.reasons == ("revert:drawdown_worse_than_baseline",)
