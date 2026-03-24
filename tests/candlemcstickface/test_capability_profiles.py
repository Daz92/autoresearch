from importlib import import_module
from pathlib import Path

import pytest
import yaml


def test_load_capability_profiles_allows_empty_agents_list(
    monkeypatch, autoresearch_src_root: Path, tmp_path: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    capability_profiles = import_module(
        "autoresearch.candlemcstickface.capability_profiles"
    )

    config_path = tmp_path / "capability-profiles.yaml"
    config_path.write_text("agents: []\n", encoding="utf-8")

    profiles = capability_profiles.load_capability_profiles(config_path)

    assert dict(profiles) == {}


def test_market_strategist_profile_requires_exa_deep_tools(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    capability_profiles = import_module(
        "autoresearch.candlemcstickface.capability_profiles"
    )

    config_path = (
        Path(__file__).resolve().parents[3]
        / "agents"
        / "candlemcstickface"
        / "data"
        / "capability-profiles.yaml"
    )

    profiles = capability_profiles.load_capability_profiles(config_path)
    profile = profiles["market-strategist"]

    assert profile.required_tools_by_mode["strategy_refresh"] == (
        "exa.web_search_advanced_exa",
        "exa.deep_researcher_start",
        "exa.deep_researcher_check",
        "exa.company_research_exa",
        "exa.people_search_exa",
        "exa.crawling_exa",
    )
    assert profile.fallback_order == (
        "exa.web_search_advanced_exa",
        "exa.company_research_exa",
        "exa.people_search_exa",
        "exa.crawling_exa",
    )
    assert "skip_deep_research" in profile.disallowed_shortcuts


def test_all_required_subagent_profiles_exist(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    capability_profiles = import_module(
        "autoresearch.candlemcstickface.capability_profiles"
    )

    config_path = (
        Path(__file__).resolve().parents[3]
        / "agents"
        / "candlemcstickface"
        / "data"
        / "capability-profiles.yaml"
    )

    profiles = capability_profiles.load_capability_profiles(config_path)

    assert set(profiles) == {
        "watcher",
        "stock-scanner",
        "macro-distiller",
        "market-strategist",
    }


def test_loaded_required_tools_mapping_is_read_only(
    monkeypatch, autoresearch_src_root: Path, tmp_path: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    capability_profiles = import_module(
        "autoresearch.candlemcstickface.capability_profiles"
    )

    config_path = tmp_path / "capability-profiles.yaml"
    config_path.write_text(
        "\n".join(
            [
                "agents:",
                "  - agent_id: market-strategist",
                "    required_tools_by_mode:",
                "      strategy_refresh:",
                "        - exa.deep",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    profiles = capability_profiles.load_capability_profiles(config_path)

    with pytest.raises(TypeError):
        profiles["market-strategist"].required_tools_by_mode["strategy_refresh"] = ()


def test_source_coverage_matrix_declares_recency_windows() -> None:
    coverage_path = (
        Path(__file__).resolve().parents[3]
        / "agents"
        / "candlemcstickface"
        / "data"
        / "source-coverage-matrix.yaml"
    )

    payload = yaml.safe_load(coverage_path.read_text(encoding="utf-8"))
    source_classes = {item["name"]: item for item in payload["source_classes"]}

    assert source_classes["institutional_news"] == {
        "name": "institutional_news",
        "min_items": 3,
        "max_age_hours": 24,
        "attribution_required": True,
    }
    assert source_classes["social_sentiment"] == {
        "name": "social_sentiment",
        "min_items": 5,
        "max_age_hours": 6,
        "attribution_required": True,
    }
    assert source_classes["specialist_outlets"] == {
        "name": "specialist_outlets",
        "min_items": 2,
        "max_age_hours": 24,
        "attribution_required": True,
    }

    assert payload["deduplication"]["drop_exact_duplicates"] is True
    assert payload["confidence_tagging"]["required_levels"] == [
        "high",
        "medium",
        "low",
    ]


def test_market_strategist_instructions_reference_company_and_people_research() -> None:
    text = (
        Path(__file__).resolve().parents[3]
        / "agents"
        / "market-strategist"
        / "AGENTS.md"
    ).read_text(encoding="utf-8")

    assert "company_research_exa" in text
    assert "people_search_exa" in text
    assert "deep_researcher_start" in text
    assert "deep_researcher_check" in text


def test_macro_distiller_instructions_reference_coverage_controls() -> None:
    text = (
        Path(__file__).resolve().parents[3] / "agents" / "macro-distiller" / "AGENTS.md"
    ).read_text(encoding="utf-8")

    assert "institutional_news" in text
    assert "social_sentiment" in text
    assert "specialist_outlets" in text
    assert "attribution" in text
    assert "dedup" in text
