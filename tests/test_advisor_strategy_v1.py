from data_quality_engine import evaluate_data_quality
from portfolio_strategy_engine import build_portfolio_strategy


def _ready_profile():
    return {
        "cash": 5000,
        "monthly_income": 7000,
        "monthly_expenses": 3000,
        "emergency_fund": 24000,
        "debt": 0,
        "investment_horizon": "5-10 years",
        "risk_tolerance": "Moderate",
        "max_single_stock_exposure": 15,
        "max_sector_exposure": 35,
    }


def test_mock_data_blocks_recommendation_gate():
    quality = evaluate_data_quality({"source": "mock", "is_fallback": True, "price": 100})

    assert quality["recommendation_gate"] == "Blocked"
    assert quality["data_confidence"] == "Low"


def test_strong_candidate_requires_suitability_before_buy_candidate():
    strategy = build_portfolio_strategy(
        _ready_profile(),
        [],
        [{"symbol": "MSFT", "score": 78, "data_confidence": "High", "recommendation_gate": "Trusted"}],
    )

    assert strategy["buy_candidates"][0]["action"] == "Buy Candidate"


def test_low_emergency_fund_keeps_cash_instead_of_buying():
    profile = _ready_profile()
    profile["emergency_fund"] = 1000
    strategy = build_portfolio_strategy(
        profile,
        [],
        [{"symbol": "MSFT", "score": 82, "data_confidence": "High", "recommendation_gate": "Trusted"}],
    )

    assert strategy["buy_candidates"] == []
    assert strategy["cash_strategy"]["action"] == "Keep Cash"


def test_overweight_holding_becomes_trim_candidate():
    strategy = build_portfolio_strategy(
        _ready_profile(),
        [{"symbol": "AAPL", "current_value": 50000}],
        [{"symbol": "AAPL", "score": 82, "data_confidence": "High", "recommendation_gate": "Trusted"}],
    )

    assert strategy["trim_candidates"][0]["action"] == "Trim"


def test_weak_holding_with_good_data_becomes_sell_candidate():
    profile = _ready_profile()
    profile["cash"] = 20000
    strategy = build_portfolio_strategy(
        profile,
        [{"symbol": "AAPL", "current_value": 1000}],
        [{"symbol": "AAPL", "score": 30, "data_confidence": "High", "recommendation_gate": "Trusted"}],
    )

    assert strategy["sell_candidates"][0]["action"] == "Sell Candidate"
