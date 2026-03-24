from __future__ import annotations

from dataclasses import dataclass

from .contracts import MetricBundle


@dataclass(frozen=True)
class ScorePolicy:
    version: str
    weight_return_pct: float
    weight_drawdown: float
    weight_hit_rate: float
    weight_turnover: float
    weight_cost_sensitivity: float
    weight_regime_stability: float

    @classmethod
    def current(cls) -> "ScorePolicy":
        return cls(
            version="v1",
            weight_return_pct=0.30,
            weight_drawdown=0.20,
            weight_hit_rate=0.20,
            weight_turnover=0.10,
            weight_cost_sensitivity=0.10,
            weight_regime_stability=0.10,
        )

    def score(self, metrics: MetricBundle) -> float:
        return_component = self._clamp_0_1((metrics.return_pct + 1.0) / 2.0)
        drawdown_component = 1.0 - metrics.drawdown
        turnover_component = 1.0 - metrics.turnover
        cost_component = 1.0 - metrics.cost_sensitivity

        composite = (
            return_component * self.weight_return_pct
            + drawdown_component * self.weight_drawdown
            + metrics.hit_rate * self.weight_hit_rate
            + turnover_component * self.weight_turnover
            + cost_component * self.weight_cost_sensitivity
            + metrics.regime_stability * self.weight_regime_stability
        )
        return round(self._clamp_0_1(composite), 6)

    @staticmethod
    def _clamp_0_1(value: float) -> float:
        return max(0.0, min(1.0, value))
