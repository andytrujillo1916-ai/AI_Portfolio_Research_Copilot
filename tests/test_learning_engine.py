import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from learning_engine import analyze_signal_effectiveness


class LearningEngineTests(unittest.TestCase):
    def test_learning_engine_returns_ranked_factors_and_signal_stats(self):
        predictions = [
            {
                "signal": "Watch",
                "score": 82,
                "quant_score": 75,
                "news_score": 7,
                "volatility": 18,
                "max_drawdown": -7,
                "backtest_return": 5.5,
                "suggested_action": "Buy",
                "realized_return_pct": 4.2,
                "correct_direction": True,
            },
            {
                "signal": "Watch",
                "score": 68,
                "quant_score": 60,
                "news_score": 8,
                "volatility": 22,
                "max_drawdown": -12,
                "backtest_return": 2.0,
                "suggested_action": "Watch",
                "realized_return_pct": 1.1,
                "correct_direction": True,
            },
            {
                "signal": "Avoid",
                "score": 28,
                "quant_score": 24,
                "news_score": -4,
                "volatility": 35,
                "max_drawdown": -24,
                "backtest_return": -2.0,
                "suggested_action": "Sell",
                "realized_return_pct": -3.5,
                "correct_direction": True,
            },
            {
                "signal": "Caution",
                "score": 46,
                "quant_score": 40,
                "news_score": 6,
                "volatility": 30,
                "max_drawdown": -18,
                "backtest_return": -1.0,
                "suggested_action": "Watch",
                "realized_return_pct": -2.2,
                "correct_direction": False,
            },
        ]

        result = analyze_signal_effectiveness(predictions)

        self.assertIn("score", result["top_positive_factors"])
        self.assertIn("max_drawdown", result["top_negative_factors"])
        self.assertIn("Buy", result["hit_rate_by_signal_type"])
        self.assertIn("Buy", result["avg_return_by_signal_type"])
        self.assertIn("research-only", result["learning_summary"].lower())


if __name__ == "__main__":
    unittest.main()
