from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class AutoresearchResumeState:
    proposal_id: str
    source_agent: str
    source_session_id: str | None
    stage: str
    outcome: str | None
    bundle_hash: str | None
    experiment_id: str | None
    next_action: str


def load_resume_state(path: str | Path) -> AutoresearchResumeState | None:
    file_path = Path(path)
    if not file_path.exists():
        return None
    payload = json.loads(file_path.read_text(encoding="utf-8"))
    return AutoresearchResumeState(**payload)


def write_resume_state(path: str | Path, state: AutoresearchResumeState) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    serialized = json.dumps(asdict(state), indent=2, sort_keys=True) + "\n"
    with temp_path.open("w", encoding="utf-8") as handle:
        handle.write(serialized)
        handle.flush()
    temp_path.replace(file_path)


__all__ = [
    "AutoresearchResumeState",
    "load_resume_state",
    "write_resume_state",
]
