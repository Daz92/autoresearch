from pathlib import Path


def _load(module_name: str):
    return __import__(module_name, fromlist=["*"])


def test_registry_records_score_version(tmp_path: Path, sample_metrics) -> None:
    contracts = _load("autoresearch.contracts")
    PromotionState = contracts.PromotionState
    registry_module = _load("autoresearch.registry")
    Registry = registry_module.Registry
    RegistryEntry = registry_module.RegistryEntry

    registry = Registry(root=tmp_path)
    entry = RegistryEntry(
        candidate_version="candlev1",
        configuration_summary={"window": "wf-30d"},
        market_coverage=("us_equities", "crypto"),
        metric_bundle=sample_metrics,
        score_version="v1",
        promotion_state=PromotionState.HOLD,
        paper_results={"consistency": 0.62},
        evaluation_artifacts=("artifact://metrics/1",),
    )

    registry.record_run(entry)
    assert (tmp_path / "runs.jsonl").exists()


def test_registry_round_trips_entries(tmp_path: Path, sample_metrics) -> None:
    contracts = _load("autoresearch.contracts")
    PromotionState = contracts.PromotionState
    registry_module = _load("autoresearch.registry")
    Registry = registry_module.Registry
    RegistryEntry = registry_module.RegistryEntry

    registry = Registry(root=tmp_path)
    registry.record_run(
        RegistryEntry(
            candidate_version="signal-agent-001",
            configuration_summary={"brief": "crypto-breakout"},
            market_coverage=("crypto",),
            metric_bundle=sample_metrics,
            score_version="v1",
            promotion_state=PromotionState.ADVANCE,
            paper_results={"paper_consistency": True},
            evaluation_artifacts=("artifact://paper/001",),
        )
    )

    entries = registry.list_runs()
    assert len(entries) == 1
    loaded = entries[0]
    assert loaded.candidate_version == "signal-agent-001"
    assert loaded.score_version == "v1"
    assert loaded.promotion_state is PromotionState.ADVANCE
