import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import best_opportunities_engine as boe
from best_opportunities_engine import rank_best_opportunities, run_any_ticker_research
from multi_horizon_router import route_multi_horizon_opportunity
from recommendation_accuracy_engine import evaluate_recommendation_accuracy, build_research_process_audit
from sec_edgar_fundamentals import extract_sec_fundamental_context


def test_strong_fundamentals_favor_long_term_lane():
    result = route_multi_horizon_opportunity(
        "QUALITY",
        {"score": 68, "recommendation_gate": "Trusted"},
        {"return_pct": 4, "volatility_pct": 10, "max_drawdown_pct": -3},
        {"fundamental_score": 92},
        {},
        {},
        {"risk_tolerance": "Moderate"},
    )

    assert result["best_lane"] == "Long Term"
    assert result["long_term_score"] > result["short_term_score"]
    assert "entry_state" in result


def test_momentum_with_weak_fundamentals_favors_short_term_lane():
    result = route_multi_horizon_opportunity(
        "MOMO",
        {"score": 88, "recommendation_gate": "Trusted"},
        {"return_pct": 18, "volatility_pct": 14, "max_drawdown_pct": -5},
        {"fundamental_score": 32},
        {"catalysts": [{"urgency": "High"}]},
        {},
        {"risk_tolerance": "Moderate"},
    )

    assert result["best_lane"] == "Short Term"
    assert result["short_term_score"] > result["long_term_score"]


def test_broad_market_proxy_can_win_futures_proxy_lane():
    result = route_multi_horizon_opportunity(
        "SPY",
        {"score": 72, "recommendation_gate": "Trusted"},
        {"return_pct": 5, "volatility_pct": 9, "max_drawdown_pct": -4},
        {"fundamental_score": 50},
        {},
        {},
        {"risk_tolerance": "Moderate"},
    )

    assert result["best_lane"] == "Futures Proxy"
    assert "proxy" in result["summary"].lower()


def test_blocked_data_prevents_buy_entry_state():
    result = route_multi_horizon_opportunity(
        "BLOCK",
        {"score": 95, "recommendation_gate": "Blocked"},
        {"return_pct": 20, "volatility_pct": 8, "max_drawdown_pct": -3},
        {"fundamental_score": 90},
        {},
        {},
        {},
    )

    assert result["best_lane"] == "Needs Data"
    assert result["entry_state"] == "Needs Data"


def test_rank_best_opportunities_splits_lanes():
    result = rank_best_opportunities(
        [
            {"symbol": "SPY", "score": 72, "return_pct": 5, "volatility_pct": 9, "max_drawdown_pct": -4, "recommendation_gate": "Trusted", "data_confidence": "High"},
            {"symbol": "MOMO", "score": 88, "return_pct": 18, "volatility_pct": 14, "max_drawdown_pct": -5, "recommendation_gate": "Trusted", "data_confidence": "High", "growth_score": 30},
            {"symbol": "BLOCK", "score": 95, "return_pct": 20, "volatility_pct": 8, "max_drawdown_pct": -3, "recommendation_gate": "Blocked", "data_confidence": "Low"},
        ]
    )

    assert result["by_lane"]["Futures Proxy"][0]["symbol"] == "SPY"
    assert result["by_lane"]["Short Term"]
    assert result["by_lane"]["Needs Data"][0]["symbol"] == "BLOCK"


def _history():
    now = datetime.now(timezone.utc)
    return {
        "source": "sec_edgar",
        "is_fallback": False,
        "last_timestamp": now.isoformat(),
        "data": {
            "Date": [(now - timedelta(days=9 - i)).isoformat() for i in range(10)],
            "Close": [100 + i for i in range(10)],
        },
    }


def test_any_ticker_valid_packet_with_monkeypatched_free_data(monkeypatch):
    monkeypatch.setattr(boe, "get_market_snapshot", lambda symbol: {"symbol": symbol, "price": 109, "change_pct": 1, "source": "sec_edgar", "is_fallback": False, "last_timestamp": datetime.now(timezone.utc).isoformat()})
    monkeypatch.setattr(boe, "get_price_history", lambda symbol, period="1mo": _history())
    monkeypatch.setattr(boe, "_generate_news_context", lambda symbol: {"market_sentiment": "Bullish", "event_tags": ["earnings"], "risk_flags": []})
    monkeypatch.setattr(boe, "_get_sec_fundamental_context", lambda symbol: {"revenue_growth_pct": 12, "profitability_trend": "Improving", "recent_filing_status": "Connected"})

    packet = run_any_ticker_research("AAPL")

    assert packet["symbol"] == "AAPL"
    assert packet["final_verdict"] in {"Buy Candidate", "Add", "Watch", "Wait for Pullback", "Needs Data"}
    assert packet["best_lane"] in {"Long Term", "Short Term", "Futures Proxy", "Needs Data"}
    assert packet["data_quality"]["recommendation_gate"] != "Blocked"


def test_any_ticker_mock_data_returns_needs_data(monkeypatch):
    monkeypatch.setattr(boe, "get_market_snapshot", lambda symbol: {"symbol": symbol, "price": 100, "source": "mock", "is_fallback": True})
    monkeypatch.setattr(boe, "get_price_history", lambda symbol, period="1mo": {"source": "mock", "is_fallback": True, "data": {"Close": [99, 100]}})
    monkeypatch.setattr(boe, "_generate_news_context", lambda symbol: {"market_sentiment": "Neutral", "event_tags": [], "risk_flags": []})
    monkeypatch.setattr(boe, "_get_sec_fundamental_context", lambda symbol: {})

    packet = run_any_ticker_research("UNKNOWN")

    assert packet["final_verdict"] == "Needs Data"
    assert packet["best_lane"] == "Needs Data"
    assert packet["data_quality"]["recommendation_gate"] == "Blocked"


def test_learning_updates_lane_stats_and_audit():
    accuracy = evaluate_recommendation_accuracy(
        [
            {
                "symbol": "A",
                "action": "Buy Candidate",
                "horizon": "Long Term",
                "realized_return_pct": -4,
                "max_drawdown_after_signal": 12,
                "alpha_vs_benchmark_pct": -2,
                "engine_inputs": '{"lane": "Long Term", "data_confidence": "High", "news_sentiment": "Bullish", "fundamental_quality": "Supportive"}',
            }
        ]
    )
    audit = build_research_process_audit(accuracy)

    assert accuracy["lane_stats"][0]["lane"] == "Long Term"
    assert accuracy["confidence_adjustment"] < 0
    assert audit["missed_risk_flags"]


def test_sec_companyfacts_extraction_is_optional_and_source_labeled():
    facts = {
        "facts": {
            "us-gaap": {
                "Revenues": {
                    "units": {
                        "USD": [
                            {"fy": 2024, "filed": "2025-01-01", "val": 100},
                            {"fy": 2025, "filed": "2026-01-01", "val": 120},
                        ]
                    }
                },
                "NetIncomeLoss": {
                    "units": {
                        "USD": [
                            {"fy": 2024, "filed": "2025-01-01", "val": 10},
                            {"fy": 2025, "filed": "2026-01-01", "val": 16},
                        ]
                    }
                },
            }
        }
    }

    result = extract_sec_fundamental_context(facts)

    assert result["source"] == "sec_edgar"
    assert result["recent_filing_status"] == "Connected"
    assert result["revenue_growth_pct"] == 20
