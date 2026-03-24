from datetime import datetime, timezone


def _load(module_name: str):
    return __import__(module_name, fromlist=["*"])


def test_us_equities_adapter_marks_market_as_us_equities() -> None:
    USEquitiesAdapter = _load(
        "autoresearch.plugins.signal_agent.adapters.us_equities"
    ).USEquitiesAdapter

    adapter = USEquitiesAdapter()
    normalized = adapter.normalize(
        {
            "symbol": "aapl",
            "price": 212.0,
            "as_of": "2026-03-23T13:30:00Z",
            "available_at": "2026-03-23T13:30:01Z",
            "provenance": ["feed:polygon"],
        }
    )
    assert normalized.market.value == "us_equities"
    assert normalized.symbol == "AAPL"


def test_us_equities_adapter_defaults_available_at_to_as_of() -> None:
    USEquitiesAdapter = _load(
        "autoresearch.plugins.signal_agent.adapters.us_equities"
    ).USEquitiesAdapter

    ts = datetime(2026, 3, 23, 13, 30, tzinfo=timezone.utc)
    normalized = USEquitiesAdapter().normalize(
        {
            "symbol": "MSFT",
            "price": 400.1,
            "as_of": ts,
            "available_at": ts,
        }
    )
    assert normalized.available_at == ts


def test_signal_agent_plugin_generates_contract_signal_from_equities_snapshot() -> None:
    USEquitiesAdapter = _load(
        "autoresearch.plugins.signal_agent.adapters.us_equities"
    ).USEquitiesAdapter
    SignalAgentPlugin = _load(
        "autoresearch.plugins.signal_agent.plugin"
    ).SignalAgentPlugin

    snapshot = USEquitiesAdapter().normalize(
        {
            "symbol": "NVDA",
            "price": 900.0,
            "as_of": "2026-03-23T14:00:00Z",
            "available_at": "2026-03-23T14:00:02Z",
        }
    )
    signal = SignalAgentPlugin().generate_signal(snapshot)
    assert signal.market.value == "us_equities"
    assert signal.symbol == "NVDA"
    assert signal.provenance[-1] == "plugin:signal-agent"
