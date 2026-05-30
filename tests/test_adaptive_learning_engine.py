import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from adaptive_learning_engine import calculate_factor_insights


class AdaptiveLearningEngineTests(unittest.TestCase):
    def test_calculate_factor_insights_returns_adjustments_and_confidence(self):
        predictions = [
            {
                "signal": "Watch",
                "quant_score": 78,
                "news_score": 8,
                "volatility": 18,
                "max_drawdown": -6,
                "backtest_return": 4.5,
                "suggested_action": "Buy",
                "realized_return": 3.0,
                "evaluation_label": "Strong Hit",
            },
            {
                "signal": "Avoid",
                "quant_score": 30,
                "news_score": -4,
                "volatility": 36,
                "max_drawdown": -24,
                "backtest_return": -2.0,
                "suggested_action": "Sell",
                "realized_return": -4.0,
                "evaluation_label": "Miss",
            },
        ]

        research_runs = [
            {
                "symbol": "AAPL",
                "regime": "Bull Trend",
                "signal_score": 78,
                "exposure_level": "Low",
                "trade_decision": "Buy",
            },
            {
                "symbol": "AAPL",
                "regime": "High Volatility",
                "signal_score": 30,
                "exposure_level": "High",
                "trade_decision": "Buy",
            },
        ]

        result = calculate_factor_insights(predictions, research_runs)

        self.assertGreaterEqual(result["learning_confidence"], 3)
        self.assertIn("news_score", result["suggested_weight_adjustments"])
        self.assertIn("volatility", result["suggested_weight_adjustments"])
        self.assertIn("strong_positive_factors", result)
        self.assertIn("weak_negative_factors", result)
        self.assertIn("reviewable_adjustments", result)
        self.assertIn("disclaimer", result)
        for adjustment in result["suggested_weight_adjustments"].values():
            self.assertGreaterEqual(adjustment, 0.85)
            self.assertLessEqual(adjustment, 1.10)
        self.assertIn("human review", result["disclaimer"].lower())


if __name__ == "__main__":
    unittest.main()
