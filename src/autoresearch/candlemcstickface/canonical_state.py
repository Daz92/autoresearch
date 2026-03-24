from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class SchemaVersion:
    version: int
    schema_hash: str
    owners: Mapping[str, str]


def _coerce_scalar(raw_value: str) -> int | float | str:
    value = raw_value.strip()
    if not value:
        return ""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def _parse_simple_yaml(text: str) -> dict[str, object]:
    data: dict[str, object] = {}
    current_mapping: dict[str, object] | None = None

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(" "))
        content = line.lstrip(" ")
        if ":" not in content:
            raise ValueError(f"Invalid schema metadata line: {raw_line!r}")

        key, raw_value = content.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()

        if indent == 0:
            if not raw_value:
                nested: dict[str, object] = {}
                data[key] = nested
                current_mapping = nested
            else:
                data[key] = _coerce_scalar(raw_value)
                current_mapping = None
            continue

        if indent == 2 and current_mapping is not None:
            current_mapping[key] = _coerce_scalar(raw_value)
            continue

        raise ValueError(f"Unsupported schema metadata indentation: {raw_line!r}")

    return data


def compute_schema_hash(version: int, owners: dict[str, str]) -> str:
    canonical_payload = {
        "owners": {key: owners[key] for key in sorted(owners)},
        "version": version,
    }
    encoded = json.dumps(
        canonical_payload, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_schema_version(path: str | Path) -> SchemaVersion:
    metadata = _parse_simple_yaml(Path(path).read_text(encoding="utf-8"))
    version = metadata.get("version")
    if not isinstance(version, int):
        raise ValueError("schema-version.yaml must declare an integer version")

    raw_owners = metadata.get("owners", {})
    if not isinstance(raw_owners, dict):
        raise ValueError("schema-version.yaml owners must be a mapping")

    owners = {str(key): str(value) for key, value in raw_owners.items()}
    computed_hash = compute_schema_hash(version, owners)
    declared_hash = metadata.get("schema_hash")

    if declared_hash in (None, "", "pending-computed"):
        schema_hash = computed_hash
    else:
        if str(declared_hash) != computed_hash:
            raise ValueError(
                "schema-version.yaml schema_hash does not match canonical payload"
            )
        schema_hash = computed_hash

    return SchemaVersion(
        version=version,
        schema_hash=schema_hash,
        owners=MappingProxyType(dict(owners)),
    )


__all__ = ["SchemaVersion", "compute_schema_hash", "load_schema_version"]
