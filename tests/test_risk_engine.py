import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from risk_engine import calculate_position_size


class RiskEngineTests(unittest.TestCase):
    def test_high_confidence_low_volatility_uses_larger_risk_budget(self):
        result = calculate_position_size(
            symbol="AAPL",
            current_price=200.0,
            confidence=8,
            volatility_pct=12.0,
            total_portfolio_value=10000.0,
            current_symbol_exposure=0.0,
        )

        self.assertGreater(result["recommended_position_value"], 300.0)
        self.assertGreater(result["portfolio_risk_pct"], 0.03)

    def test_high_volatility_and_existing_exposure_reduce_size(self):
        result = calculate_position_size(
            symbol="AAPL",
            current_price=200.0,
            confidence=5,
            volatility_pct=40.0,
            total_portfolio_value=10000.0,
            current_symbol_exposure=2500.0,
        )

        self.assertLess(result["recommended_position_value"], 500.0)
        self.assertIn("volatility", " ".join(result["sizing_reasoning"]).lower())
        self.assertIn("exposure", " ".join(result["sizing_reasoning"]).lower())


if __name__ == "__main__":
    unittest.main()
