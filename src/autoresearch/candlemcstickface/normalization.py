from __future__ import annotations

from collections.abc import Mapping, Sequence

MUTABLE_PRESET_FIELDS = ("rationale", "min_market_cap", "max_results")


def normalize_market_strategist_proposal(
    proposal: Mapping[str, object],
    screener_rules: Mapping[str, object],
) -> dict[str, object]:
    if proposal.get("agent") != "market-strategist":
        raise ValueError("invalid_agent")

    raw_rules = screener_rules.get("rules")
    if not isinstance(raw_rules, list):
        raise ValueError("invalid_screener_rules")

    by_name: dict[str, tuple[int, Mapping[str, object]]] = {}
    for idx, rule in enumerate(raw_rules):
        if not isinstance(rule, Mapping):
            continue
        name = rule.get("name")
        if not isinstance(name, str) or not name:
            continue
        if name in by_name:
            raise ValueError(f"duplicate_rule_name:{name}")
        by_name[name] = (idx, rule)

    raw_presets = proposal.get("presets")
    if not isinstance(raw_presets, Sequence) or isinstance(raw_presets, (str, bytes)):
        raise ValueError("invalid_presets")

    changes: dict[str, object] = {}
    for preset in raw_presets:
        if not isinstance(preset, Mapping):
            raise ValueError("invalid_preset")
        preset_name = preset.get("name")
        if not isinstance(preset_name, str) or preset_name not in by_name:
            raise ValueError(f"unknown_rule:{preset_name}")

        rule_index, current_rule = by_name[preset_name]
        if preset.get("conditions") != current_rule.get("conditions"):
            raise ValueError(f"conditions_not_mutable:{preset_name}")

        for field in MUTABLE_PRESET_FIELDS:
            if field in preset and preset[field] != current_rule.get(field):
                changes[f"screener_rules.rules.{rule_index}.{field}"] = preset[field]

    if not changes:
        raise ValueError("no_mutable_changes")

    raw_sources = proposal.get("sources", [])
    sources: list[object]
    if isinstance(raw_sources, Sequence) and not isinstance(raw_sources, (str, bytes)):
        sources = list(raw_sources)
    else:
        sources = []

    return {
        "proposal_id": proposal["proposal_id"],
        "generated_at": proposal["generated_at"],
        "agent": "market-strategist",
        "sources": sources,
        "changes": changes,
    }


__all__ = ["MUTABLE_PRESET_FIELDS", "normalize_market_strategist_proposal"]
