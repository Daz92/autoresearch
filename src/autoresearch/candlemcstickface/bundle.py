from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import cast


FROZEN_BUNDLE_CREATED_AT = "1970-01-01T00:00:00Z"


@dataclass(frozen=True)
class DeskCycleBundle:
    bundle_hash: str
    created_at: str
    payload: Mapping[str, object]
    payload_hash: str


def _freeze_value(value: object) -> object:
    if isinstance(value, Mapping):
        frozen_mapping = {str(key): _freeze_value(item) for key, item in value.items()}
        return MappingProxyType(frozen_mapping)
    if isinstance(value, list):
        return tuple(_freeze_value(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze_value(item) for item in value)
    return value


def _json_ready(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    return value


def _sha256_hex(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_bundle(
    payload: Mapping[str, object],
    *,
    created_at: str = FROZEN_BUNDLE_CREATED_AT,
) -> DeskCycleBundle:
    frozen_payload = cast(Mapping[str, object], _freeze_value(payload))
    json_payload = _json_ready(frozen_payload)

    payload_hash = _sha256_hex(json_payload)
    bundle_hash = _sha256_hex(
        {
            "created_at": created_at,
            "payload_hash": payload_hash,
        }
    )

    return DeskCycleBundle(
        bundle_hash=bundle_hash,
        created_at=created_at,
        payload=frozen_payload,
        payload_hash=payload_hash,
    )


__all__ = [
    "DeskCycleBundle",
    "FROZEN_BUNDLE_CREATED_AT",
    "build_bundle",
]
