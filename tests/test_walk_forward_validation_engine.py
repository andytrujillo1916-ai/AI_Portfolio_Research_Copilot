from walk_forward_engine import run_walk_forward_validation


def test_walk_forward_validation_returns_expected_keys():
    result = run_walk_forward_validation(
        watchlist=["AAPL", "MSFT", "NVDA", "SPY"],
        research_mode="Balanced",
        train_window_days=40,
        test_window_days=10,
        period="1y",
    )
    required = {
        "total_windows",
        "win_rate_vs_spy",
        "average_alpha_vs_spy",
        "best_window",
        "worst_window",
        "window_results",
        "summary",
    }
    assert required.issubset(result.keys())
    assert isinstance(result["window_results"], list)


def test_walk_forward_validation_handles_short_inputs_gracefully():
    result = run_walk_forward_validation(
        watchlist=[],
        research_mode="Balanced",
        train_window_days=200,
        test_window_days=50,
        period="1mo",
    )
    assert result["total_windows"] == 0
    assert "summary" in result
