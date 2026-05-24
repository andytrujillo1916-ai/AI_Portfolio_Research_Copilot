def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mode_thresholds(research_mode):
    if research_mode == "Conservative":
        return {"ready": 78, "near_ready": 60, "watch": 45}
    if research_mode == "Aggressive":
        return {"ready": 68, "near_ready": 52, "watch": 40}
    return {"ready": 72, "near_ready": 56, "watch": 42}


def evaluate_execution_readiness(
    signal_data,
    conviction_data,
    opportunity_data,
    alpha_data,
    regime_data,
    news_context,
    catalyst_data,
    risk,
    research_mode="Balanced",
    confidence_data=None,
):
    """Evaluate research-only paper-trade execution readiness."""
    thresholds = _mode_thresholds(research_mode)
    positive_checks = []
    failed_checks = []

    signal_score = _safe_float(signal_data.get("score", 0.0))
    conviction_score = _safe_float(conviction_data.get("conviction_score", 0.0))
    opportunity_score = _safe_float(
        (opportunity_data.get("best_opportunity") or {}).get("opportunity_score", 0.0)
    )
    alpha_pct = _safe_float(alpha_data.get("alpha_pct", 0.0))
    regime = str(regime_data.get("regime", "Unknown"))
    volatility = _safe_float(risk.get("volatility_pct", 0.0))
    drawdown = _safe_float(risk.get("max_drawdown_pct", 0.0))
    sentiment = str(news_context.get("market_sentiment", "Neutral"))
    conviction_risk = str(catalyst_data.get("conviction_risk", "Low"))
    trust_level = str((confidence_data or {}).get("trust_level", "Moderate"))

    execution_score = 50.0

    # Positive alignment checks
    if signal_score >= 70:
        execution_score += 10
        positive_checks.append("Signal score is strong.")
    elif signal_score >= 55:
        execution_score += 4
        positive_checks.append("Signal score is moderately supportive.")
    else:
        execution_score -= 8
        failed_checks.append("Signal score is weak.")

    if conviction_score >= 70:
        execution_score += 10
        positive_checks.append("Conviction score is high.")
    elif conviction_score < 45:
        execution_score -= 8
        failed_checks.append("Conviction score is low.")

    if opportunity_score >= 65:
        execution_score += 6
        positive_checks.append("Opportunity profile is strong.")
    elif opportunity_score < 45:
        execution_score -= 5
        failed_checks.append("Opportunity profile is weak.")

    if alpha_pct > 0:
        execution_score += 6
        positive_checks.append("Alpha vs benchmark is positive.")
    else:
        execution_score -= 6
        failed_checks.append("Alpha vs benchmark is weak or negative.")

    # Regime and risk checks
    if regime == "Bull Trend":
        execution_score += 6
        positive_checks.append("Bull Trend regime supports paper-trade timing.")
    elif regime in {"Bear Trend", "High Volatility"}:
        execution_score -= 10
        failed_checks.append(f"{regime} regime lowers entry readiness.")

    if volatility >= 30:
        execution_score -= 9
        failed_checks.append("Volatility is elevated.")
    elif volatility <= 18:
        execution_score += 3
        positive_checks.append("Volatility is controlled.")

    if drawdown <= -20:
        execution_score -= 7
        failed_checks.append("Drawdown is deep.")

    if sentiment == "Bullish":
        execution_score += 3
        positive_checks.append("News sentiment is supportive.")
    elif sentiment == "Bearish":
        execution_score -= 5
        failed_checks.append("News sentiment is bearish.")

    if conviction_risk == "High":
        execution_score -= 8
        failed_checks.append("Catalyst tracker indicates high conviction risk.")
    elif conviction_risk == "Low":
        execution_score += 2
        positive_checks.append("Catalyst risk is currently low.")

    if trust_level == "High":
        execution_score += 3
        positive_checks.append("Confidence calibration trust is high.")
    elif trust_level == "Low":
        execution_score -= 3
        failed_checks.append("Confidence calibration trust is low.")

    execution_score = max(0, min(100, round(execution_score, 1)))

    if execution_score >= thresholds["ready"]:
        readiness_level = "Ready for Paper Trade"
        entry_quality = "High quality setup for research-approved paper entry."
        recommended_action = "Paper Trade Only"
    elif execution_score >= thresholds["near_ready"]:
        readiness_level = "Near Ready"
        entry_quality = "Constructive setup, but one or two checks need confirmation."
        recommended_action = "Watch"
    elif execution_score >= thresholds["watch"]:
        readiness_level = "Watch"
        entry_quality = "Mixed setup with meaningful uncertainty."
        recommended_action = "Re-run Research"
    else:
        readiness_level = "Not Ready"
        entry_quality = "Weak alignment across core checks."
        recommended_action = "Avoid"

    risk_note = (
        f"Mode {research_mode}: thresholds are tuned for research-only paper-trade discipline."
    )
    summary = (
        f"Execution readiness score is {execution_score}/100 ({readiness_level}). "
        "This supports paper-trading research decisions only."
    )

    return {
        "execution_score": execution_score,
        "readiness_level": readiness_level,
        "positive_checks": positive_checks,
        "failed_checks": failed_checks,
        "entry_quality": entry_quality,
        "risk_note": risk_note,
        "recommended_action": recommended_action,
        "summary": summary,
    }
