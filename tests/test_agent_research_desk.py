import json
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent_research_desk import (
    evaluate_agent_research_memory,
    generate_daily_agent_queue,
    run_agent_research_desk,
)
from db_service import load_agent_evidence, load_agent_runs, load_ticker_memory


def _fresh_history():
    now = datetime.now(timezone.utc)
    dates = [(now - timedelta(days=29 - i)).isoformat() for i in range(30)]
    prices = [100 + i for i in range(30)]
    return {
        "source": "sec_edgar",
        "error": "",
        "data": {"Date": dates, "Close": prices},
        "last_timestamp": datetime.now(timezone.utc).isoformat(),
        "is_fallback": False,
    }


def _fresh_snapshot(symbol="TST"):
    return {
        "symbol": symbol,
        "price": 129.0,
        "change_pct": 1.2,
        "volume": 1000000,
        "source": "sec_edgar",
        "error": "",
        "last_timestamp": datetime.now(timezone.utc).isoformat(),
        "is_fallback": False,
    }


def _supportive_inputs(symbol="TST"):
    risk = {"return_pct": 12.0, "volatility_pct": 12.0, "max_drawdown_pct": -4.0}
    news = {"market_sentiment": "Bullish", "event_tags": ["earnings"], "risk_flags": []}
    signal = {"signal": "Watch", "score": 82, "quant_score": 78, "news_score": 8}
    regime = {"regime": "Bull Trend"}
    fundamentals = {
        "fundamental_quality": "Supportive",
        "fundamental_score": 76,
        "summary": f"{symbol} fundamentals are supportive in test context.",
        "risk_flags": [],
    }
    return risk, news, signal, regime, fundamentals


def test_blocked_data_prevents_buy_or_add_verdict():
    risk, news, signal, regime, fundamentals = _supportive_inputs("MOCK")
    result = run_agent_research_desk(
        "MOCK",
        snapshot={"symbol": "MOCK", "price": 100, "source": "mock", "is_fallback": True},
        price_data={"source": "mock", "is_fallback": True, "data": {"Close": [99, 100]}},
        risk=risk,
        news_context=news,
        signal_data=signal,
        regime_data=regime,
        fundamentals=fundamentals,
        save_memory=False,
    )

    assert result["final_verdict"] == "Needs Data"
    assert result["lane"] == "Needs Data"
    assert result["data_quality"]["recommendation_gate"] == "Blocked"


def test_bull_bear_critic_always_outputs_both_sides_and_triggers():
    risk, news, signal, regime, fundamentals = _supportive_inputs("TST")
    result = run_agent_research_desk(
        "TST",
        snapshot=_fresh_snapshot("TST"),
        price_data=_fresh_history(),
        risk=risk,
        news_context=news,
        signal_data=signal,
        regime_data=regime,
        fundamentals=fundamentals,
        save_memory=False,
    )

    agent_names = {row["agent_name"] for row in result["agent_evidence"]}
    assert "Bull/Bear Critic" in agent_names
    assert result["bull_case"]
    assert result["bear_case"]
    assert result["invalidation_triggers"]


def test_agent_memory_saves_and_reloads_structured_and_narrative_rows():
    symbol = "MEMTST"
    risk, news, signal, regime, fundamentals = _supportive_inputs(symbol)
    result = run_agent_research_desk(
        symbol,
        snapshot=_fresh_snapshot(symbol),
        price_data=_fresh_history(),
        risk=risk,
        news_context=news,
        signal_data=signal,
        regime_data=regime,
        fundamentals=fundamentals,
        save_memory=True,
    )

    memory = load_ticker_memory(symbol)
    runs = load_agent_runs(symbol=symbol, limit=5)
    evidence = load_agent_evidence(run_id=result["run_id"])

    assert memory["symbol"] == symbol
    assert memory["last_verdict"] == result["final_verdict"]
    assert runs
    assert evidence


def test_agent_evaluation_adjusts_confidence_within_bounds():
    weak = evaluate_agent_research_memory(
        agent_runs=[],
        evidence_rows=[],
        recommendation_log=[
            {
                "action": "Buy Candidate",
                "horizon": "Short Term",
                "realized_return_pct": -3,
                "engine_inputs": json.dumps({"lane": "Short Term", "data_confidence": "High"}),
            }
        ],
    )
    strong = evaluate_agent_research_memory(
        agent_runs=[],
        evidence_rows=[],
        recommendation_log=[
            {
                "action": "Buy Candidate",
                "horizon": "Long Term",
                "realized_return_pct": 2,
                "engine_inputs": json.dumps({"lane": "Long Term", "data_confidence": "High"}),
            }
            for _ in range(5)
        ],
    )

    assert weak["confidence_adjustment"] < 0
    assert 0 < strong["confidence_adjustment"] <= 10
    assert strong["lane_stats"][0]["lane"] == "Long Term"


def test_daily_queue_keeps_futures_proxy_research_proxy_only():
    queue = generate_daily_agent_queue(
        [
            {
                "symbol": "SPY",
                "score": 78,
                "volatility_pct": 10,
                "max_drawdown_pct": -4,
                "data_confidence": "High",
                "recommendation_gate": "Trusted",
            }
        ],
        limit=1,
    )

    assert queue["queue"][0]["symbol"] == "SPY"
    assert queue["queue"][0]["lane"] == "Futures Proxy"
    assert "Proxy-only" in queue["queue"][0]["reason"]
