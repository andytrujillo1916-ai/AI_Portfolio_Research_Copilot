def _safe_float(value):
    """Convert values to float when possible."""
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _infer_correct_direction(prediction):
    """Infer correct_direction from realized return and signal label."""
    realized_return = _safe_float(
        prediction.get("realized_return_pct", prediction.get("realized_return"))
    )
    signal = str(prediction.get("signal", "") or prediction.get("suggested_action", "")).lower()

    if realized_return is None:
        return False

    if any(label in signal for label in ["buy", "strong watch", "watch"]):
        return realized_return > 0
    if any(label in signal for label in ["sell", "avoid", "caution"]):
        return realized_return <= 0
    return realized_return > 0


def _build_factor_rows(predictions):
    """Create factor rows for simple rule-based feature comparisons."""
    factor_rows = []
    for prediction in predictions:
        realized_return = _safe_float(
            prediction.get("realized_return_pct", prediction.get("realized_return"))
        )
        if realized_return is None:
            continue

        score = _safe_float(prediction.get("score"))
        quant_score = _safe_float(prediction.get("quant_score"))
        news_score = _safe_float(prediction.get("news_score"))
        volatility = _safe_float(prediction.get("volatility"))
        max_drawdown = _safe_float(prediction.get("max_drawdown"))
        backtest_return = _safe_float(prediction.get("backtest_return"))

        factor_rows.append(
            {
                "score": score,
                "quant_score": quant_score,
                "news_score": news_score,
                "volatility": volatility,
                "max_drawdown": abs(max_drawdown) if max_drawdown is not None else None,
                "backtest_return": backtest_return,
                "realized_return": realized_return,
            }
        )

    return factor_rows


def analyze_signal_effectiveness(predictions):
    """Provide simple rule-based insights about which factors correlate with good outcomes."""
    valid_predictions = [prediction for prediction in predictions if isinstance(prediction, dict)]
    if not valid_predictions:
        return {
            "top_positive_factors": [],
            "top_negative_factors": [],
            "hit_rate_by_signal_type": {},
            "avg_return_by_signal_type": {},
            "learning_summary": (
                "No evaluated predictions are available yet. Save more predictions and review them "
                "to build a research-only learning summary."
            ),
        }

    signal_groups = {}
    factor_rows = _build_factor_rows(valid_predictions)

    for prediction in valid_predictions:
        signal_type = str(
            prediction.get("suggested_action")
            or prediction.get("signal")
            or "Unknown"
        )
        realized_return = _safe_float(
            prediction.get("realized_return_pct", prediction.get("realized_return"))
        )
        correct_direction = prediction.get("correct_direction")
        if correct_direction is None:
            correct_direction = _infer_correct_direction(prediction)

        if signal_type not in signal_groups:
            signal_groups[signal_type] = {"hits": 0, "total": 0, "returns": []}

        signal_groups[signal_type]["total"] += 1
        if correct_direction:
            signal_groups[signal_type]["hits"] += 1
        if realized_return is not None:
            signal_groups[signal_type]["returns"].append(realized_return)

    factor_scores = []
    for factor_name in ["score", "quant_score", "news_score", "volatility", "max_drawdown", "backtest_return"]:
        values = [row.get(factor_name) for row in factor_rows if row.get(factor_name) is not None]
        returns = [row["realized_return"] for row in factor_rows if row.get(factor_name) is not None]

        if len(values) < 2 or len(returns) < 2:
            continue

        median = sorted(values)[len(values) // 2]
        high_group = [r for value, r in zip(values, returns) if value is not None and value >= median]
        low_group = [r for value, r in zip(values, returns) if value is not None and value < median]

        if not high_group or not low_group:
            continue

        delta = (sum(high_group) / len(high_group)) - (sum(low_group) / len(low_group))
        factor_scores.append((factor_name, delta))

    factor_scores.sort(key=lambda item: item[1], reverse=True)
    top_positive = [name for name, delta in factor_scores if delta >= 0.5][:3]
    top_negative = [name for name, delta in sorted(factor_scores, key=lambda item: item[1]) if delta <= -0.5][:3]

    hit_rate_by_signal_type = {}
    avg_return_by_signal_type = {}
    for signal_type, stats in signal_groups.items():
        total = stats["total"]
        if total:
            hit_rate_by_signal_type[signal_type] = round((stats["hits"] / total) * 100, 2)
            if stats["returns"]:
                avg_return_by_signal_type[signal_type] = round(
                    sum(stats["returns"]) / len(stats["returns"]), 2
                )

    best_signal = max(
        signal_groups.items(),
        key=lambda item: (
            (sum(item[1]["returns"]) / len(item[1]["returns"]))
            if item[1]["returns"]
            else -999
        ),
    )

    positive_text = ", ".join(top_positive) if top_positive else "no strong positive patterns"
    negative_text = ", ".join(top_negative) if top_negative else "no strong negative patterns"
    best_signal_text = best_signal[0] if best_signal else "No signal type"
    best_return = (
        round(sum(best_signal[1]["returns"]) / len(best_signal[1]["returns"]), 2)
        if best_signal and best_signal[1]["returns"]
        else 0.0
    )

    learning_summary = (
        f"Research-only learning summary: {positive_text} were the strongest positive associations, "
        f"while {negative_text} were the strongest negative associations. {best_signal_text} had the "
        f"best average realized return in this sample at {best_return:+.2f}%. This is descriptive "
        f"insight, not a prediction model or auto-execution logic."
    )

    return {
        "top_positive_factors": top_positive,
        "top_negative_factors": top_negative,
        "hit_rate_by_signal_type": hit_rate_by_signal_type,
        "avg_return_by_signal_type": avg_return_by_signal_type,
        "learning_summary": learning_summary,
    }
