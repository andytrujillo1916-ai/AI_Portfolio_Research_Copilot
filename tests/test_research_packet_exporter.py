import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from research_packet_exporter import build_research_packet_markdown


def test_research_packet_contains_required_sections_and_disclaimer():
    packet = build_research_packet_markdown(
        "AAPL",
        {"price": 100, "change_pct": 1.2, "volume": 1000, "source": "yfinance"},
        {"return_pct": 5, "volatility_pct": 20, "max_drawdown_pct": -8},
        {"market_sentiment": "Neutral", "event_tags": ["earnings"], "risk_flags": ["valuation risk"]},
        {"signal": "Watch", "score": 62, "quant_score": 60, "news_score": 55, "reasons": ["Trend improving"], "risks": ["Volatility elevated"]},
        {"strategy_return_pct": 3, "buy_and_hold_return_pct": 2, "signal_changes": 4},
        {"strategy_return_pct": 3, "benchmark_return_pct": 2, "edge_vs_benchmark_pct": 1},
        timestamp="2026-05-27 10:00:00",
    )

    for section in [
        "## Asset",
        "## Market Snapshot",
        "## Risk Metrics",
        "## News Context",
        "## Signal Summary",
        "## Backtest Summary",
        "## Portfolio Comparison Summary",
        "## Bull Case",
        "## Bear Case",
        "## Key Risks",
        "## Uncertainty / Limitations",
        "## Research-Only Disclaimer",
    ]:
        assert section in packet

    assert "Research-only packet" in packet
    assert "does not connect to broker APIs" in packet
    assert "Fallback/mock data: No" in packet
    assert "Signal changes: 4" in packet
    assert "AAPL" in packet


def test_research_packet_marks_fallback_context():
    packet = build_research_packet_markdown(
        "XYZ",
        {
            "price": 100,
            "change_pct": 0.0,
            "volume": 0,
            "source": "mock",
            "is_fallback": True,
            "error": "sample fallback",
        },
        {},
        {"market_sentiment": "Neutral", "recent_headlines": []},
        {},
        {"number_of_signal_changes": 2},
        {},
        timestamp="2026-05-27 10:00:00",
    )

    assert "Fallback/mock data: Yes" in packet
    assert "sample fallback" in packet
    assert "Fallback/mock rule-based context" in packet
    assert "Signal changes: 2" in packet
