import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from market_microstructure_engine import build_microstructure_context, classify_intraday_window
from trade_operations_engine import build_order_intent, build_trade_plan


def _quality():
    return {"recommendation_gate": "Trusted", "data_confidence": "High", "source": "broker_paper"}


def test_intraday_windows_classify_open_midday_power_hour_and_close():
    assert classify_intraday_window(datetime(2026, 6, 1, 9, 35))["window"] == "Open"
    assert classify_intraday_window(datetime(2026, 6, 1, 12, 15))["window"] == "Midday Lull"
    assert classify_intraday_window(datetime(2026, 6, 1, 15, 15))["window"] == "Power Hour"
    assert classify_intraday_window(datetime(2026, 6, 1, 15, 50))["window"] == "Closing Auction"


def test_high_spread_blocks_paper_intent():
    micro = build_microstructure_context(
        "TST",
        snapshot={"symbol": "TST", "price": 100, "volume": 1000000},
        quote_data={"bid": 99, "ask": 101, "last_price": 100, "last_timestamp": "2026-06-01T15:50:00-04:00"},
        now=datetime(2026, 6, 1, 15, 50),
        data_quality=_quality(),
    )
    plan = build_trade_plan(
        "TST",
        {"symbol": "TST", "price": 100},
        {"final_verdict": "Buy Candidate", "confidence": "High"},
        {"entry_zone": "Favorable Entry Zone", "stop_loss_guidance_pct": 6},
        {"recommended_position_pct": 2.0},
        {"volatility_pct": 10, "max_drawdown_pct": -3},
        _quality(),
        market_timing={"market_risk_level": "Moderate"},
        microstructure_context=micro,
    )
    intent = build_order_intent(plan, snapshot={"price": 100})

    assert micro["paper_trade_allowed"] is False
    assert plan["status"] == "Needs Data"
    assert intent["intent_type"] == "none"


def test_close_timing_cannot_override_market_risk_gate():
    micro = build_microstructure_context(
        "TST",
        snapshot={"symbol": "TST", "price": 100, "volume": 1000000},
        quote_data={"bid": 99.99, "ask": 100.01, "last_price": 100, "last_timestamp": "2026-06-01T15:50:00-04:00"},
        now=datetime(2026, 6, 1, 15, 50),
        data_quality=_quality(),
    )
    plan = build_trade_plan(
        "TST",
        {"symbol": "TST", "price": 100},
        {"final_verdict": "Buy Candidate", "confidence": "High"},
        {"entry_zone": "Favorable Entry Zone", "stop_loss_guidance_pct": 6},
        {"recommended_position_pct": 2.0},
        {"volatility_pct": 10, "max_drawdown_pct": -3},
        _quality(),
        market_timing={"market_risk_level": "High"},
        microstructure_context=micro,
    )

    assert micro["timing_bias"] == "Prefer Close Review"
    assert plan["status"] == "Wait for Pullback"


def test_calendar_context_never_creates_buy_by_itself():
    micro = build_microstructure_context(
        "TST",
        snapshot={"symbol": "TST", "price": 100, "volume": 1000000},
        quote_data={"bid": 99.99, "ask": 100.01, "last_price": 100, "last_timestamp": "2026-06-01T15:50:00-04:00"},
        now=datetime(2026, 6, 1, 15, 50),
        data_quality=_quality(),
    )
    plan = build_trade_plan(
        "TST",
        {"symbol": "TST", "price": 100},
        {"final_verdict": "Watch", "confidence": "Low"},
        {"entry_zone": "Favorable Entry Zone", "stop_loss_guidance_pct": 6},
        {"recommended_position_pct": 2.0},
        {"volatility_pct": 10, "max_drawdown_pct": -3},
        _quality(),
        market_timing={"market_risk_level": "Moderate"},
        microstructure_context=micro,
    )

    assert micro["microstructure_score"] >= 50
    assert plan["status"] == "Watch"
    assert plan["final_verdict"] == "Watch"
