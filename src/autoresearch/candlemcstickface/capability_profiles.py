from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

import yaml


@dataclass(frozen=True)
class CapabilityProfile:
    agent_id: str
    required_tools_by_mode: Mapping[str, tuple[str, ...]]
    fallback_order: tuple[str, ...] = ()
    disallowed_shortcuts: tuple[str, ...] = ()


def _coerce_string_list(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} must be a list of strings")
    return tuple(value)


def _coerce_required_tools(value: object) -> Mapping[str, tuple[str, ...]]:
    if not isinstance(value, dict):
        raise ValueError("required_tools_by_mode must be a mapping")

    tools_by_mode: dict[str, tuple[str, ...]] = {}
    for mode, tools in value.items():
        if not isinstance(mode, str) or not mode:
            raise ValueError("required_tools_by_mode keys must be non-empty strings")
        tools_by_mode[mode] = _coerce_string_list(
            tools, f"required_tools_by_mode.{mode}"
        )

    return MappingProxyType(tools_by_mode)


def _load_payload(path: str | Path) -> dict[str, object]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("capability profile payload must be a mapping")
    return payload


def load_capability_profiles(path: str | Path) -> Mapping[str, CapabilityProfile]:
    payload = _load_payload(path)
    agents = payload.get("agents")

    if not isinstance(agents, list):
        raise ValueError("capability profiles must define an agents list")

    profiles: dict[str, CapabilityProfile] = {}
    for raw_profile in agents:
        if not isinstance(raw_profile, dict):
            raise ValueError("each capability profile must be a mapping")

        agent_id = raw_profile.get("agent_id")
        if not isinstance(agent_id, str) or not agent_id:
            raise ValueError("capability profiles require a non-empty agent_id")
        if agent_id in profiles:
            raise ValueError(f"duplicate capability profile for agent_id={agent_id}")

        profiles[agent_id] = CapabilityProfile(
            agent_id=agent_id,
            required_tools_by_mode=_coerce_required_tools(
                raw_profile.get("required_tools_by_mode", {})
            ),
            fallback_order=_coerce_string_list(
                raw_profile.get("fallback_order", []), "fallback_order"
            ),
            disallowed_shortcuts=_coerce_string_list(
                raw_profile.get("disallowed_shortcuts", []),
                "disallowed_shortcuts",
            ),
        )

    return MappingProxyType(profiles)


__all__ = ["CapabilityProfile", "load_capability_profiles"]
