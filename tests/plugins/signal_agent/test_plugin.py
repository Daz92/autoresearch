from pathlib import Path


def _load(module_name: str):
    return __import__(module_name, fromlist=["*"])


def test_signal_plugin_requires_generate_signal() -> None:
    SignalPlugin = _load("autoresearch.plugins.base").SignalPlugin

    assert hasattr(SignalPlugin, "generate_signal")
    assert not hasattr(SignalPlugin, "score")


def test_run_brief_requires_objective_and_scope() -> None:
    RunBrief = _load("autoresearch.run_brief").RunBrief

    brief = RunBrief(
        objective="improve crypto breakout signals",
        allowed_scope=("signal-agent",),
        promotion_focus="paper_consistency",
    )
    assert brief.objective == "improve crypto breakout signals"


def test_run_brief_from_markdown(tmp_path: Path) -> None:
    RunBrief = _load("autoresearch.run_brief").RunBrief

    path = tmp_path / "brief.md"
    path.write_text(
        "\n".join(
            [
                "- objective: improve us_equities momentum reliability",
                "- allowed_scope: signal-agent",
                "- promotion_focus: paper_consistency",
            ]
        ),
        encoding="utf-8",
    )
    brief = RunBrief.from_markdown(path)
    assert brief.allowed_scope == ("signal-agent",)
