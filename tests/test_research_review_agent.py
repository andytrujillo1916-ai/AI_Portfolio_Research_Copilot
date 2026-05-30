from research_review_agent import generate_research_review


def test_research_review_agent_flags_risks_and_recommendations():
    review = generate_research_review(
        prediction_summary={"hit_rate": 40, "alpha_vs_benchmark": -1.2, "average_return": -0.5},
        research_run_summary={"total_runs": 2},
        experiment_summary={"total_experiments": 1, "status_counts": {"Planned": 1}},
        leaderboard_summary={},
        portfolio_performance={"drawdown_pct": -15},
    )

    assert review["overall_system_status"] in {"Needs Work", "Stable", "Improving", "Insufficient Data"}
    assert review["what_is_not_working"]
    assert review["biggest_risks"]
    assert review["recommended_next_experiments"]


def test_research_review_agent_handles_insufficient_data():
    review = generate_research_review()
    assert review["overall_system_status"] == "Insufficient Data"
    assert "summary" in review
