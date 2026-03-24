from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from .contracts import Market, TimeProvenance, parse_timestamp


REQUIRED_TIME_FIELDS = ("market", "symbol", "as_of", "available_at", "provenance")


@dataclass(frozen=True)
class ProvenanceValidationResult:
    is_valid: bool
    errors: tuple[str, ...] = ()
    artifact: TimeProvenance | None = None


def ensure_time_order(
    artifact: Mapping[str, Any] | TimeProvenance,
) -> ProvenanceValidationResult:
    if isinstance(artifact, TimeProvenance):
        return _validate_typed(artifact)

    missing = [
        key
        for key in REQUIRED_TIME_FIELDS
        if key not in artifact or artifact[key] in (None, "", [])
    ]
    if missing:
        return ProvenanceValidationResult(
            is_valid=False,
            errors=(f"missing required provenance fields: {', '.join(missing)}",),
        )

    try:
        typed = TimeProvenance(
            market=Market(str(artifact["market"])),
            symbol=str(artifact["symbol"]),
            as_of=parse_timestamp(artifact["as_of"]),
            available_at=parse_timestamp(artifact["available_at"]),
            provenance=tuple(str(item) for item in artifact["provenance"]),
        )
    except (TypeError, ValueError) as exc:
        return ProvenanceValidationResult(
            is_valid=False, errors=(f"invalid provenance format: {exc}",)
        )

    return _validate_typed(typed)


def _validate_typed(artifact: TimeProvenance) -> ProvenanceValidationResult:
    errors: list[str] = []
    if artifact.available_at < artifact.as_of:
        errors.append("available_at cannot be earlier than as_of")
    if not artifact.provenance:
        errors.append("provenance must be non-empty")

    return ProvenanceValidationResult(
        is_valid=not errors,
        errors=tuple(errors),
        artifact=artifact if not errors else None,
    )


def is_fresh_enough(
    *, now: datetime, available_at: datetime, max_age_seconds: int
) -> bool:
    normalized_now = parse_timestamp(now)
    normalized_available = parse_timestamp(available_at)
    age_seconds = (normalized_now - normalized_available).total_seconds()
    return age_seconds <= max_age_seconds
