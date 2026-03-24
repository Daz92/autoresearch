from datetime import timedelta


def _load(module_name: str):
    return __import__(module_name, fromlist=["*"])


def test_judge_rejects_candidate_with_excessive_drawdown(sample_signal) -> None:
    contracts = _load("autoresearch.contracts")
    MetricBundle = contracts.MetricBundle
    PromotionState = contracts.PromotionState
    Judge = _load("autoresearch.judge").Judge

    metrics = MetricBundle(
        return_pct=0.45,
        drawdown=0.31,
        hit_rate=0.68,
        turnover=0.28,
        cost_sensitivity=0.18,
        regime_stability=0.70,
    )
    decision = Judge.current().decide(
        metrics=metrics, signal=sample_signal, paper_consistency=True
    )
    assert decision.state is PromotionState.REJECT


def test_judge_invalid_on_time_provenance_violation(sample_signal) -> None:
    PromotionState = _load("autoresearch.contracts").PromotionState
    Judge = _load("autoresearch.judge").Judge

    invalid_signal = sample_signal.__class__(
        market=sample_signal.market,
        symbol=sample_signal.symbol,
        as_of=sample_signal.as_of,
        available_at=sample_signal.as_of - timedelta(minutes=1),
        side=sample_signal.side,
        confidence=sample_signal.confidence,
        thesis=sample_signal.thesis,
        entry_zone=sample_signal.entry_zone,
        invalidation=sample_signal.invalidation,
        target_logic=sample_signal.target_logic,
        provenance=sample_signal.provenance,
    )
    decision = Judge.current().decide(
        metrics=sample_metrics(), signal=invalid_signal, paper_consistency=True
    )
    assert decision.state is PromotionState.INVALID


def sample_metrics():
    MetricBundle = _load("autoresearch.contracts").MetricBundle

    return MetricBundle(
        return_pct=0.32,
        drawdown=0.14,
        hit_rate=0.60,
        turnover=0.30,
        cost_sensitivity=0.20,
        regime_stability=0.66,
    )


def test_judge_holds_when_score_good_but_paper_inconsistent(
    sample_signal, sample_metrics
) -> None:
    PromotionState = _load("autoresearch.contracts").PromotionState
    Judge = _load("autoresearch.judge").Judge

    decision = Judge.current().decide(
        metrics=sample_metrics, signal=sample_signal, paper_consistency=False
    )
    assert decision.state is PromotionState.HOLD


def test_judge_advances_when_score_and_paper_consistent(sample_signal) -> None:
    contracts = _load("autoresearch.contracts")
    MetricBundle = contracts.MetricBundle
    PromotionState = contracts.PromotionState
    Judge = _load("autoresearch.judge").Judge

    metrics = MetricBundle(
        return_pct=0.60,
        drawdown=0.09,
        hit_rate=0.70,
        turnover=0.20,
        cost_sensitivity=0.10,
        regime_stability=0.82,
    )
    decision = Judge.current().decide(
        metrics=metrics, signal=sample_signal, paper_consistency=True
    )
    assert decision.state is PromotionState.ADVANCE
