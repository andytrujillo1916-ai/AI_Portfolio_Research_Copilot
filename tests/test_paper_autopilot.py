import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import paper_autopilot
from paper_autopilot import (
    build_autopilot_paper_ticket,
    build_paper_trade_checklist_markdown,
    run_daily_paper_autopilot,
)


def _agent_result(symbol, score=86, verdict="Buy Candidate", gate="Trusted", confidence="High", lane="Short Term"):
    return {
        "symbol": symbol,
        "final_verdict": verdict,
        "score": score,
        "lane": lane,
        "data_quality": {"recommendation_gate": gate, "data_confidence": confidence},
        "bull_case": ["Supportive signal"],
        "bear_case": ["Can fail"],
        "invalidation_triggers": ["Data gate becomes Blocked"],
    }


def test_autopilot_ticket_uses_dynamic_sizing_and_risk_cut():
    ticket = build_autopilot_paper_ticket(
        _agent_result("AAPL", score=86),
        {"price": 100},
        {"volatility_pct": 35, "max_drawdown_pct": -10},
        {"portfolio_value": 100000, "existing_trades": [], "today": "2026-05-31"},
    )

    assert ticket["paper_trade_eligible"] is True
    assert ticket["requested_allocation_pct"] == 2.5
    assert ticket["allocation_pct"] == 2.5
    assert ticket["quantity"] == 25


def test_autopilot_ticket_blocks_duplicate_same_day_buy():
    ticket = build_autopilot_paper_ticket(
        _agent_result("AAPL", score=86),
        {"price": 100},
        {"volatility_pct": 12, "max_drawdown_pct": -3},
        {
            "portfolio_value": 100000,
            "existing_trades": [{"symbol": "AAPL", "action": "buy", "date": "2026-05-31 09:30:00"}],
            "today": "2026-05-31",
        },
    )

    assert ticket["paper_trade_eligible"] is False
    assert any("Duplicate" in item for item in ticket["risk_controls_failed"])


def test_autopilot_ticket_respects_daily_exposure_cap():
    ticket = build_autopilot_paper_ticket(
        _agent_result("MSFT", score=90),
        {"price": 100},
        {"volatility_pct": 12, "max_drawdown_pct": -3},
        {
            "portfolio_value": 100000,
            "used_daily_allocation_pct": 9,
            "max_daily_allocation_pct": 10,
            "existing_trades": [],
            "today": "2026-05-31",
        },
    )

    assert ticket["allocation_pct"] == 1
    assert ticket["quantity"] == 10


def test_daily_autopilot_selects_top_three_and_skips_blocked(monkeypatch):
    def fake_runner(symbol, **kwargs):
        return _agent_result(symbol, score={"AAA": 90, "BBB": 80, "CCC": 72}.get(symbol, 60))

    monkeypatch.setattr(paper_autopilot, "get_market_snapshot", lambda symbol: {"price": 100})
    monkeypatch.setattr(
        paper_autopilot,
        "get_price_history",
        lambda symbol, period="1mo": {"data": {"Close": [100, 102, 104]}},
    )
    monkeypatch.setattr(
        paper_autopilot,
        "get_risk_metrics",
        lambda data: {"return_pct": 4, "volatility_pct": 10, "max_drawdown_pct": -2},
    )

    saved = []

    def fake_save(**kwargs):
        saved.append(kwargs)
        return {"date": "2026-05-31", **kwargs}

    result = run_daily_paper_autopilot(
        [
            {"symbol": "AAA", "score": 99, "recommendation_gate": "Trusted", "data_confidence": "High"},
            {"symbol": "BLOCK", "score": 98, "recommendation_gate": "Blocked", "data_confidence": "High"},
            {"symbol": "BBB", "score": 97, "recommendation_gate": "Trusted", "data_confidence": "High"},
            {"symbol": "CCC", "score": 96, "recommendation_gate": "Trusted", "data_confidence": "High"},
            {"symbol": "DDD", "score": 95, "recommendation_gate": "Trusted", "data_confidence": "High"},
        ],
        profile={},
        period="1mo",
        paper_context={"portfolio_value": 100000, "existing_trades": [], "today": "2026-05-31"},
        max_trades=3,
        agent_runner=fake_runner,
        save_trade_fn=fake_save,
        today="2026-05-31",
    )

    assert len(result["saved_trades"]) == 3
    assert [row["symbol"] for row in saved] == ["AAA", "BBB", "CCC"]
    assert any(row["symbol"] == "BLOCK" for row in result["skipped_candidates"])
    assert len(result["checklists"]) == 3


def test_paper_trade_checklist_contains_required_safety_language():
    ticket = build_autopilot_paper_ticket(
        _agent_result("AAPL", score=75),
        {"price": 100},
        {"volatility_pct": 12, "max_drawdown_pct": -4},
        {"portfolio_value": 100000, "existing_trades": [], "today": "2026-05-31"},
    )
    markdown = build_paper_trade_checklist_markdown(ticket, _agent_result("AAPL", score=75))

    assert "Paper Trade Checklist: AAPL" in markdown
    assert "Safety Gates Passed" in markdown
    assert "Research-Only Disclaimer" in markdown
    assert "No broker APIs" in markdown
