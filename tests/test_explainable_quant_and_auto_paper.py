import pandas as pd

import auto_paper_trader
from auto_paper_trader import build_auto_paper_trade_ticket, save_auto_paper_trade
from benchmark_basket_engine import find_best_etf_benchmark
from explainable_quant_engine import (
    build_ranked_decision_table,
    calculate_explainability_panel,
    generate_position_sizing_modes,
    generate_timing_explanation,
)
from strategy_scorecard_engine import generate_strategy_scorecard


def test_ranked_decision_table_uses_research_only_actions():
    screened_assets = [
        {
            "symbol": "AAPL",
            "score": 78,
            "volatility_pct": 18,
            "max_drawdown_pct": -8,
            "regime": "Bull Trend",
            "news_sentiment": "Bullish",
        },
        {
            "symbol": "WEAK",
            "score": 25,
            "volatility_pct": 30,
            "max_drawdown_pct": -20,
            "regime": "Bear Trend",
            "news_sentiment": "Bearish",
        },
    ]
    rows = build_ranked_decision_table(screened_assets)
    actions = {row["research_action"] for row in rows}

    assert rows[0]["asset"] == "AAPL"
    assert "Buy" not in actions
    assert any("research-only" in action or "Paper" in action or "Research" in action for action in actions)


def test_explainability_panel_returns_weighted_contributions():
    result = calculate_explainability_panel(
        signal_data={"score": 72},
        conviction_data={"conviction_score": 68},
        regime_data={"regime": "Bull Trend"},
        news_context={"market_sentiment": "Neutral"},
        opportunity_data={"best_opportunity": {"opportunity_score": 66}},
        risk={"volatility_pct": 18},
        exposure_limits_data={"exposure_status": "Healthy"},
        thesis_health={"thesis_status": "Stable"},
        confidence_data={"trust_level": "Moderate"},
    )

    assert "contributions" in result
    assert 0 <= result["final_score"] <= 100
    assert {row["engine"] for row in result["contributions"]} >= {"signal", "conviction"}


def test_timing_and_sizing_outputs_are_simple_and_bounded():
    timing = generate_timing_explanation(
        regime_data={"regime": "Bull Trend"},
        risk={"volatility_pct": 16, "max_drawdown_pct": -5},
        catalyst_data={"conviction_risk": "Low"},
        thesis_health={"thesis_status": "Stable"},
        signal_data={"score": 75},
    )
    sizing = generate_position_sizing_modes(
        {"recommended_position_pct": 8},
        {"volatility_pct": 16},
    )

    assert timing["timing_label"] in {
        "overextended",
        "pullback watch",
        "trend continuation",
        "wait",
        "high-risk event",
        "thesis invalidation",
    }
    assert max(row["suggested_position_pct"] for row in sizing) <= 15


def test_auto_paper_ticket_passes_only_when_gates_pass():
    ticket = build_auto_paper_trade_ticket(
        symbol="AAPL",
        snapshot={"price": 100},
        meta_decision={"final_verdict": "Research Candidate"},
        execution_data={"readiness_level": "Ready for Paper Trade"},
        position_size_data={"recommended_position_pct": 5, "recommended_position_value": 5000},
        entry_exit_data={"recommended_action": "Enter Paper Trade"},
        exposure_limits_data={"exposure_status": "Healthy"},
        correlation_data={"diversification_score": 70},
        benchmark_data={"best_benchmark": {"symbol": "SPY"}},
        data_confidence="High",
    )

    assert ticket["action"] == "Enter Paper Trade"
    assert ticket["paper_trade_action"] == "buy"
    assert ticket["quantity"] > 0


def test_auto_paper_ticket_blocks_low_confidence_and_high_exposure():
    low_confidence = build_auto_paper_trade_ticket(
        "AAPL",
        {"price": 100},
        {"final_verdict": "Research Candidate"},
        {"readiness_level": "Ready for Paper Trade"},
        {"recommended_position_pct": 5, "recommended_position_value": 5000},
        {"recommended_action": "Enter Paper Trade"},
        {"exposure_status": "Healthy"},
        {"diversification_score": 70},
        {"best_benchmark": {"symbol": "SPY"}},
        data_confidence="Low",
    )
    high_exposure = build_auto_paper_trade_ticket(
        "AAPL",
        {"price": 100},
        {"final_verdict": "Research Candidate"},
        {"readiness_level": "Ready for Paper Trade"},
        {"recommended_position_pct": 5, "recommended_position_value": 5000},
        {"recommended_action": "Enter Paper Trade"},
        {"exposure_status": "High Risk"},
        {"diversification_score": 70},
        {"best_benchmark": {"symbol": "SPY"}},
        data_confidence="High",
    )

    assert low_confidence["action"] == "Skip"
    assert high_exposure["action"] == "Skip"


def test_auto_paper_trim_requires_existing_position():
    no_position = build_auto_paper_trade_ticket(
        "AAPL",
        {"price": 100},
        {"final_verdict": "Watch"},
        {"readiness_level": "Watch"},
        {"recommended_position_pct": 0, "recommended_position_value": 0},
        {"recommended_action": "Trim"},
        {"exposure_status": "Healthy"},
        {"diversification_score": 70},
        {},
    )
    existing_position = build_auto_paper_trade_ticket(
        "AAPL",
        {"price": 100},
        {"final_verdict": "Watch"},
        {"readiness_level": "Watch"},
        {"recommended_position_pct": 0, "recommended_position_value": 0},
        {"recommended_action": "Trim"},
        {"exposure_status": "Healthy"},
        {"diversification_score": 70},
        {},
        existing_position={"shares": 10},
    )

    assert no_position["paper_trade_action"] == "none"
    assert existing_position["paper_trade_action"] == "sell"
    assert existing_position["quantity"] == 5


def test_duplicate_same_day_auto_trade_is_blocked(monkeypatch):
    monkeypatch.setattr(
        auto_paper_trader,
        "load_paper_trades",
        lambda: [{"symbol": "AAPL", "action": "buy", "date": auto_paper_trader._today()}],
    )
    result = save_auto_paper_trade(
        {
            "symbol": "AAPL",
            "paper_trade_action": "buy",
            "quantity": 1,
            "price": 100,
            "reason": "test",
        }
    )

    assert result["saved"] is False
    assert "Duplicate" in result["message"]


def test_benchmark_basket_selects_strongest_mock_etf():
    def loader(symbol, period="1mo"):
        end_price = {"SPY": 105, "QQQ": 112, "VOO": 103}.get(symbol, 101)
        return {
            "source": "mock",
            "data": pd.DataFrame(
                {
                    "Date": pd.date_range("2026-01-01", periods=3),
                    "Close": [100, 101, end_price],
                }
            ),
        }

    result = find_best_etf_benchmark(
        benchmark_symbols=["SPY", "QQQ", "VOO"],
        price_history_loader=loader,
    )

    assert result["best_benchmark"]["symbol"] == "QQQ"


def test_strategy_scorecard_reports_outperformance():
    result = generate_strategy_scorecard(
        paper_performance={
            "total_unrealized_pnl_pct": 8,
            "number_of_trades": 4,
            "win_rate": 75,
            "best_position": "AAPL",
            "worst_position": "MSFT",
        },
        benchmark_data={"best_benchmark": {"symbol": "SPY", "return_pct": 3}},
        paper_positions={"positions": {}, "market_value": 0},
    )

    assert result["status"] == "Outperforming"
    assert result["alpha_vs_best_etf_pct"] == 5
