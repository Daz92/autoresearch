from __future__ import annotations

from dataclasses import dataclass

from .contracts import MetricBundle, PromotionDecision, PromotionState, SignalProposal
from .provenance import ensure_time_order
from .score import ScorePolicy


@dataclass(frozen=True)
class Judge:
    policy: ScorePolicy
    max_drawdown: float = 0.30
    max_turnover: float = 0.80
    max_cost_sensitivity: float = 0.60
    min_regime_stability: float = 0.40
    advance_threshold: float = 0.70
    hold_threshold: float = 0.55

    @classmethod
    def current(cls) -> "Judge":
        return cls(policy=ScorePolicy.current())

    def decide(
        self,
        *,
        metrics: MetricBundle,
        signal: SignalProposal | None,
        paper_consistency: bool,
    ) -> PromotionDecision:
        if signal is None:
            return PromotionDecision(
                state=PromotionState.INVALID,
                score=None,
                score_version=self.policy.version,
                reasons=("missing signal proposal",),
            )

        time_result = ensure_time_order(signal.time)
        if not time_result.is_valid:
            return PromotionDecision(
                state=PromotionState.INVALID,
                score=None,
                score_version=self.policy.version,
                reasons=time_result.errors,
            )

        rejection_reasons: list[str] = []
        if metrics.drawdown > self.max_drawdown:
            rejection_reasons.append("drawdown exceeds hard gate")
        if metrics.turnover > self.max_turnover:
            rejection_reasons.append("turnover exceeds hard gate")
        if metrics.cost_sensitivity > self.max_cost_sensitivity:
            rejection_reasons.append("cost sensitivity exceeds hard gate")
        if metrics.regime_stability < self.min_regime_stability:
            rejection_reasons.append("regime stability below hard gate")

        if rejection_reasons:
            return PromotionDecision(
                state=PromotionState.REJECT,
                score=self.policy.score(metrics),
                score_version=self.policy.version,
                reasons=tuple(rejection_reasons),
            )

        composite = self.policy.score(metrics)
        if composite >= self.advance_threshold and paper_consistency:
            return PromotionDecision(
                state=PromotionState.ADVANCE,
                score=composite,
                score_version=self.policy.version,
                reasons=("clears score threshold and paper consistency",),
            )
        if composite >= self.hold_threshold:
            return PromotionDecision(
                state=PromotionState.HOLD,
                score=composite,
                score_version=self.policy.version,
                reasons=("promising but requires additional paper validation",),
            )
        return PromotionDecision(
            state=PromotionState.REJECT,
            score=composite,
            score_version=self.policy.version,
            reasons=("composite score below hold threshold",),
        )
