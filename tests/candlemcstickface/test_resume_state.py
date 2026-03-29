from importlib import import_module
from pathlib import Path


def test_write_and_load_resume_state_round_trip(
    monkeypatch, autoresearch_src_root: Path, tmp_path: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    resume_state = import_module("autoresearch.candlemcstickface.resume_state")

    path = tmp_path / "autoresearch-resume-state.json"
    state = resume_state.AutoresearchResumeState(
        proposal_id="strategist-1",
        source_agent="market-strategist",
        source_session_id="agent:market-strategist:subagent:123",
        stage="evaluated",
        outcome="hold",
        bundle_hash="bundle-abc",
        experiment_id="exp-123",
        next_action="await_new_proposal",
    )

    resume_state.write_resume_state(path, state)
    loaded = resume_state.load_resume_state(path)

    assert loaded == state


def test_load_resume_state_returns_none_when_file_missing(
    monkeypatch, autoresearch_src_root: Path, tmp_path: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    resume_state = import_module("autoresearch.candlemcstickface.resume_state")

    assert resume_state.load_resume_state(tmp_path / "missing.json") is None


def test_write_resume_state_replaces_temp_file_atomically(
    monkeypatch, autoresearch_src_root: Path, tmp_path: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    resume_state = import_module("autoresearch.candlemcstickface.resume_state")

    path = tmp_path / "autoresearch-resume-state.json"
    state = resume_state.AutoresearchResumeState(
        proposal_id="strategist-2",
        source_agent="market-strategist",
        source_session_id=None,
        stage="evaluated",
        outcome="promote",
        bundle_hash="bundle-def",
        experiment_id="exp-456",
        next_action="promote_rules",
    )

    resume_state.write_resume_state(path, state)

    assert path.read_text(encoding="utf-8").endswith("\n")
    assert list(tmp_path.glob("autoresearch-resume-state.json.tmp")) == []
