import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from final_recommendation_engine import build_final_recommendation
from growth_discovery_engine import score_growth_discovery
from market_timing_engine import build_market_timing_context
from opportunity_universe import build_opportunity_universe


def test_opportunity_universe_includes_us_adrs_etfs_and_recent_listings():
    rows = build_opportunity_universe(scope="US_ADR", include_etfs=True, include_ipos=True)
    symbols = {row["symbol"] for row in rows}
    listing_types = {row["listing_type"] for row in rows}

    assert "PLTR" in symbols
    assert "TSM" in symbols
    assert "SMH" in symbols
    assert "RDDT" in symbols
    assert "US-listed ADR/global equity" in listing_types
    assert "ETF" in listing_types
    assert "IPO/recent listing" in listing_types


def test_blocked_data_caps_growth_discovery_action():
    result = score_growth_discovery(
        "TEST",
        {"return_pct": 20, "volatility_pct": 15, "max_drawdown_pct": -4, "score": 90},
        source_quality={"recommendation_gate": "Blocked", "data_confidence": "Low"},
    )

    assert result["growth_score"] <= 48
    assert result["research_label"] in {"Emerging Watchlist", "Avoid"}


def test_high_market_risk_downgrades_final_verdict_to_pullback():
    final = build_final_recommendation(
        "PLTR",
        [
            {"engine": "Signal", "action": "Buy Candidate", "score": 85},
            {"engine": "Growth Discovery", "action": "Strategic Buy Candidate", "score": 82},
        ],
        {"score": 82, "volatility_pct": 20, "target_allocation_band": "2%-4%"},
        {"recommendation_gate": "Trusted", "data_confidence": "High"},
        {"status": "Risk allowed"},
        {"confidence_adjustment": 0},
        growth_discovery_context={"research_label": "Strategic Buy Candidate", "growth_score": 82},
        market_timing_context={"market_risk_level": "High", "timing_regime": "Stress", "strategic_buy_zones": ["Wait for stabilization."]},
    )

    assert final["final_verdict"] == "Wait for Pullback"
    assert final["paper_trade_eligible"] is False
    assert final["market_regime"] == "Stress"


def test_market_timing_reports_high_risk_when_breadth_and_indexes_are_weak():
    timing = build_market_timing_context(
        {
            "rows": [
                {"symbol": "SPY", "return_pct": -8, "volatility_pct": 35, "max_drawdown_pct": -18},
                {"symbol": "QQQ", "return_pct": -10, "volatility_pct": 38, "max_drawdown_pct": -22},
            ]
        },
        [
            {"symbol": "A", "return_pct": -1},
            {"symbol": "B", "return_pct": -2},
            {"symbol": "C", "return_pct": 1},
        ],
        {},
        {"macro_state": "Risk-Off"},
        {"monthly_income": 1000, "monthly_expenses": 1500, "emergency_fund": 500},
    )

    assert timing["market_risk_level"] == "High"
    assert timing["timing_regime"] == "Stress"
    assert timing["crash_warning_flags"]

