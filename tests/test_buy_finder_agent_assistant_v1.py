import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent_research_engine import generate_agent_research_tasks
from buy_finder_engine import build_buy_finder, build_portfolio_action_plan
from final_recommendation_engine import build_final_recommendation


def test_blocked_interesting_candidate_becomes_needs_data_not_avoid():
    result = build_buy_finder(
        [
            {
                "symbol": "PLTR",
                "score": 68,
                "growth_score": 70,
                "return_pct": 4,
                "volatility_pct": 24,
                "recommendation_gate": "Blocked",
                "data_confidence": "Low",
                "theme": "AI software",
            }
        ],
        {},
        {"market_risk_level": "Moderate"},
        {"monthly_income": 5000, "monthly_expenses": 3000, "emergency_fund": 15000},
        [],
        {},
    )

    assert result["all_rows"][0]["action"] == "Needs Data"
    assert result["avoid_with_evidence"] == []


def test_strong_trusted_candidate_can_be_buy_candidate():
    result = build_buy_finder(
        [
            {
                "symbol": "NVDA",
                "score": 82,
                "growth_score": 80,
                "return_pct": 9,
                "volatility_pct": 22,
                "recommendation_gate": "Trusted",
                "data_confidence": "High",
            }
        ],
        {},
        {"market_risk_level": "Moderate"},
        {"monthly_income": 5000, "monthly_expenses": 3000, "emergency_fund": 18000},
        [],
        {},
    )

    assert result["best_buy_candidates"][0]["symbol"] == "NVDA"
    assert result["best_buy_candidates"][0]["paper_trade_eligible"] is True


def test_high_market_risk_turns_strong_candidate_to_pullback():
    result = build_buy_finder(
        [
            {
                "symbol": "TSM",
                "score": 82,
                "growth_score": 80,
                "return_pct": 9,
                "volatility_pct": 22,
                "recommendation_gate": "Trusted",
                "data_confidence": "High",
            }
        ],
        {},
        {"market_risk_level": "High"},
        {"monthly_income": 5000, "monthly_expenses": 3000, "emergency_fund": 18000},
        [],
        {},
    )

    assert result["wait_for_pullback"][0]["symbol"] == "TSM"


def test_final_verdict_uses_needs_data_for_blocked_gate():
    final = build_final_recommendation(
        "PLTR",
        [{"engine": "Buy Finder", "action": "Needs Data", "score": 70}],
        {"score": 70},
        {"recommendation_gate": "Blocked", "data_confidence": "Low"},
        {"status": "Ready for selective investing"},
        {},
    )

    assert final["final_verdict"] == "Needs Data"
    assert final["paper_trade_eligible"] is False


def test_agent_queue_and_portfolio_action_plan_are_generated():
    buy_finder = build_buy_finder(
        [
            {
                "symbol": "NVDA",
                "score": 82,
                "growth_score": 80,
                "return_pct": 9,
                "volatility_pct": 22,
                "recommendation_gate": "Trusted",
                "data_confidence": "High",
            },
            {
                "symbol": "PLTR",
                "score": 68,
                "growth_score": 70,
                "return_pct": 4,
                "volatility_pct": 24,
                "recommendation_gate": "Blocked",
                "data_confidence": "Low",
                "theme": "AI software",
            },
        ],
        {},
        {"market_risk_level": "Moderate"},
        {"cash": 10000, "monthly_income": 5000, "monthly_expenses": 3000, "emergency_fund": 18000},
        [],
        {},
    )
    plan = build_portfolio_action_plan(
        buy_finder["all_rows"],
        [],
        {"cash": 10000, "max_single_stock_exposure": 15},
        {"market_risk_level": "Moderate"},
    )
    tasks = generate_agent_research_tasks(buy_finder["all_rows"], [], plan)

    assert any(row["portfolio_action"] == "Buy Candidate" for row in plan["actions"])
    assert any(task["assigned_agent_role"] == "Data Quality Agent" for task in tasks["tasks"])

