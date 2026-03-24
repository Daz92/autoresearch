from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .bundle import DeskCycleBundle, build_bundle


@dataclass(frozen=True)
class ReplayResult:
    replay_hash: str
    decision: str
    score: float


def replay_bundle(
    bundle: DeskCycleBundle,
    *,
    candidate_rules: Mapping[str, object],
) -> ReplayResult:
    decision = "hold"
    score = 0.0

    if candidate_rules:
        decision = "evaluate"
        score += 1.0

    market_path = bundle.payload.get("market_path")
    if isinstance(market_path, Mapping):
        closes = market_path.get("closes")
        if isinstance(closes, tuple) and closes:
            numeric = [value for value in closes if isinstance(value, (int, float))]
            if numeric:
                score += float(numeric[-1] - numeric[0])

    replay_hash = bundle.bundle_hash
    return ReplayResult(replay_hash=replay_hash, decision=decision, score=score)


def replay_payload(
    payload: Mapping[str, object],
    *,
    candidate_rules: Mapping[str, object],
) -> ReplayResult:
    bundle = build_bundle(payload)
    return replay_bundle(bundle, candidate_rules=candidate_rules)


__all__ = [
    "ReplayResult",
    "replay_bundle",
    "replay_payload",
]
