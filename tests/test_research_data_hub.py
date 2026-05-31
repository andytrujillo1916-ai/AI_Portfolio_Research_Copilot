import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from research_data_hub import (
    build_research_data_context,
    build_source_manifest_item,
    filter_candidates_by_preset,
    merge_research_universe,
    rank_discovery_candidates,
)


def test_universe_merges_and_dedupes_dynamic_rows_before_static_defaults():
    rows = merge_research_universe(
        watchlist=["AAPL", "SPY", "QQQ"],
        dynamic_rows=[{"symbol": "RKLB", "score": 80}, {"symbol": "AAPL", "score": 20}],
        paper_positions={"positions": {"MSFT": {"shares": 1}}},
        manual_symbols=["TEM"],
        selected_symbol="NVDA",
    )
    symbols = [row["symbol"] for row in rows]

    assert symbols.count("AAPL") == 1
    assert symbols.index("RKLB") < symbols.index("SPY")
    assert {"NVDA", "RKLB", "MSFT", "TEM"}.issubset(set(symbols))
    assert "dynamic_scan" in next(row for row in rows if row["symbol"] == "AAPL")["origins"]


def test_source_manifest_splits_freshness_from_source_trust():
    manifest = build_source_manifest_item(
        "AAPL",
        "history",
        {"source": "yfinance", "last_timestamp": "2026-05-31T12:00:00+00:00", "is_fallback": False, "data": {"Close": [1, 2]}},
    )

    assert manifest["freshness_confidence"] in {"High", "Medium"}
    assert manifest["source_trust"] == "Warning"
    assert manifest["allowed_use"] in {"research_only", "research_and_recommendation"}


def test_research_context_marks_period_or_universe_changes_stale():
    context = build_research_data_context(
        "AAPL",
        "3mo",
        watchlist=["AAPL"],
        dynamic_rows=[{"symbol": "AAPL", "score": 80, "recommendation_gate": "Trusted", "data_confidence": "High"}],
        previous_signature="old-signature",
        previous_period="1mo",
        last_scan_at="2026-05-31 10:00:00",
    )

    assert context["is_stale"] is True
    assert "Period changed" in context["stale_reason"]
    assert context["data_source_manifest"]
    assert context["discovery_rows"][0]["source_manifest"]


def test_discovery_ranker_prefers_lanes_and_blocks_bad_data():
    ranked = rank_discovery_candidates(
        [
            {"symbol": "QUALITY", "score": 68, "fundamental_score": 92, "growth_score": 88, "return_pct": 3, "volatility_pct": 10, "max_drawdown_pct": -4, "news_sentiment": "Neutral", "recommendation_gate": "Trusted", "data_confidence": "High"},
            {"symbol": "MOMO", "score": 90, "fundamental_score": 35, "return_pct": 16, "volatility_pct": 14, "max_drawdown_pct": -5, "news_sentiment": "Bullish", "recommendation_gate": "Trusted", "data_confidence": "High"},
            {"symbol": "WEAK", "score": 25, "return_pct": -18, "volatility_pct": 20, "max_drawdown_pct": -22, "news_sentiment": "Bearish", "recommendation_gate": "Trusted", "data_confidence": "High"},
            {"symbol": "MOCK", "score": 95, "return_pct": 30, "volatility_pct": 10, "max_drawdown_pct": -2, "recommendation_gate": "Blocked", "data_confidence": "Low"},
        ],
        market_timing={"market_risk_level": "Elevated"},
    )
    by_symbol = {row["symbol"]: row for row in ranked}

    assert by_symbol["QUALITY"]["best_lane"] == "Long-Term Buy Research"
    assert by_symbol["MOMO"]["best_lane"] == "Short-Term Buy Research"
    assert by_symbol["WEAK"]["best_lane"] == "Short-Sale Research"
    assert by_symbol["WEAK"]["short_sale_research_only"] is True
    assert by_symbol["MOCK"]["best_lane"] == "Needs Data"


def test_saved_screen_filters_return_expected_candidates():
    rows = [
        {"symbol": "A", "best_lane": "Long-Term Buy Research", "opportunity_label": "Research Candidate"},
        {"symbol": "B", "best_lane": "Short-Sale Research", "opportunity_label": "Research Candidate"},
        {"symbol": "C", "best_lane": "Needs Data", "opportunity_label": "Needs Data", "recommendation_gate": "Blocked"},
    ]

    assert filter_candidates_by_preset(rows, "Long-Term Quality")[0]["symbol"] == "A"
    assert filter_candidates_by_preset(rows, "Short-Sale Research")[0]["symbol"] == "B"
    assert filter_candidates_by_preset(rows, "Needs Data")[0]["symbol"] == "C"
