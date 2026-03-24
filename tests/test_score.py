def _load(module_name: str):
    return __import__(module_name, fromlist=["*"])


def test_score_policy_exposes_version() -> None:
    ScorePolicy = _load("autoresearch.score").ScorePolicy

    policy = ScorePolicy.current()
    assert policy.version == "v1"


def test_score_policy_returns_deterministic_composite(sample_metrics) -> None:
    ScorePolicy = _load("autoresearch.score").ScorePolicy

    policy = ScorePolicy.current()
    score = policy.score(sample_metrics)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
    assert score == policy.score(sample_metrics)


def test_score_penalizes_drawdown_and_costs() -> None:
    contracts = _load("autoresearch.contracts")
    MetricBundle = contracts.MetricBundle
    ScorePolicy = _load("autoresearch.score").ScorePolicy

    policy = ScorePolicy.current()
    clean = MetricBundle(
        return_pct=0.40,
        drawdown=0.10,
        hit_rate=0.62,
        turnover=0.22,
        cost_sensitivity=0.15,
        regime_stability=0.74,
    )
    expensive = MetricBundle(
        return_pct=0.40,
        drawdown=0.28,
        hit_rate=0.62,
        turnover=0.60,
        cost_sensitivity=0.55,
        regime_stability=0.74,
    )

    assert policy.score(clean) > policy.score(expensive)
