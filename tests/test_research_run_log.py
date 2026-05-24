import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from research_run_log import load_research_runs, save_research_run


class ResearchRunLogTests(unittest.TestCase):
    def test_save_and_load_research_run_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = os.path.join(tmp_dir, "research_runs.csv")

            save_research_run(
                symbol="AAPL",
                price=200.0,
                return_pct=3.5,
                volatility_pct=18.0,
                max_drawdown_pct=-8.0,
                regime="Bull Trend",
                signal="Watch",
                signal_score=78,
                exposure_level="Low",
                trade_decision="Buy",
                research_summary="Bullish trend with moderate risk.",
                csv_path=csv_path,
            )

            runs = load_research_runs(csv_path=csv_path)

            self.assertEqual(len(runs), 1)
            self.assertEqual(runs[0]["symbol"], "AAPL")
            self.assertEqual(runs[0]["signal"], "Watch")
            self.assertEqual(runs[0]["trade_decision"], "Buy")
            self.assertEqual(runs[0]["exposure_level"], "Low")


if __name__ == "__main__":
    unittest.main()
