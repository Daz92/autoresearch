from importlib import import_module
from pathlib import Path

import pytest


def test_schema_version_file_required(
    monkeypatch, autoresearch_src_root: Path, tmp_path: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    canonical_state = import_module("autoresearch.candlemcstickface.canonical_state")

    path = tmp_path / "schema-version.yaml"
    path.write_text("version: 1\n", encoding="utf-8")

    state = canonical_state.load_schema_version(path)

    assert state.version == 1
    assert state.owners == {}
    assert len(state.schema_hash) == 64


def test_repo_schema_version_declares_canonical_owners(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    canonical_state = import_module("autoresearch.candlemcstickface.canonical_state")

    schema_path = (
        Path(__file__).resolve().parents[3]
        / "agents"
        / "candlemcstickface"
        / "data"
        / "schema-version.yaml"
    )

    state = canonical_state.load_schema_version(schema_path)

    expected_owners = {
        "working_list": "agents/candlemcstickface/data/working-list.yaml",
        "screener_rules": "agents/candlemcstickface/data/screener-rules.yaml",
        "opportunity_queue": "agents/candlemcstickface/data/opportunity-queue.yaml",
    }

    assert state.version == 1
    assert state.owners == expected_owners
    assert state.schema_hash == canonical_state.compute_schema_hash(1, expected_owners)


def test_schema_version_rejects_non_mapping_owners(
    monkeypatch, autoresearch_src_root: Path, tmp_path: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    canonical_state = import_module("autoresearch.candlemcstickface.canonical_state")

    path = tmp_path / "schema-version.yaml"
    path.write_text("version: 1\nowners: not-a-mapping\n", encoding="utf-8")

    with pytest.raises(ValueError, match="owners must be a mapping"):
        canonical_state.load_schema_version(path)


def test_schema_version_rejects_invalid_declared_hash(
    monkeypatch, autoresearch_src_root: Path, tmp_path: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    canonical_state = import_module("autoresearch.candlemcstickface.canonical_state")

    path = tmp_path / "schema-version.yaml"
    path.write_text(
        "\n".join(
            [
                "version: 1",
                "schema_hash: deadbeef",
                "owners:",
                "  working_list: agents/candlemcstickface/data/working-list.yaml",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="schema_hash does not match"):
        canonical_state.load_schema_version(path)


def test_loaded_schema_version_owners_are_read_only(
    monkeypatch, autoresearch_src_root: Path, tmp_path: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    canonical_state = import_module("autoresearch.candlemcstickface.canonical_state")

    path = tmp_path / "schema-version.yaml"
    path.write_text(
        "\n".join(
            [
                "version: 1",
                "owners:",
                "  working_list: agents/candlemcstickface/data/working-list.yaml",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    state = canonical_state.load_schema_version(path)

    with pytest.raises(TypeError):
        state.owners["working_list"] = "mutated"
