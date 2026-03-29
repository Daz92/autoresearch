from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from .contracts import PromotionOutcome


@dataclass(frozen=True)
class RegistryRecord:
    experiment_id: str
    created_at: str
    bundle_hash: str
    outcome: PromotionOutcome
    score_delta: float
    details: Mapping[str, object]


def _compute_experiment_id(payload: Mapping[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def _write_json_atomically(path: Path, payload: list[dict[str, object]]) -> None:
    temp_path = path.with_suffix(path.suffix + ".tmp")
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    with temp_path.open("w", encoding="utf-8") as handle:
        handle.write(serialized)
        handle.flush()
    temp_path.replace(path)


def append_registry_record(
    registry_path: str | Path,
    *,
    bundle_hash: str,
    outcome: PromotionOutcome,
    score_delta: float,
    details: Mapping[str, object],
    created_at: str | None = None,
) -> RegistryRecord:
    now = created_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    identity_payload = {
        "bundle_hash": bundle_hash,
        "created_at": now,
        "details": details,
        "outcome": outcome.value,
        "score_delta": score_delta,
    }
    experiment_id = _compute_experiment_id(identity_payload)

    record = {
        "experiment_id": experiment_id,
        "created_at": now,
        "bundle_hash": bundle_hash,
        "outcome": outcome.value,
        "score_delta": score_delta,
        "details": details,
    }

    path = Path(registry_path)
    existing: list[dict[str, object]]
    if path.exists():
        parsed = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(parsed, list):
            raise ValueError("registry file must be a JSON list")
        existing = []
        for item in parsed:
            if not isinstance(item, dict):
                raise ValueError("registry list entries must be JSON objects")
            existing.append(item)
    else:
        existing = []

    existing.append(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_json_atomically(path, existing)

    return RegistryRecord(
        experiment_id=experiment_id,
        created_at=now,
        bundle_hash=bundle_hash,
        outcome=outcome,
        score_delta=score_delta,
        details=details,
    )


def load_registry(registry_path: str | Path) -> tuple[RegistryRecord, ...]:
    path = Path(registry_path)
    if not path.exists():
        return ()

    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, list):
        raise ValueError("registry file must be a JSON list")

    records: list[RegistryRecord] = []
    for entry in parsed:
        if not isinstance(entry, dict):
            raise ValueError("registry list entries must be JSON objects")
        records.append(
            RegistryRecord(
                experiment_id=str(entry["experiment_id"]),
                created_at=str(entry["created_at"]),
                bundle_hash=str(entry["bundle_hash"]),
                outcome=PromotionOutcome(str(entry["outcome"])),
                score_delta=float(entry["score_delta"]),
                details=dict(entry.get("details", {})),
            )
        )
    return tuple(records)


__all__ = [
    "RegistryRecord",
    "append_registry_record",
    "load_registry",
]
