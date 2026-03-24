from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import re

ALLOWLIST_PREFIXES = ("screener_rules.",)
ALLOWED_PATH_PATTERN = re.compile(
    r"^screener_rules\.rules\.(\d+)\.([a-zA-Z_][a-zA-Z0-9_]*)$"
)

ALLOWED_RULE_FIELDS = {
    "max_results",
    "min_market_cap",
    "min_price",
    "max_price",
    "name",
    "rationale",
}

NUMERIC_BOUNDS = {
    "max_results": (1, 500),
    "min_market_cap": (0, 10_000_000_000_000),
    "min_price": (0, 1_000_000),
    "max_price": (0, 1_000_000),
}


@dataclass(frozen=True)
class MutationEligibilityResult:
    allowed: bool
    reasons: tuple[str, ...]
    eligible_fields: tuple[str, ...] = ()


def _normalize_changes(proposal: Mapping[str, object]) -> Mapping[str, object] | None:
    changes = proposal.get("changes")
    if not isinstance(changes, Mapping):
        return None
    return changes


def _extract_leaf_field(field_name: str) -> str:
    return field_name.rsplit(".", 1)[-1]


def _parse_allowed_path(field_name: str) -> tuple[int, str] | None:
    match = ALLOWED_PATH_PATTERN.fullmatch(field_name)
    if match is None:
        return None
    return int(match.group(1)), match.group(2)


def _check_field_allowed(field_name: str) -> str | None:
    parsed = _parse_allowed_path(field_name)
    if parsed is None:
        return f"rejected:field_not_allowlisted_path:{field_name}"

    _, leaf = parsed
    if leaf not in ALLOWED_RULE_FIELDS:
        return f"rejected:field_not_allowlisted_path:{field_name}"
    return None


def _check_value_bounds(field_name: str, value: object) -> str | None:
    leaf = _extract_leaf_field(field_name)

    if leaf in {"name", "rationale"}:
        if not isinstance(value, str) or not value.strip():
            return f"rejected:invalid_type_or_empty:{field_name}"
        return None

    lower, upper = NUMERIC_BOUNDS[leaf]
    if not isinstance(value, (int, float)):
        return f"rejected:invalid_numeric_type:{field_name}"
    if value < lower or value > upper:
        return f"rejected:out_of_bounds:{field_name}"
    return None


def _check_value_feasibility(changes: Mapping[str, object]) -> str | None:
    by_rule_index: dict[int, dict[str, object]] = {}
    for field_name, value in changes.items():
        if not isinstance(field_name, str):
            continue
        parsed = _parse_allowed_path(field_name)
        if parsed is None:
            continue
        rule_index, leaf = parsed
        by_rule_index.setdefault(rule_index, {})[leaf] = value

    for fields in by_rule_index.values():
        min_price = fields.get("min_price")
        max_price = fields.get("max_price")
        if isinstance(min_price, (int, float)) and isinstance(max_price, (int, float)):
            if min_price > max_price:
                return "rejected:infeasible:min_price_gt_max_price"
    return None


def check_mutation_eligibility(
    proposal: Mapping[str, object],
) -> MutationEligibilityResult:
    changes = _normalize_changes(proposal)
    if changes is None:
        return MutationEligibilityResult(
            allowed=False,
            reasons=("invalid:changes_missing_or_not_mapping",),
        )

    if not changes:
        return MutationEligibilityResult(
            allowed=False,
            reasons=("invalid:no_changes_proposed",),
        )

    rejection_reasons: list[str] = []
    eligible_fields: list[str] = []
    for field_name, value in changes.items():
        if not isinstance(field_name, str) or not field_name:
            rejection_reasons.append("rejected:field_not_allowlisted:<invalid-field>")
            continue

        if not field_name.startswith(ALLOWLIST_PREFIXES):
            rejection_reasons.append(f"rejected:field_not_allowlisted:{field_name}")
            continue

        disallow_reason = _check_field_allowed(field_name)
        if disallow_reason:
            rejection_reasons.append(disallow_reason)
            continue

        bounds_reason = _check_value_bounds(field_name, value)
        if bounds_reason:
            rejection_reasons.append(bounds_reason)
            continue

        eligible_fields.append(field_name)

    feasibility_reason = _check_value_feasibility(changes)
    if feasibility_reason:
        rejection_reasons.append(feasibility_reason)

    if rejection_reasons:
        return MutationEligibilityResult(
            allowed=False,
            reasons=tuple(rejection_reasons),
            eligible_fields=tuple(eligible_fields),
        )

    return MutationEligibilityResult(
        allowed=True,
        reasons=(),
        eligible_fields=tuple(eligible_fields),
    )


__all__ = [
    "ALLOWED_PATH_PATTERN",
    "ALLOWED_RULE_FIELDS",
    "ALLOWLIST_PREFIXES",
    "MutationEligibilityResult",
    "NUMERIC_BOUNDS",
    "check_mutation_eligibility",
]
