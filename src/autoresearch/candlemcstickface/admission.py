from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

FRESHNESS_WINDOW_SECONDS = 300


@dataclass(frozen=True)
class AdmissionResult:
    status: str
    reasons: tuple[str, ...]
    quality_score: float


def _parse_iso8601(
    value: object, field_name: str
) -> tuple[datetime | None, str | None]:
    if not isinstance(value, str):
        return None, f"invalid:{field_name}:not_string"

    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized), None
    except ValueError:
        return None, f"invalid:{field_name}:bad_timestamp"


def _missing_fields(
    payload: dict[str, object], required: tuple[str, ...]
) -> tuple[str, ...]:
    missing: list[str] = []
    for key in required:
        if key not in payload or payload[key] in (None, ""):
            missing.append(f"missing:{key}")
    return tuple(missing)


def admit_watcher_payload(payload: dict[str, object]) -> AdmissionResult:
    required = (
        "session_id",
        "generated_at",
        "agent",
        "asset",
        "price",
        "price_timestamp",
    )
    reasons = _missing_fields(payload, required)
    if reasons:
        return AdmissionResult(status="invalid", reasons=reasons, quality_score=0.0)

    if payload.get("agent") != "watcher":
        return AdmissionResult(
            status="invalid",
            reasons=("inconsistent:agent_mismatch",),
            quality_score=0.0,
        )

    if not isinstance(payload.get("price"), (int, float)):
        return AdmissionResult(
            status="invalid",
            reasons=("invalid:price:not_numeric",),
            quality_score=0.0,
        )

    generated_at, generated_error = _parse_iso8601(
        payload.get("generated_at"), "generated_at"
    )
    if generated_error:
        return AdmissionResult(
            status="invalid", reasons=(generated_error,), quality_score=0.0
        )

    price_at, price_error = _parse_iso8601(
        payload.get("price_timestamp"), "price_timestamp"
    )
    if price_error:
        return AdmissionResult(
            status="invalid", reasons=(price_error,), quality_score=0.0
        )

    assert generated_at is not None
    assert price_at is not None

    age_seconds = (generated_at - price_at).total_seconds()
    if age_seconds < 0:
        return AdmissionResult(
            status="invalid",
            reasons=("inconsistent:generated_before_price",),
            quality_score=0.0,
        )

    if "alerts" not in payload:
        return AdmissionResult(
            status="insufficient",
            reasons=("insufficient:alerts_missing",),
            quality_score=0.25,
        )

    alerts = payload.get("alerts")
    if not isinstance(alerts, list) or any(
        not isinstance(item, str) for item in alerts
    ):
        return AdmissionResult(
            status="invalid",
            reasons=("invalid:alerts:not_string_list",),
            quality_score=0.0,
        )

    if age_seconds > FRESHNESS_WINDOW_SECONDS:
        return AdmissionResult(
            status="degraded",
            reasons=("freshness:stale_price_data",),
            quality_score=0.5,
        )

    return AdmissionResult(status="complete", reasons=(), quality_score=1.0)


__all__ = ["AdmissionResult", "admit_watcher_payload"]
