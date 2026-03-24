def _load(module_name: str):
    return __import__(module_name, fromlist=["*"])


def test_handoff_maps_signal_to_trade_intent_payload(sample_signal) -> None:
    build_trade_intent_payload = _load(
        "autoresearch.integrations.candlemcstickface"
    ).build_trade_intent_payload

    payload = build_trade_intent_payload(
        signal=sample_signal,
        watcher_session_id="watch-123",
        macro_session_id="macro-456",
    )
    assert payload["signal_inputs"]["watcher_session_id"] == "watch-123"
    assert payload["signal_inputs"]["macro_session_id"] == "macro-456"
    assert payload["symbol"] == "BTC/USD"
    assert payload["side"] == "buy"


def test_handoff_is_payload_only_and_contains_contract_shape(sample_signal) -> None:
    build_trade_intent_payload = _load(
        "autoresearch.integrations.candlemcstickface"
    ).build_trade_intent_payload

    payload = build_trade_intent_payload(
        signal=sample_signal,
        watcher_session_id="watch-abc",
        macro_session_id="macro-def",
        screener_session_id="scan-xyz",
    )
    assert set(payload.keys()) == {
        "intent_id",
        "created_at",
        "symbol",
        "side",
        "qty",
        "type",
        "limit_price",
        "stop_price",
        "time_in_force",
        "max_slippage_bps",
        "max_risk_usd",
        "signal_inputs",
        "data_freshness",
        "metadata",
    }
    assert payload["signal_inputs"]["screener_session_id"] == "scan-xyz"
