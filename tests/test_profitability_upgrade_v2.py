from multi_horizon_router import route_multi_horizon_opportunity
from portfolio_strategy_engine import build_portfolio_strategy
from recommendation_accuracy_engine import evaluate_recommendation_accuracy


def _profile():
    return {
        "cash": 10000,
        "monthly_income": 8000,
        "monthly_expenses": 3000,
        "emergency_fund": 24000,
        "debt": 0,
        "investment_horizon": "5-10 years",
        "risk_tolerance": "Moderate",
        "max_single_stock_exposure": 15,
        "max_sector_exposure": 35,
    }


def test_weak_accuracy_reduces_future_confidence():
    accuracy = evaluate_recommendation_accuracy(
        [
            {"symbol": "AAPL", "action": "Buy Candidate", "horizon": "Swing", "sector": "Technology", "realized_return_pct": -5},
            {"symbol": "MSFT", "action": "Add", "horizon": "Swing", "sector": "Technology", "realized_return_pct": -2},
        ]
    )

    assert accuracy["confidence_adjustment"] < 0


def test_accuracy_context_reduces_strategy_candidate_confidence():
    weak_accuracy = {"confidence_adjustment": -10, "hit_rate": 20, "evaluated_count": 5, "summary": "Weak"}
    strategy = build_portfolio_strategy(
        _profile(),
        [],
        [{"symbol": "MSFT", "score": 78, "data_confidence": "High", "recommendation_gate": "Trusted"}],
        accuracy_context=weak_accuracy,
    )

    assert strategy["buy_candidates"][0]["accuracy_context"]["confidence_adjustment"] == -10
    assert strategy["buy_candidates"][0]["confidence_level"] in {"Moderate", "Low"}


def test_multi_horizon_router_blocks_short_term_when_risk_is_high():
    routed = route_multi_horizon_opportunity(
        "NVDA",
        {"score": 82},
        {"volatility_pct": 45, "max_drawdown_pct": -28, "return_pct": 12},
        {"fundamental_score": 78},
        {"catalysts": [{"urgency": "High"}]},
        {"confidence_adjustment": 0},
        _profile(),
    )

    assert routed["best_horizon"] in {"Swing", "Long-term"}
    assert any("Short-term action blocked" in item for item in routed["blocked_reasons"])


def test_multi_horizon_router_can_choose_long_term_over_swing():
    routed = route_multi_horizon_opportunity(
        "JNJ",
        {"score": 55},
        {"volatility_pct": 10, "max_drawdown_pct": -4, "return_pct": 1},
        {"fundamental_score": 88},
        {"catalysts": []},
        {"confidence_adjustment": 0},
        _profile(),
    )

    assert routed["best_horizon"] == "Long-term"
