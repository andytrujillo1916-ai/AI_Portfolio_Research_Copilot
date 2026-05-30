def _safe_float(value):
    try:
        if value in (None, ""):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _safe_str(value):
    return str(value) if value is not None else ""


def _bounded_adjustment(value, low=0.85, high=1.10):
    return round(max(low, min(high, float(value))), 2)


def calculate_factor_insights(predictions, research_runs):
    """Create simple, rule-based adaptive insights from saved predictions and research runs."""
    positive_outcomes = []
    negative_outcomes = []

    for prediction in predictions:
        realized_return = _safe_float(prediction.get("realized_return"))
        evaluation_label = _safe_str(prediction.get("evaluation_label"))
        is_positive = evaluation_label in {"Strong Hit", "Partial Hit"} or realized_return > 0
        is_negative = evaluation_label == "Miss" or realized_return < 0

        if is_positive:
            positive_outcomes.append(prediction)
        elif is_negative:
            negative_outcomes.append(prediction)

    strong_positive_factors = []
    weak_negative_factors = []
    suggested_weight_adjustments = {
        "quant_score": 1.0,
        "news_score": 1.0,
        "volatility": 1.0,
        "max_drawdown": 1.0,
    }

    def avg(key):
        values = [_safe_float(item.get(key)) for item in positive_outcomes if item.get(key) not in (None, "")]
        return sum(values) / len(values) if values else 0.0

    def avg_negative(key):
        values = [_safe_float(item.get(key)) for item in negative_outcomes if item.get(key) not in (None, "")]
        return sum(values) / len(values) if values else 0.0

    positive_news = avg("news_score")
    negative_news = avg_negative("news_score")
    positive_backtest = avg("backtest_return")
    negative_backtest = avg_negative("backtest_return")
    positive_vol = avg("volatility")
    negative_vol = avg_negative("volatility")
    positive_drawdown = abs(avg("max_drawdown"))
    negative_drawdown = abs(avg_negative("max_drawdown"))

    if positive_news >= 4 and positive_news > negative_news:
        strong_positive_factors.append("Bullish news context has often lined up with successful outcomes.")
        suggested_weight_adjustments["news_score"] = _bounded_adjustment(1.05)

    if positive_backtest >= 2 and positive_backtest > negative_backtest:
        strong_positive_factors.append("Positive backtest results have been useful in past research runs.")
        suggested_weight_adjustments["quant_score"] = _bounded_adjustment(1.03)

    if negative_vol >= 25 and negative_vol > positive_vol:
        weak_negative_factors.append("High volatility has often been associated with weak outcomes.")
        suggested_weight_adjustments["volatility"] = _bounded_adjustment(0.92)

    if negative_drawdown >= 15 and negative_drawdown > positive_drawdown:
        weak_negative_factors.append("Large drawdowns have often weakened the quality of bullish setups.")
        suggested_weight_adjustments["max_drawdown"] = _bounded_adjustment(0.93)

    for run in research_runs:
        regime = _safe_str(run.get("regime"))
        exposure = _safe_str(run.get("exposure_level"))
        decision = _safe_str(run.get("trade_decision"))

        if regime == "Bull Trend" and exposure in {"Low", "Medium"} and decision in {"Buy", "Watch"}:
            strong_positive_factors.append("Low-to-moderate exposure in bull regimes looks more practical than aggressive sizing.")
        if regime == "High Volatility" and decision == "Buy":
            weak_negative_factors.append("Buy decisions in high-volatility regimes have been weaker than expected.")
            suggested_weight_adjustments["volatility"] = _bounded_adjustment(
                min(suggested_weight_adjustments["volatility"], 0.90)
            )

    if not strong_positive_factors:
        strong_positive_factors.append("No strong positive pattern was clear from the current sample.")
    if not weak_negative_factors:
        weak_negative_factors.append("No major negative pattern was clear from the current sample.")

    total_samples = len(positive_outcomes) + len(negative_outcomes)
    learning_confidence = 4
    if total_samples >= 6:
        learning_confidence = 7
    elif total_samples >= 3:
        learning_confidence = 5

    if len(strong_positive_factors) >= 2 and len(weak_negative_factors) >= 2:
        learning_confidence = min(10, learning_confidence + 1)

    reviewable_adjustments = []
    for factor, adjustment in suggested_weight_adjustments.items():
        bounded = _bounded_adjustment(adjustment)
        suggested_weight_adjustments[factor] = bounded
        if bounded > 1.0:
            direction = "slightly increase"
        elif bounded < 1.0:
            direction = "slightly reduce"
        else:
            direction = "keep unchanged"
        reviewable_adjustments.append(
            {
                "factor": factor,
                "adjustment": bounded,
                "direction": direction,
                "reason": (
                    "Review this suggestion manually before changing scoring logic. "
                    "It is based on saved outcomes, not a self-modifying model."
                ),
            }
        )

    summary = (
        "This is a simple rule-based adaptation. It uses past prediction outcomes and saved research-run context "
        "to make small, bounded, reviewable suggestions only. It does not rewrite code or execute trades."
    )

    return {
        "strong_positive_factors": strong_positive_factors,
        "weak_negative_factors": weak_negative_factors,
        "suggested_weight_adjustments": suggested_weight_adjustments,
        "reviewable_adjustments": reviewable_adjustments,
        "learning_confidence": learning_confidence,
        "sample_size": total_samples,
        "disclaimer": (
            "Research-only recursive learning. Suggestions require human review and do not guarantee future performance."
        ),
        "summary": summary,
    }
