from governance_engine import run_governance_review


def test_governance_flags_overconfidence_and_risk():
    review = run_governance_review(
        meta_decision={"final_verdict": "Research Candidate"},
        conviction_data={"conviction_score": 80},
        execution_data={"execution_score": 75},
        position_size_data={"recommended_position_pct": 12, "max_loss_tolerance_pct": 4},
        prediction_accuracy={
            "hit_rate": 42,
            "alpha_vs_benchmark": -1.5,
            "avg_drawdown_after_signal": 14,
            "total_predictions": 6,
            "total_runs": 4,
        },
        benchmark_data={"ai_outperformance_pct": -1.5},
        research_mode="Conservative",
    )
    assert review["governance_status"] in {"Needs Review", "High Risk"}
    assert review["evidence_quality"] in {"Low", "Medium", "High"}
    assert review["required_disclaimers"]
    assert review["approval_notes"]


def test_governance_always_requires_disclaimers():
    review = run_governance_review()
    assert "Research-only decision support; not financial advice." in review["required_disclaimers"]
