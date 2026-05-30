import json


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _avg(values):
    values = [value for value in values if value is not None]
    return sum(values) / len(values) if values else 0.0


def _label_is_win(row):
    label = str(row.get("outcome_label", "")).lower()
    if label in {"win", "good", "profitable", "positive"}:
        return True
    if label in {"loss", "poor", "bad", "negative"}:
        return False
    return _safe_float(row.get("realized_return_pct")) > 0


def _engine_inputs(row):
    value = row.get("engine_inputs", {})
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def evaluate_recommendation_accuracy(recommendation_log, benchmark_data=None, current_prices=None):
    """Evaluate which recommendations, horizons, and sectors are working."""
    recommendation_log = recommendation_log or []
    benchmark_data = benchmark_data or {}
    current_prices = current_prices or {}

    evaluated = []
    for row in recommendation_log:
        realized = row.get("realized_return_pct")
        if realized in {None, ""} and row.get("price") and row.get("symbol") in current_prices:
            entry_price = _safe_float(row.get("price"))
            current_price = _safe_float(current_prices.get(row.get("symbol")))
            if entry_price > 0 and current_price > 0:
                realized = ((current_price - entry_price) / entry_price) * 100
        if realized in {None, ""}:
            continue
        merged = dict(row)
        inputs = _engine_inputs(merged)
        merged["realized_return_pct"] = _safe_float(realized)
        merged["is_win"] = _label_is_win(merged)
        merged["lane"] = inputs.get("lane") or merged.get("horizon") or "Unknown"
        merged["data_confidence"] = inputs.get("data_confidence") or merged.get("data_gate") or "Unknown"
        merged["news_sentiment"] = inputs.get("news_sentiment") or "Unknown"
        merged["fundamental_quality"] = inputs.get("fundamental_quality") or "Unknown"
        merged["entry_state"] = inputs.get("entry_state") or merged.get("action") or "Unknown"
        evaluated.append(merged)

    if not evaluated:
        return {
            "total_recommendations": len(recommendation_log),
            "evaluated_count": 0,
            "hit_rate": 0.0,
            "average_return_pct": 0.0,
            "average_alpha_pct": 0.0,
            "average_drawdown_pct": 0.0,
            "false_positive_count": 0,
            "false_negative_count": 0,
            "best_holding_window": "Not enough evaluated data",
            "best_timeframe": "Unknown",
            "best_sector": "Unknown",
            "best_signal_type": "Unknown",
            "worst_recurring_mistake": "Not enough evaluated data",
            "confidence_adjustment": 0.0,
            "horizon_stats": [],
            "lane_stats": [],
            "sector_stats": [],
            "data_confidence_stats": [],
            "factor_stats": [],
            "summary": "No evaluated recommendation outcomes yet. Save recommendations and update outcomes to enable learning.",
        }

    wins = [row for row in evaluated if row["is_win"]]
    losses = [row for row in evaluated if not row["is_win"]]
    hit_rate = (len(wins) / len(evaluated)) * 100
    avg_return = _avg([row.get("realized_return_pct") for row in evaluated])
    avg_alpha = _avg([row.get("alpha_vs_benchmark_pct") for row in evaluated])
    avg_drawdown = _avg([abs(_safe_float(row.get("max_drawdown_after_signal"))) for row in evaluated])

    false_positive_count = sum(
        1
        for row in evaluated
        if row.get("action") in {"Buy Candidate", "Add"} and row.get("realized_return_pct", 0) < 0
    )
    false_negative_count = sum(
        1
        for row in evaluated
        if row.get("action") in {"Sell Candidate", "Avoid", "Keep Cash"} and row.get("realized_return_pct", 0) > 0
    )

    def grouped_stats(field):
        groups = {}
        for row in evaluated:
            key = row.get(field) or "Unknown"
            groups.setdefault(key, []).append(row)
        stats = []
        for key, rows in groups.items():
            stats.append(
                {
                    field: key,
                    "count": len(rows),
                    "hit_rate": round((sum(1 for row in rows if row["is_win"]) / len(rows)) * 100, 2),
                    "average_return_pct": round(_avg([row.get("realized_return_pct") for row in rows]), 2),
                }
            )
        stats.sort(key=lambda row: (row["average_return_pct"], row["hit_rate"]), reverse=True)
        return stats

    horizon_stats = grouped_stats("horizon")
    lane_stats = grouped_stats("lane")
    sector_stats = grouped_stats("sector")
    action_stats = grouped_stats("action")
    data_confidence_stats = grouped_stats("data_confidence")
    news_stats = grouped_stats("news_sentiment")
    fundamental_stats = grouped_stats("fundamental_quality")

    if hit_rate < 45 or avg_return < 0:
        confidence_adjustment = -10.0
    elif hit_rate >= 60 and avg_return > 0:
        confidence_adjustment = 6.0
    else:
        confidence_adjustment = 0.0

    worst_mistake = "Not enough repeated mistakes"
    if false_positive_count >= false_negative_count and false_positive_count > 0:
        worst_mistake = "Buy/Add recommendations have produced too many negative outcomes."
    elif false_negative_count > 0:
        worst_mistake = "Avoid/Sell calls may be missing later upside."

    return {
        "total_recommendations": len(recommendation_log),
        "evaluated_count": len(evaluated),
        "hit_rate": round(hit_rate, 2),
        "average_return_pct": round(avg_return, 2),
        "average_alpha_pct": round(avg_alpha, 2),
        "average_drawdown_pct": round(avg_drawdown, 2),
        "false_positive_count": false_positive_count,
        "false_negative_count": false_negative_count,
        "best_holding_window": horizon_stats[0]["horizon"] if horizon_stats else "Unknown",
        "best_timeframe": horizon_stats[0]["horizon"] if horizon_stats else "Unknown",
        "best_sector": sector_stats[0]["sector"] if sector_stats else "Unknown",
        "best_signal_type": action_stats[0]["action"] if action_stats else "Unknown",
        "worst_recurring_mistake": worst_mistake,
        "confidence_adjustment": confidence_adjustment,
        "horizon_stats": horizon_stats,
        "lane_stats": lane_stats,
        "sector_stats": sector_stats,
        "action_stats": action_stats,
        "data_confidence_stats": data_confidence_stats,
        "factor_stats": {
            "news_sentiment": news_stats,
            "fundamental_quality": fundamental_stats,
        },
        "summary": (
            f"Evaluated {len(evaluated)} recommendation outcome(s): hit rate {hit_rate:.1f}%, "
            f"average return {avg_return:+.2f}%, confidence adjustment {confidence_adjustment:+.1f}."
        ),
    }


def build_learning_dashboard_context(accuracy):
    """Translate recommendation accuracy into dashboard guidance."""
    accuracy = accuracy or {}
    experiments = []
    if accuracy.get("evaluated_count", 0) < 10:
        experiments.append("Log and evaluate at least 10 recommendations before trusting calibration.")
    if accuracy.get("false_positive_count", 0) > 0:
        experiments.append("Tighten Buy Candidate rules after false positives.")
    if accuracy.get("average_drawdown_pct", 0) > 8:
        experiments.append("Test smaller position sizes or stricter stop-loss assumptions.")
    if accuracy.get("average_alpha_pct", 0) < 0:
        experiments.append("Compare candidates against SPY/sector ETF before approving action.")
    if not experiments:
        experiments.append("Run a controlled experiment on the best-performing timeframe.")

    return {
        "working": [
            f"Best timeframe: {accuracy.get('best_timeframe', 'Unknown')}.",
            f"Best sector: {accuracy.get('best_sector', 'Unknown')}.",
            f"Best signal/action type: {accuracy.get('best_signal_type', 'Unknown')}.",
        ],
        "not_working": [
            accuracy.get("worst_recurring_mistake", "No recurring mistake identified."),
        ],
        "next_experiments": experiments,
        "summary": accuracy.get("summary", "No accuracy summary available."),
    }


def build_research_process_audit(accuracy):
    """Create descriptive audit warnings from evaluated research outcomes."""
    accuracy = accuracy or {}
    warnings = []
    repeated_mistakes = []
    missed_risks = []
    benchmark_notes = []

    if accuracy.get("evaluated_count", 0) < 10:
        warnings.append("Sample size is still small; avoid overconfidence.")
    if accuracy.get("confidence_adjustment", 0.0) > 0 and accuracy.get("evaluated_count", 0) < 20:
        warnings.append("Positive calibration exists, but it is not enough to loosen risk controls.")
    if accuracy.get("false_positive_count", 0) > 0:
        repeated_mistakes.append("Buy/Add ideas have produced false positives; tighten entry and data gates.")
    if accuracy.get("average_drawdown_pct", 0.0) > 8:
        missed_risks.append("Post-signal drawdowns are high; review volatility, pullback, and sizing assumptions.")
    if accuracy.get("average_alpha_pct", 0.0) < 0:
        benchmark_notes.append("Recent evaluated ideas are lagging benchmark alpha on average.")
    else:
        benchmark_notes.append("Evaluated ideas are not showing negative benchmark alpha on average.")

    weak_lanes = [
        row for row in accuracy.get("lane_stats", [])
        if row.get("count", 0) >= 2 and row.get("average_return_pct", 0.0) < 0
    ]
    for row in weak_lanes:
        repeated_mistakes.append(f"{row.get('lane')} lane has negative average evaluated return.")

    if not warnings:
        warnings.append("No major overconfidence warning from current evaluated sample.")
    if not repeated_mistakes:
        repeated_mistakes.append("No repeated mistake pattern is clear yet.")
    if not missed_risks:
        missed_risks.append("No major missed-risk pattern is clear yet.")

    return {
        "overconfidence_warnings": warnings,
        "repeated_mistake_patterns": repeated_mistakes,
        "missed_risk_flags": missed_risks,
        "benchmark_notes": benchmark_notes,
        "summary": "Research process audit is descriptive and requires human review before scoring changes.",
    }
