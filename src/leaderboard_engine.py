def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _consistency_score(win_rate, avg_alpha, avg_return, max_drawdown):
    score = 50.0
    score += (_safe_float(win_rate) - 50.0) * 0.35
    score += _safe_float(avg_alpha) * 2.0
    score += _safe_float(avg_return) * 1.2
    score -= abs(_safe_float(max_drawdown)) * 0.6
    return round(max(0.0, min(100.0, score)), 2)


def _build_strategy_row(walk_forward_results):
    windows = (walk_forward_results or {}).get("window_results", [])
    win_rate = _safe_float((walk_forward_results or {}).get("win_rate_vs_spy", 0.0))
    avg_alpha = _safe_float((walk_forward_results or {}).get("average_alpha_vs_spy", 0.0))

    returns = [_safe_float(row.get("portfolio_return_pct", 0.0)) for row in windows]
    avg_return = sum(returns) / len(returns) if returns else 0.0
    max_drawdown = min(returns) if returns else 0.0
    consistency = _consistency_score(win_rate, avg_alpha, avg_return, max_drawdown)

    return {
        "name": "Walk-Forward Portfolio Selection",
        "type": "Strategy",
        "win_rate": round(win_rate, 2),
        "avg_return": round(avg_return, 2),
        "avg_alpha": round(avg_alpha, 2),
        "max_drawdown": round(max_drawdown, 2),
        "consistency_score": consistency,
        "rank": 0,
        "summary": "Rolling train/test portfolio selection compared to SPY.",
    }


def _build_signal_row(prediction_evaluations):
    prediction_evaluations = prediction_evaluations or {}
    win_rate = _safe_float(prediction_evaluations.get("hit_rate", prediction_evaluations.get("win_rate", 0.0)))
    avg_return = _safe_float(prediction_evaluations.get("average_return", prediction_evaluations.get("avg_return_after_signal", 0.0)))
    avg_alpha = _safe_float(prediction_evaluations.get("alpha_vs_benchmark", 0.0))
    max_drawdown = _safe_float(prediction_evaluations.get("avg_drawdown_after_signal", 0.0)) * -1
    consistency = _consistency_score(win_rate, avg_alpha, avg_return, max_drawdown)

    return {
        "name": "Signal Accuracy Layer",
        "type": "Signal",
        "win_rate": round(win_rate, 2),
        "avg_return": round(avg_return, 2),
        "avg_alpha": round(avg_alpha, 2),
        "max_drawdown": round(max_drawdown, 2),
        "consistency_score": consistency,
        "rank": 0,
        "summary": "Signal hit-rate and return calibration across saved predictions.",
    }


def _build_mode_row(research_run_evaluations):
    research_run_evaluations = research_run_evaluations or {}
    total_runs = int(_safe_float(research_run_evaluations.get("total_runs", 0), 0))
    avg_return = _safe_float(research_run_evaluations.get("average_realized_return", 0.0))
    best_run = research_run_evaluations.get("best_run") or {}
    worst_run = research_run_evaluations.get("worst_run") or {}
    best_value = _safe_float(best_run.get("realized_return_pct", 0.0))
    worst_value = _safe_float(worst_run.get("realized_return_pct", 0.0))
    wins = 0
    for row in research_run_evaluations.get("recent_evaluated_runs", []):
        if _safe_float(row.get("realized_return_pct", 0.0)) > 0:
            wins += 1
    recent_count = len(research_run_evaluations.get("recent_evaluated_runs", []))
    win_rate = (wins / recent_count) * 100 if recent_count else (50.0 if total_runs else 0.0)
    max_drawdown = worst_value if total_runs else 0.0
    consistency = _consistency_score(win_rate, 0.0, avg_return, max_drawdown)

    return {
        "name": "Research Mode Outcomes",
        "type": "Research Mode",
        "win_rate": round(win_rate, 2),
        "avg_return": round(avg_return, 2),
        "avg_alpha": 0.0,
        "max_drawdown": round(max_drawdown, 2),
        "consistency_score": consistency,
        "rank": 0,
        "summary": "Realized outcomes from saved research runs by current workflow.",
    }


def build_strategy_leaderboard(
    walk_forward_results,
    prediction_evaluations=None,
    research_run_evaluations=None,
):
    """Rank Strategy, Signal, and Research Mode performance summaries."""
    leaderboard = []

    if walk_forward_results:
        leaderboard.append(_build_strategy_row(walk_forward_results))
    if prediction_evaluations:
        leaderboard.append(_build_signal_row(prediction_evaluations))
    if research_run_evaluations:
        leaderboard.append(_build_mode_row(research_run_evaluations))

    if not leaderboard:
        return {
            "leaderboard": [],
            "top_performer": {},
            "worst_performer": {},
            "learning_summary": "No historical inputs were available for leaderboard ranking.",
        }

    ranked = sorted(leaderboard, key=lambda row: row.get("consistency_score", 0.0), reverse=True)
    for idx, row in enumerate(ranked, start=1):
        row["rank"] = idx

    top = ranked[0]
    worst = ranked[-1]
    learning_summary = (
        f"Top performer: {top.get('name', 'N/A')} ({top.get('consistency_score', 0):.1f}). "
        f"Lowest performer: {worst.get('name', 'N/A')} ({worst.get('consistency_score', 0):.1f}). "
        "Use this ranking for research calibration only."
    )

    return {
        "leaderboard": ranked,
        "top_performer": top,
        "worst_performer": worst,
        "learning_summary": learning_summary,
    }
