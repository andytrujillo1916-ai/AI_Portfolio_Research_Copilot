from auto_paper_trader import build_auto_paper_trade_ticket
from final_recommendation_engine import build_final_recommendation
from ipo_research_engine import generate_ipo_research_context


def test_conflicting_buy_and_blocked_data_becomes_watch():
    final = build_final_recommendation(
        "MSFT",
        [{"engine": "Signal", "action": "Buy Candidate", "score": 90}],
        {"score": 90},
        {"recommendation_gate": "Blocked", "data_confidence": "Low"},
        {"status": "Ready for selective investing"},
        {"confidence_adjustment": 0},
    )

    assert final["final_verdict"] == "Watch"
    assert final["paper_trade_eligible"] is False
    assert final["conflict_rows"][0]["engine_view"] == "Buy Candidate"


def test_overweight_holding_trims_even_with_strong_signal():
    final = build_final_recommendation(
        "AAPL",
        [{"engine": "Signal", "action": "Buy Candidate", "score": 85}],
        {"score": 85, "current_exposure_pct": 40, "max_single_stock_exposure": 15, "has_position": True},
        {"recommendation_gate": "Trusted", "data_confidence": "High"},
        {"status": "Ready for selective investing"},
        {"confidence_adjustment": 0},
    )

    assert final["final_verdict"] == "Trim"


def test_ipo_without_listing_is_research_only_watch():
    ipo = generate_ipo_research_context("Databricks")["selected_ipo"]
    final = build_final_recommendation(
        "Databricks",
        [{"engine": "IPO", "action": "Buy Candidate", "score": 80}],
        {"score": 80},
        {"recommendation_gate": "Trusted", "data_confidence": "High"},
        {"status": "Ready for selective investing"},
        {"confidence_adjustment": 0},
        ipo_context=ipo,
    )

    assert ipo["research_only"] is True
    assert final["final_verdict"] == "Watch"
    assert final["paper_trade_eligible"] is False


def test_auto_paper_ticket_requires_final_verdict_eligibility():
    ticket = build_auto_paper_trade_ticket(
        "MSFT",
        {"price": 100},
        {"final_verdict": "Research Candidate"},
        {"readiness_level": "Ready for Paper Trade"},
        {"recommended_position_pct": 5, "recommended_position_value": 1000},
        {"recommended_action": "Enter"},
        {"exposure_status": "Moderate"},
        {"diversification_score": 70},
        {"best_benchmark": {"symbol": "SPY"}},
        data_confidence="High",
        final_recommendation={"final_verdict": "Watch", "paper_trade_eligible": False},
    )

    assert ticket["paper_trade_eligible"] is False
    assert ticket["paper_trade_action"] == "none"


def test_auto_paper_ticket_uses_final_verdict_as_source_of_truth():
    ticket = build_auto_paper_trade_ticket(
        "MSFT",
        {"price": 100},
        {"final_verdict": "Watch"},
        {"readiness_level": "Ready for Paper Trade"},
        {"recommended_position_pct": 5, "recommended_position_value": 1000},
        {"recommended_action": "Watch"},
        {"exposure_status": "Moderate"},
        {"diversification_score": 70},
        {"best_benchmark": {"symbol": "SPY"}},
        data_confidence="High",
        final_recommendation={"final_verdict": "Buy Candidate", "paper_trade_eligible": True},
    )

    assert ticket["paper_trade_action"] == "buy"
    assert ticket["final_verdict"] == "Buy Candidate"
