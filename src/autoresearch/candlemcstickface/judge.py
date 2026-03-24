from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .contracts import PromotionOutcome


MIN_PARTICIPATION_TRADES = 1
JudgeOutcome = PromotionOutcome


@dataclass(frozen=True)
class JudgeResult:
    outcome: PromotionOutcome
    reasons: tuple[str, ...]
    score_delta: float


def _extract_numeric(
    payload: Mapping[str, object],
    key: str,
) -> float | None:
    value = payload.get(key)
    if isinstance(value, (int, float)):
        return float(value)
    return None


def judge_candidate(
    *,
    baseline: Mapping[str, object],
    mutant: Mapping[str, object],
    holdout: Mapping[str, object] | None,
) -> JudgeResult:
    if holdout is None:
        return JudgeResult(
            outcome=PromotionOutcome.INVALID,
            reasons=("invalid:holdout_missing",),
            score_delta=0.0,
        )

    baseline_pnl = _extract_numeric(baseline, "pnl")
    mutant_pnl = _extract_numeric(mutant, "pnl")
    holdout_pnl = _extract_numeric(holdout, "pnl")
    if baseline_pnl is None or mutant_pnl is None or holdout_pnl is None:
        return JudgeResult(
            outcome=PromotionOutcome.INVALID,
            reasons=("invalid:missing_pnl",),
            score_delta=0.0,
        )

    baseline_drawdown = _extract_numeric(baseline, "drawdown")
    mutant_drawdown = _extract_numeric(mutant, "drawdown")
    holdout_drawdown = _extract_numeric(holdout, "drawdown")
    if baseline_drawdown is None or mutant_drawdown is None or holdout_drawdown is None:
        return JudgeResult(
            outcome=PromotionOutcome.INVALID,
            reasons=("invalid:missing_drawdown",),
            score_delta=0.0,
        )

    baseline_trades = _extract_numeric(baseline, "trades")
    mutant_trades = _extract_numeric(mutant, "trades")
    holdout_trades = _extract_numeric(holdout, "trades")
    if baseline_trades is None or mutant_trades is None or holdout_trades is None:
        return JudgeResult(
            outcome=PromotionOutcome.INVALID,
            reasons=("invalid:missing_participation",),
            score_delta=0.0,
        )

    if mutant_trades < MIN_PARTICIPATION_TRADES:
        return JudgeResult(
            outcome=PromotionOutcome.REVERT,
            reasons=("revert:insufficient_participation",),
            score_delta=mutant_pnl - baseline_pnl,
        )

    if mutant_drawdown > baseline_drawdown:
        return JudgeResult(
            outcome=PromotionOutcome.REVERT,
            reasons=("revert:drawdown_worse_than_baseline",),
            score_delta=mutant_pnl - baseline_pnl,
        )

    if holdout_drawdown > baseline_drawdown:
        return JudgeResult(
            outcome=PromotionOutcome.HOLD,
            reasons=("hold:holdout_drawdown_not_confirmed",),
            score_delta=mutant_pnl - baseline_pnl,
        )

    if holdout_pnl <= baseline_pnl:
        return JudgeResult(
            outcome=PromotionOutcome.HOLD,
            reasons=("hold:holdout_pnl_not_confirmed",),
            score_delta=mutant_pnl - baseline_pnl,
        )

    if mutant_pnl <= baseline_pnl:
        return JudgeResult(
            outcome=PromotionOutcome.REVERT,
            reasons=("revert:pnl_not_improved",),
            score_delta=mutant_pnl - baseline_pnl,
        )

    return JudgeResult(
        outcome=PromotionOutcome.PROMOTE,
        reasons=(),
        score_delta=mutant_pnl - baseline_pnl,
    )


__all__ = [
    "JudgeOutcome",
    "JudgeResult",
    "MIN_PARTICIPATION_TRADES",
    "judge_candidate",
]
