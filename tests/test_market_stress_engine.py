import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from market_stress_engine import analyze_market_stress


def _history(values, source="test", is_fallback=False):
    return {
        "source": source,
        "is_fallback": is_fallback,
        "error": "",
        "data": {"Close": values},
    }


def test_market_stress_normal_with_constructive_proxy_data():
    def loader(symbol, period="3mo"):
        if symbol == "^VIX":
            return _history([20, 19, 18, 17, 16, 15])
        return _history([100, 101, 102, 103, 104, 105])

    result = analyze_market_stress(price_history_loader=loader)

    assert result["risk_posture"] == "Normal"
    assert result["breadth_pct"] == 100
    assert result["fallback_count"] == 0
    assert "hypothesis testing only" in result["disclaimer"]


def test_market_stress_flags_stress_with_weak_risk_on_and_rising_vix():
    def loader(symbol, period="3mo"):
        if symbol in {"TLT", "GLD"}:
            return _history([100, 103, 106, 109, 112, 115])
        if symbol == "^VIX":
            return _history([15, 18, 22, 27, 32, 38])
        return _history([120, 112, 104, 96, 88, 80])

    result = analyze_market_stress(price_history_loader=loader)

    assert result["risk_posture"] == "Stress"
    assert result["breadth_pct"] == 0
    assert result["defensive_rotation"] is True
    assert result["credit_risk_proxy"] == "Weakening"


def test_market_stress_needs_more_data_when_loader_fails():
    def loader(symbol, period="3mo"):
        raise ValueError("no data")

    result = analyze_market_stress(price_history_loader=loader)

    assert result["risk_posture"] == "Needs More Data"
    assert result["fallback_count"] == len(result["rows"])
    assert all(row["source"] == "error" for row in result["rows"])
