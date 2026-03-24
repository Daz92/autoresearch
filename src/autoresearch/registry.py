from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from .contracts import MetricBundle, PromotionState, parse_timestamp, utc_now


@dataclass(frozen=True)
class RegistryEntry:
    candidate_version: str
    configuration_summary: Mapping[str, Any]
    market_coverage: tuple[str, ...]
    metric_bundle: MetricBundle
    score_version: str
    promotion_state: PromotionState
    paper_results: Mapping[str, Any] = field(default_factory=dict)
    evaluation_artifacts: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.candidate_version:
            raise ValueError("candidate_version is required")
        if not self.score_version:
            raise ValueError("score_version is required")
        if not self.market_coverage:
            raise ValueError("market_coverage is required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_version": self.candidate_version,
            "configuration_summary": dict(self.configuration_summary),
            "market_coverage": list(self.market_coverage),
            "metric_bundle": {
                "return_pct": self.metric_bundle.return_pct,
                "drawdown": self.metric_bundle.drawdown,
                "hit_rate": self.metric_bundle.hit_rate,
                "turnover": self.metric_bundle.turnover,
                "cost_sensitivity": self.metric_bundle.cost_sensitivity,
                "regime_stability": self.metric_bundle.regime_stability,
                "metadata": dict(self.metric_bundle.metadata),
            },
            "score_version": self.score_version,
            "promotion_state": self.promotion_state.value,
            "paper_results": dict(self.paper_results),
            "evaluation_artifacts": list(self.evaluation_artifacts),
            "created_at": parse_timestamp(self.created_at).isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "RegistryEntry":
        metric_payload = data.get("metric_bundle", {})
        return cls(
            candidate_version=str(data["candidate_version"]),
            configuration_summary=dict(data.get("configuration_summary", {})),
            market_coverage=tuple(
                str(item) for item in data.get("market_coverage", [])
            ),
            metric_bundle=MetricBundle(
                return_pct=float(metric_payload.get("return_pct", 0.0)),
                drawdown=float(metric_payload.get("drawdown", 0.0)),
                hit_rate=float(metric_payload.get("hit_rate", 0.0)),
                turnover=float(metric_payload.get("turnover", 0.0)),
                cost_sensitivity=float(metric_payload.get("cost_sensitivity", 0.0)),
                regime_stability=float(metric_payload.get("regime_stability", 0.0)),
                metadata=dict(metric_payload.get("metadata", {})),
            ),
            score_version=str(data["score_version"]),
            promotion_state=PromotionState(str(data["promotion_state"])),
            paper_results=dict(data.get("paper_results", {})),
            evaluation_artifacts=tuple(
                str(item) for item in data.get("evaluation_artifacts", [])
            ),
            created_at=parse_timestamp(data.get("created_at", utc_now())),
        )


class Registry:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self._runs_file = self.root / "runs.jsonl"

    @property
    def runs_file(self) -> Path:
        return self._runs_file

    def record_run(self, entry: RegistryEntry | Mapping[str, Any]) -> RegistryEntry:
        typed_entry = (
            entry
            if isinstance(entry, RegistryEntry)
            else RegistryEntry.from_dict(entry)
        )
        payload = typed_entry.to_dict()
        with self._runs_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True))
            handle.write("\n")
        return typed_entry

    def list_runs(self) -> list[RegistryEntry]:
        if not self._runs_file.exists():
            return []
        entries: list[RegistryEntry] = []
        with self._runs_file.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped:
                    continue
                entries.append(RegistryEntry.from_dict(json.loads(stripped)))
        return entries
