import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pandas as pd

from regime_engine import detect_market_regime


class RegimeEngineTests(unittest.TestCase):
    def test_detects_bull_trend_for_positive_returns_and_low_volatility(self):
        price_data = pd.DataFrame(
            {
                "Date": pd.date_range("2026-01-01", periods=8),
                "Close": [100, 101, 103, 105, 106, 108, 110, 112],
            }
        )
        result = detect_market_regime(
            price_data,
            {"return_pct": 12.0, "volatility_pct": 12.0, "max_drawdown_pct": -4.0},
        )

        self.assertEqual(result["regime"], "Bull Trend")
        self.assertGreaterEqual(result["confidence"], 6)
        self.assertIn("trend-following", result["strategy_bias"].lower())

    def test_detects_high_volatility_when_volatility_is_extreme(self):
        price_data = pd.DataFrame(
            {
                "Date": pd.date_range("2026-01-01", periods=8),
                "Close": [100, 98, 104, 96, 108, 92, 110, 90],
            }
        )
        result = detect_market_regime(
            price_data,
            {"return_pct": -2.0, "volatility_pct": 40.0, "max_drawdown_pct": -12.0},
        )

        self.assertEqual(result["regime"], "High Volatility")
        self.assertIn("reduce confidence", result["risk_note"].lower())


if __name__ == "__main__":
    unittest.main()
