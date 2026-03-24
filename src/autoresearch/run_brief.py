from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunBrief:
    objective: str
    allowed_scope: tuple[str, ...]
    promotion_focus: str

    def __post_init__(self) -> None:
        if not self.objective.strip():
            raise ValueError("objective is required")
        if not self.allowed_scope:
            raise ValueError("allowed_scope is required")
        if not self.promotion_focus.strip():
            raise ValueError("promotion_focus is required")

    @classmethod
    def from_markdown(cls, path: Path) -> "RunBrief":
        text = path.read_text(encoding="utf-8")
        values: dict[str, str] = {}
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line.startswith("-") or ":" not in line:
                continue
            key, value = line[1:].split(":", maxsplit=1)
            values[key.strip().lower()] = value.strip()

        objective = values.get("objective", "")
        promotion_focus = values.get("promotion_focus", "")
        scope_raw = values.get("allowed_scope", "")
        allowed_scope = tuple(
            part.strip() for part in scope_raw.split(",") if part.strip()
        )
        return cls(
            objective=objective,
            allowed_scope=allowed_scope,
            promotion_focus=promotion_focus,
        )
