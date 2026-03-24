from datetime import datetime, timezone


def _load(module_name: str):
    return __import__(module_name, fromlist=["*"])


def test_crypto_adapter_marks_market_as_crypto() -> None:
    CryptoAdapter = _load(
        "autoresearch.plugins.signal_agent.adapters.crypto"
    ).CryptoAdapter

    adapter = CryptoAdapter()
    normalized = adapter.normalize(
        {
            "symbol": "BTC-USD",
            "price": 87500.0,
            "as_of": "2026-03-23T12:00:00Z",
            "available_at": "2026-03-23T12:00:00Z",
            "provenance": ["feed:binance"],
        }
    )
    assert normalized.market.value == "crypto"
    assert normalized.symbol == "BTC/USD"


def test_crypto_adapter_uses_input_timestamp() -> None:
    CryptoAdapter = _load(
        "autoresearch.plugins.signal_agent.adapters.crypto"
    ).CryptoAdapter

    ts = datetime(2026, 3, 23, 12, 0, tzinfo=timezone.utc)
    normalized = CryptoAdapter().normalize(
        {
            "symbol": "ETH/USD",
            "price": 4200.0,
            "as_of": ts,
            "available_at": ts,
        }
    )
    assert normalized.as_of == ts
    assert normalized.available_at == ts


def test_signal_agent_plugin_generates_contract_signal_from_crypto_snapshot() -> None:
    CryptoAdapter = _load(
        "autoresearch.plugins.signal_agent.adapters.crypto"
    ).CryptoAdapter
    SignalAgentPlugin = _load(
        "autoresearch.plugins.signal_agent.plugin"
    ).SignalAgentPlugin

    snapshot = CryptoAdapter().normalize(
        {
            "symbol": "SOL/USD",
            "price": 180.0,
            "as_of": "2026-03-23T12:05:00Z",
            "available_at": "2026-03-23T12:05:00Z",
        }
    )
    signal = SignalAgentPlugin(min_confidence=0.64).generate_signal(snapshot)
    assert signal.market.value == "crypto"
    assert signal.symbol == "SOL/USD"
    assert signal.confidence >= 0.64
