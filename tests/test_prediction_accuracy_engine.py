import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from prediction_accuracy_engine import evaluate_prediction_accuracy


def test_prediction_accuracy_returns_required_fields():
    predictions = [
        {
            "signal": "Watch",
            "realized_return": "5",
            "max_drawdown": "-4",
            "time_horizon": "1 month",
            "evaluation_label": "Strong Hit",
            "regime": "Bull Trend",
            "asset_class": "Stock",
        },
        {
            "signal": "Watch",
            "realized_return": "-2",
            "max_drawdown": "-8",
            "time_horizon": "1 month",
            "evaluation_label": "Miss",
            "regime": "High Volatility",
            "asset_class": "Stock",
        },
        {
            "signal": "Avoid",
            "realized_return": "-3",
            "max_drawdown": "-5",
            "time_horizon": "1 week",
            "evaluation_label": "Partial Hit",
            "regime": "Bear Trend",
            "asset_class": "ETF",
        },
    ]

    result = evaluate_prediction_accuracy(
        predictions,
        benchmark_returns={"best_benchmark": {"return_pct": 1}},
    )

    assert result["win_rate"] == 66.67
    assert result["avg_return_after_signal"] == 0
    assert result["false_positive_rate"] == 50
    assert result["alpha_vs_benchmark"] == -1
    assert result["best_holding_window"] in {"1 month", "1 week"}
    assert result["worst_holding_window"] in {"1 month", "1 week"}
    assert result["sample_confidence"] == "Not enough evidence"
    assert result["grouped_by_signal"]
    assert result["grouped_by_regime"]
    assert result["grouped_by_horizon"]
    assert result["grouped_by_asset_class"]
    assert "Research-only calibration" in result["disclaimer"]
    assert result["lessons"]


def test_prediction_accuracy_handles_empty_log():
    result = evaluate_prediction_accuracy([], benchmark_returns=2)

    assert result["win_rate"] == 0
    assert result["avg_return_after_signal"] == 0
    assert result["false_positive_rate"] == 0
    assert result["best_holding_window"] == "Not enough data"
    assert result["sample_confidence"] == "No evidence yet"
    assert "Save predictions first" in result["lessons"][0]
