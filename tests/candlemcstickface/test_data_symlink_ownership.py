from pathlib import Path


def test_subagent_data_paths_are_symlinked_to_canonical_owner() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    expected = {
        "agents/watcher/data/working-list.yaml": "agents/candlemcstickface/data/working-list.yaml",
        "agents/stock-scanner/data/screener-rules.yaml": "agents/candlemcstickface/data/screener-rules.yaml",
        "agents/stock-scanner/data/opportunity-queue.yaml": "agents/candlemcstickface/data/opportunity-queue.yaml",
        "agents/market-strategist/data/screener-rules.yaml": "agents/candlemcstickface/data/screener-rules.yaml",
        "agents/market-strategist/data/opportunity-queue.yaml": "agents/candlemcstickface/data/opportunity-queue.yaml",
    }

    for local_rel, canonical_rel in expected.items():
        local_path = repo_root / local_rel
        canonical_path = (repo_root / canonical_rel).resolve()

        assert local_path.is_symlink(), f"Expected symlink: {local_rel}"
        assert local_path.resolve() == canonical_path, (
            f"Symlink target mismatch for {local_rel}: "
            f"{local_path.resolve()} != {canonical_path}"
        )
