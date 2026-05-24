import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from research_run_log import evaluate_research_runs, save_research_run


class ResearchRunEvaluationTests(unittest.TestCase):
    def test_evaluate_research_runs_returns_summary_for_selected_symbol(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = os.path.join(tmp_dir, "research_runs.csv")

            save_research_run(
                symbol="AAPL",
                price=100.0,
                return_pct=3.0,
                volatility_pct=18.0,
                max_drawdown_pct=-8.0,
                regime="Bull Trend",
                signal="Watch",
                signal_score=72,
                exposure_level="Low",
                trade_decision="Buy",
                research_summary="Bullish research summary.",
                csv_path=csv_path,
            )
            save_research_run(
                symbol="AAPL",
                price=120.0,
                return_pct=4.0,
                volatility_pct=20.0,
                max_drawdown_pct=-10.0,
                regime="Bull Trend",
                signal="Strong Watch",
                signal_score=84,
                exposure_level="Medium",
                trade_decision="Buy",
                research_summary="Strong upside research summary.",
                csv_path=csv_path,
            )

            result = evaluate_research_runs("AAPL", 130.0, csv_path=csv_path)

            self.assertEqual(result["total_runs"], 2)
            self.assertEqual(result["best_run"]["symbol"], "AAPL")
            self.assertEqual(result["worst_run"]["symbol"], "AAPL")
            self.assertEqual(len(result["recent_evaluated_runs"]), 2)
            self.assertIn(result["recent_evaluated_runs"][0]["outcome"], {"Positive", "Flat", "Negative"})


if __name__ == "__main__":
    unittest.main()
