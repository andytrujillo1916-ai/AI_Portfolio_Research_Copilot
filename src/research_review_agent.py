def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _status_from_signals(hit_rate, avg_alpha, avg_return):
    if hit_rate == 0 and avg_alpha == 0 and avg_return == 0:
        return "Insufficient Data"
    if hit_rate >= 55 and avg_alpha >= 0:
        return "Improving"
    if hit_rate >= 45 and avg_alpha > -1:
        return "Stable"
    return "Needs Work"


def generate_research_review(
    prediction_summary=None,
    research_run_summary=None,
    experiment_summary=None,
    leaderboard_summary=None,
    portfolio_performance=None,
):
    """Generate a research-only system review with next-step recommendations."""
    prediction_summary = prediction_summary or {}
    research_run_summary = research_run_summary or {}
    experiment_summary = experiment_summary or {}
    leaderboard_summary = leaderboard_summary or {}
    portfolio_performance = portfolio_performance or {}

    hit_rate = _safe_float(
        prediction_summary.get("hit_rate", prediction_summary.get("win_rate", 0.0))
    )
    avg_alpha = _safe_float(
        prediction_summary.get("alpha_vs_benchmark", leaderboard_summary.get("average_alpha_vs_spy", 0.0))
    )
    avg_return = _safe_float(
        prediction_summary.get("average_return", prediction_summary.get("avg_return_after_signal", 0.0))
    )
    avg_drawdown = abs(
        _safe_float(
            prediction_summary.get("avg_drawdown_after_signal", portfolio_performance.get("drawdown_pct", 0.0))
        )
    )
    total_runs = int(_safe_float(research_run_summary.get("total_runs", 0), 0))
    total_experiments = int(_safe_float(experiment_summary.get("total_experiments", 0), 0))

    working = []
    not_working = []
    risks = []
    recommended = []
    notes = []

    if hit_rate >= 55:
        working.append(f"Signal hit rate is currently supportive at {hit_rate:.1f}%.")
    elif hit_rate > 0:
        not_working.append(f"Signal hit rate is weak at {hit_rate:.1f}%; rules need calibration.")
        recommended.append("Refine signal rules and compare simpler baseline thresholds.")

    if avg_alpha >= 0:
        working.append(f"Average alpha is non-negative at {avg_alpha:+.2f}%.")
    else:
        not_working.append(f"Average alpha is negative at {avg_alpha:+.2f}%.")
        recommended.append("Improve benchmark-relative filtering before promoting candidates.")

    if avg_drawdown >= 12:
        risks.append(f"Average drawdown risk is elevated at {avg_drawdown:.2f}%.")
        recommended.append("Tune risk/exposure controls and tighten position sizing under volatility.")
    elif avg_drawdown > 0:
        working.append(f"Drawdown is currently moderate at {avg_drawdown:.2f}%.")

    if total_experiments == 0:
        not_working.append("No tracked experiments yet; learning loop is incomplete.")
        recommended.append("Track planned strategy changes in Experiment Tracker with before/after metrics.")
    else:
        status_counts = experiment_summary.get("status_counts", {})
        completed = int(_safe_float(status_counts.get("Completed", 0), 0))
        if completed == 0:
            not_working.append("Experiments are mostly inconclusive (no completed results).")
            recommended.append("Complete at least 2 experiments with explicit metrics_before/metrics_after.")
        else:
            working.append(f"Experiment tracking is active with {completed} completed experiments.")

    if total_runs < 5:
        risks.append("Research run sample is small; conclusions are fragile.")
        recommended.append("Collect more paper-trading/research runs before claiming persistent edge.")

    leaderboard_rows = leaderboard_summary.get("leaderboard", [])
    if leaderboard_rows:
        top = leaderboard_summary.get("top_performer", {})
        notes.append(
            f"Top current approach: {top.get('name', 'N/A')} ({top.get('consistency_score', 0):.1f} consistency)."
        )
    else:
        notes.append("Leaderboard depth is limited; continue walk-forward and prediction logging.")

    if not working:
        working.append("Core data pipeline is functioning and producing evaluable research outputs.")
    if not not_working:
        not_working.append("No major failure cluster detected, but confidence remains limited by sample size.")
    if not risks:
        risks.append("No acute risk spike detected from current summaries, but uncertainty remains.")
    if not recommended:
        recommended.append("Continue controlled experiments and monitor benchmark-relative drift.")

    status = _status_from_signals(hit_rate, avg_alpha, avg_return)
    summary = (
        f"System status: {status}. "
        f"Hit rate {hit_rate:.1f}%, alpha {avg_alpha:+.2f}%, "
        f"tracked runs {total_runs}, tracked experiments {total_experiments}."
    )

    return {
        "overall_system_status": status,
        "what_is_working": working,
        "what_is_not_working": not_working,
        "biggest_risks": risks,
        "recommended_next_experiments": recommended,
        "developer_notes": notes,
        "summary": summary,
    }
