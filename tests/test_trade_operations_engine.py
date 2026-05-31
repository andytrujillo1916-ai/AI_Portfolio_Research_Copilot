import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from trade_operations_engine import (
    assess_market_data_readiness,
    build_order_intent,
    build_trade_plan,
    evaluate_autopilot_safety,
)


def _base_plan_inputs():
    return {
        "symbol": "AAPL",
        "snapshot": {"symbol": "AAPL", "price": 100},
        "final_recommendation": {"final_verdict": "Buy Candidate", "confidence": "High", "market_regime": "Bull Trend"},
        "entry_exit_data": {"entry_zone": "Favorable Entry Zone", "stop_loss_guidance_pct": 6, "summary": "Entry is favorable."},
        "position_size_data": {"recommended_position_pct": 2.0, "risk_budget": "Risk 0.5% on thesis failure."},
        "risk": {"volatility_pct": 12, "max_drawdown_pct": -4},
        "data_quality": {"recommendation_gate": "Trusted", "data_confidence": "High", "source": "yfinance"},
        "market_timing": {"market_risk_level": "Moderate"},
    }


def test_short_term_trade_plan_has_required_sell_and_review_fields():
    inputs = _base_plan_inputs()
    plan = build_trade_plan(**inputs, strategy_type="Short Term")

    assert plan["status"] == "Approved for Paper"
    assert plan["entry_trigger"]
    assert plan["stop_loss"] > 0
    assert plan["take_profit"] > 0
    assert plan["sell_triggers"]
    assert plan["trim_rules"]
    assert plan["time_stop"]
    assert plan["next_review_time"]
    assert plan["preferred_entry_window"]
    assert plan["preferred_exit_window"]
    assert plan["reason_stack"]
    assert any("Thesis break" in item for item in plan["sell_triggers"])


def test_blocked_data_prevents_live_and_paper_approval():
    inputs = _base_plan_inputs()
    inputs["data_quality"] = {"recommendation_gate": "Blocked", "data_confidence": "Low", "source": "mock", "issues": ["mock data"]}
    readiness = assess_market_data_readiness(inputs["data_quality"])
    plan = build_trade_plan(**inputs, strategy_type="Short Term")
    intent = build_order_intent(plan, snapshot=inputs["snapshot"], live_requested=True)

    assert readiness["paper_allowed"] is False
    assert readiness["live_allowed"] is False
    assert plan["status"] == "Needs Data"
    assert intent["intent_type"] == "live_candidate"
    assert intent["live_blockers"]


def test_market_risk_downgrade_converts_buy_to_pullback():
    inputs = _base_plan_inputs()
    inputs["market_timing"] = {"market_risk_level": "High"}
    plan = build_trade_plan(**inputs, strategy_type="Short Term")

    assert plan["status"] == "Wait for Pullback"


def test_order_intent_is_paper_only_for_approved_plan():
    inputs = _base_plan_inputs()
    plan = build_trade_plan(**inputs, strategy_type="Short Term")
    intent = build_order_intent(plan, snapshot=inputs["snapshot"])

    assert intent["intent_type"] == "paper_buy"
    assert intent["paper_only"] is True
    assert intent["quantity"] > 0


def test_autopilot_safety_blocks_duplicate_loss_and_kill_switch():
    intent = {"intent_type": "paper_buy", "symbol": "AAPL", "quantity": 1, "limit_price": 100}
    blocked = evaluate_autopilot_safety(
        intent,
        paper_performance={"total_unrealized_pnl_pct": -3},
        paper_positions={"market_value": 1000},
        controls={"max_daily_loss_pct": 2, "kill_switch": True, "max_trades_per_day": 3, "portfolio_value": 100000},
        existing_trades=[{"symbol": "AAPL", "action": "buy", "date": "2099-01-01"}],
    )

    assert blocked["allowed"] is False
    assert any("kill switch" in item.lower() for item in blocked["failed"])
    assert any("loss limit" in item.lower() for item in blocked["failed"])


def test_autopilot_allows_clean_paper_intent():
    intent = {"intent_type": "paper_buy", "symbol": "MSFT", "quantity": 1, "limit_price": 100}
    allowed = evaluate_autopilot_safety(
        intent,
        paper_performance={"total_unrealized_pnl_pct": 1},
        paper_positions={"market_value": 1000},
        controls={"max_daily_loss_pct": 2, "max_weekly_loss_pct": 5, "max_trades_per_day": 3, "portfolio_value": 100000},
        existing_trades=[],
    )

    assert allowed["allowed"] is True


def test_long_term_plan_outputs_staged_buy_action():
    inputs = _base_plan_inputs()
    plan = build_trade_plan(**inputs, strategy_type="Long Term")

    assert plan["long_term_action"] == "Buy Now"
    assert "thesis review" in plan["max_holding_window"].lower()


def test_friday_weekend_risk_tightens_short_term_review_window():
    inputs = _base_plan_inputs()
    inputs["microstructure_context"] = {
        "day_of_week_context": "Friday weekend-risk review",
        "timing_bias": "Prefer Close Review",
        "preferred_entry_window": "Prefer late-session review only if the trade plan already supports entry.",
        "preferred_exit_window": "For short-term plans, review exit or trim before the close to manage weekend-gap risk.",
        "sell_timing_reason": "For short-term plans, review exit or trim before the close to manage weekend-gap risk.",
        "microstructure_score": 54.0,
        "calendar_context": ["Friday weekend-risk review"],
        "paper_trade_allowed": True,
        "reason_stack": [],
    }
    plan = build_trade_plan(**inputs, strategy_type="Short Term")

    assert "Friday close" in plan["max_holding_window"]
    assert any("weekend-gap risk" in item for item in plan["sell_triggers"])
