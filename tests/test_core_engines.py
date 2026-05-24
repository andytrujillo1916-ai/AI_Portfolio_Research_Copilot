import pandas as pd

from backtester import run_simple_backtest
from conviction_engine import calculate_conviction_score
from meta_decision_engine import generate_meta_decision
from portfolio_optimizer import generate_portfolio_allocation
from position_sizing_engine import calculate_position_size
from signal_engine import generate_signal


def test_generate_signal_required_keys():
    snapshot = {"price": 100.0, "change_pct": 1.2}
    risk = {"return_pct": 4.0, "volatility_pct": 18.0, "max_drawdown_pct": -8.0}
    news = {"market_sentiment": "Neutral", "event_tags": [], "risk_flags": []}
    result = generate_signal("AAPL", snapshot, risk, news_context=news)
    required = {"symbol", "signal", "score", "quant_score", "news_score", "reasons", "risks"}
    assert required.issubset(result.keys())


def test_conviction_score_in_range():
    result = calculate_conviction_score(
        signal_data={"score": 72},
        opportunity_data={"best_opportunity": {"opportunity_score": 65}},
        thesis_health={"thesis_status": "Stable"},
        regime_data={"regime": "Bull Trend"},
        news_context={"market_sentiment": "Neutral"},
        factor_attribution={"dominant_factor": {"factor": "Signal score quality"}, "risk_driver": {"factor": ""}},
        confidence_data={"adjusted_confidence": 6.0, "trust_level": "Moderate"},
        research_mode="Balanced",
    )
    assert 0 <= result["conviction_score"] <= 100


def test_meta_decision_required_fields():
    result = generate_meta_decision(
        symbol="AAPL",
        signal_data={"score": 70},
        conviction_data={"conviction_score": 68},
        opportunity_data={},
        alpha_data={"alpha_pct": 2.5},
        execution_data={"execution_score": 66, "readiness_level": "Near Ready"},
        position_size_data={"recommended_position_pct": 5.0},
        entry_exit_data={"recommended_action": "Hold"},
        regime_data={"regime": "Recovery"},
        news_context={"market_sentiment": "Neutral"},
        catalyst_data={"conviction_risk": "Moderate"},
        scenario_data={"overall_scenario_summary": "Mixed outcomes."},
        stress_test_data={"summary": "Manageable risk in stress view."},
        exposure_limits_data={"exposure_status": "Moderate"},
        correlation_data={"diversification_score": 62},
        capital_hierarchy_data={"top_capital_candidate": {"symbol": "AAPL"}},
        strategy_comparison_data={"best_strategy": {"strategy_name": "Trend Following Strategy"}},
        research_mode="Balanced",
    )
    assert "final_verdict" in result
    assert "decision_score" in result
    assert 0 <= result["decision_score"] <= 100


def test_simple_backtest_with_sample_prices():
    price_data = pd.DataFrame(
        {
            "Date": pd.date_range("2026-01-01", periods=30, freq="D"),
            "Close": [100 + i for i in range(30)],
        }
    )
    result = run_simple_backtest(price_data)
    assert "strategy_return_pct" in result
    assert "buy_and_hold_return_pct" in result


def test_portfolio_optimizer_returns_allocations():
    screened_assets = [
        {
            "symbol": "AAPL",
            "score": 75,
            "volatility_pct": 20,
            "max_drawdown_pct": -10,
            "regime": "Bull Trend",
            "news_sentiment": "Bullish",
        },
        {
            "symbol": "XLV",
            "score": 60,
            "volatility_pct": 15,
            "max_drawdown_pct": -8,
            "regime": "Recovery",
            "news_sentiment": "Neutral",
        },
    ]
    result = generate_portfolio_allocation(screened_assets, research_mode="Balanced")
    assert "allocations" in result
    assert isinstance(result["allocations"], list)


def test_position_sizing_returns_percentage():
    result = calculate_position_size(
        execution_data={"execution_score": 70, "readiness_level": "Near Ready"},
        conviction_data={"conviction_score": 72, "confidence_level": "Moderate"},
        risk={"volatility_pct": 22, "max_drawdown_pct": -12},
        portfolio_value=100000,
        research_mode="Balanced",
    )
    assert "recommended_position_pct" in result
    assert isinstance(result["recommended_position_pct"], float)
