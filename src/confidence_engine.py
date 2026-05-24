def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def calculate_confidence_adjustment(
    signal_data,
    evaluation_summary,
    regime_data,
    adaptive_learning,
    research_mode="Balanced",
    analysis_depth="Standard",
):
    """Calibrate trust in the current research signal without implying certainty."""
    signal_score = _safe_float(signal_data.get("score", 50))
    base_confidence = max(1, min(10, round(signal_score / 10, 1)))
    adjusted_confidence = base_confidence
    confidence_reasoning = [
        f"Base confidence starts from the current signal score: {base_confidence}/10."
    ]

    total_predictions = int(_safe_float(evaluation_summary.get("total_predictions", 0)))
    hit_rate = _safe_float(evaluation_summary.get("hit_rate", 0))

    if total_predictions >= 5 and hit_rate >= 65:
        adjusted_confidence += 1.0
        confidence_reasoning.append(
            "Historical hit rate is strong enough to slightly increase trust."
        )
    elif total_predictions >= 3 and hit_rate < 45:
        adjusted_confidence -= 1.0
        confidence_reasoning.append(
            "Historical hit rate has been weak, so trust is reduced."
        )
    else:
        confidence_reasoning.append(
            "Historical sample size or hit rate is not strong enough for a major adjustment."
        )

    regime = regime_data.get("regime", "Unknown")
    if regime in {"High Volatility", "Bear Trend"}:
        adjusted_confidence -= 1.0
        confidence_reasoning.append(
            f"{regime} conditions reduce trust in current signals."
        )
    elif regime == "Bull Trend":
        adjusted_confidence += 0.5
        confidence_reasoning.append(
            "Bull Trend conditions modestly support the current signal."
        )
    else:
        confidence_reasoning.append(
            f"{regime} conditions do not add strong confidence."
        )

    strategy_consistency = adaptive_learning.get("strategy_consistency", "Unknown")
    if strategy_consistency == "Weak":
        adjusted_confidence -= 0.75
        confidence_reasoning.append(
            "Strategy consistency is weak, so trust is reduced."
        )
    elif strategy_consistency == "Improving":
        adjusted_confidence += 0.25
        confidence_reasoning.append(
            "Strategy consistency is improving, so trust gets a small cautious boost."
        )
    else:
        confidence_reasoning.append(
            "Strategy consistency is not clear enough to raise trust."
        )

    weak_factors = adaptive_learning.get("weak_negative_factors", [])
    if len(weak_factors) >= 2:
        adjusted_confidence -= 0.5
        confidence_reasoning.append(
            "Adaptive learning found multiple weak factors, so trust is trimmed."
        )

    learning_confidence = _safe_float(adaptive_learning.get("learning_confidence", 0))
    if learning_confidence >= 7:
        adjusted_confidence += 0.5
        confidence_reasoning.append(
            "Adaptive learning confidence is improving, so trust gets a small boost."
        )
    else:
        confidence_reasoning.append(
            "Adaptive learning confidence is still developing, so no certainty is assumed."
        )

    if research_mode == "Conservative":
        adjusted_confidence -= 0.5
        confidence_reasoning.append(
            "Conservative mode lowers trust to keep the research stance cautious."
        )
    elif research_mode == "Aggressive":
        adjusted_confidence += 0.5
        confidence_reasoning.append(
            "Aggressive mode allows slightly higher trust, still within research-only limits."
        )
    else:
        confidence_reasoning.append("Balanced mode keeps default trust calibration.")

    adjusted_confidence = round(max(1, min(10, adjusted_confidence)), 1)

    if adjusted_confidence >= 7:
        trust_level = "High"
    elif adjusted_confidence >= 4:
        trust_level = "Moderate"
    else:
        trust_level = "Low"

    confidence_reasoning.append(
        "Confidence is a research calibration only, not a guarantee of future results."
    )
    if analysis_depth == "Deep":
        confidence_reasoning.append(
            f"Depth context: {analysis_depth}. Review hit-rate quality, regime stability, and adaptive notes together."
        )
    elif analysis_depth == "Quick":
        confidence_reasoning = confidence_reasoning[:4]

    return {
        "base_confidence": base_confidence,
        "adjusted_confidence": adjusted_confidence,
        "confidence_reasoning": confidence_reasoning,
        "trust_level": trust_level,
    }
