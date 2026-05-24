import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from trade_decision_assistant import generate_trade_decision


class TradeDecisionAssistantTests(unittest.TestCase):
    def test_strong_bullish_context_recommends_buy(self):
        result = generate_trade_decision(
            "AAPL",
            {"price": 100.0, "change_pct": 1.5},
            {"volatility_pct": 16.0, "max_drawdown_pct": -8.0},
            {"score": 82},
            {"market_sentiment": "Bullish", "event_tags": [], "risk_flags": []},
            {"strategy_return_pct": 6.0, "buy_and_hold_return_pct": 3.0},
            {"total_shares": 0},
        )

        self.assertEqual(result["suggested_action"], "Buy")
        self.assertGreaterEqual(result["confidence"], 7)

    def test_bearish_news_with_supportive_context_uses_watch(self):
        result = generate_trade_decision(
            "AAPL",
            {"price": 100.0, "change_pct": 1.5},
            {"volatility_pct": 16.0, "max_drawdown_pct": -8.0},
            {"score": 72},
            {"market_sentiment": "Bearish", "event_tags": [], "risk_flags": ["headline"]},
            {"strategy_return_pct": 5.0, "buy_and_hold_return_pct": 2.0},
            {"total_shares": 0},
        )

        self.assertEqual(result["suggested_action"], "Watch")

    def test_existing_position_recommends_hold(self):
        result = generate_trade_decision(
            "AAPL",
            {"price": 100.0, "change_pct": 1.5},
            {"volatility_pct": 16.0, "max_drawdown_pct": -8.0},
            {"score": 88},
            {"market_sentiment": "Bullish", "event_tags": [], "risk_flags": []},
            {"strategy_return_pct": 7.0, "buy_and_hold_return_pct": 4.0},
            {"total_shares": 3},
        )

        self.assertEqual(result["suggested_action"], "Hold")


if __name__ == "__main__":
    unittest.main()
