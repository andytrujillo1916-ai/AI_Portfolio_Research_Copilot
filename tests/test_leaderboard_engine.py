from leaderboard_engine import build_strategy_leaderboard


def test_leaderboard_builds_ranked_rows():
    walk_forward = {
        "win_rate_vs_spy": 60,
        "average_alpha_vs_spy": 1.5,
        "window_results": [
            {"portfolio_return_pct": 4.0, "alpha_vs_spy_pct": 1.2},
            {"portfolio_return_pct": -2.0, "alpha_vs_spy_pct": -0.8},
        ],
    }
    prediction_eval = {
        "hit_rate": 55,
        "average_return": 0.8,
        "alpha_vs_benchmark": 0.3,
        "avg_drawdown_after_signal": 6.0,
    }
    run_eval = {
        "total_runs": 3,
        "average_realized_return": 1.1,
        "best_run": {"realized_return_pct": 3.0},
        "worst_run": {"realized_return_pct": -2.0},
        "recent_evaluated_runs": [
            {"realized_return_pct": 3.0},
            {"realized_return_pct": -1.0},
            {"realized_return_pct": 1.2},
        ],
    }

    result = build_strategy_leaderboard(
        walk_forward,
        prediction_evaluations=prediction_eval,
        research_run_evaluations=run_eval,
    )

    assert "leaderboard" in result
    assert len(result["leaderboard"]) == 3
    assert result["leaderboard"][0]["rank"] == 1
    assert result["top_performer"]
    assert result["worst_performer"]


def test_leaderboard_handles_missing_data():
    result = build_strategy_leaderboard({}, None, None)
    assert result["leaderboard"] == []
    assert "learning_summary" in result
