def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mode_weights(research_mode):
    if research_mode == "Conservative":
        return {"upside": 0.9, "risk_penalty": 1.2}
    if research_mode == "Aggressive":
        return {"upside": 1.1, "risk_penalty": 0.9}
    return {"upside": 1.0, "risk_penalty": 1.0}


def _conviction_level(score):
    if score >= 80:
        return "Very High"
    if score >= 65:
        return "High"
    if score >= 45:
        return "Medium"
    return "Low"


def _research_priority(level):
    if level in {"Very High", "High"}:
        return "High"
    if level == "Medium":
        return "Medium"
    return "Low"


def calculate_conviction_score(
    signal_data,
    opportunity_data,
    thesis_health,
    regime_data,
    news_context,
    factor_attribution,
    confidence_data,
    research_mode="Balanced",
):
    """Calculate a unified research-only conviction score with transparent rules."""
    weights = _mode_weights(research_mode)
    positive_drivers = []
    negative_drivers = []

    score = 50.0

    signal_score = _safe_float(signal_data.get("score", 0.0))
    score += ((signal_score - 50) * 0.35) * weights["upside"]
    if signal_score >= 70:
        positive_drivers.append("Strong signal score supports conviction.")
    elif signal_score <= 40:
        negative_drivers.append("Weak signal score lowers conviction.")

    best_opp = opportunity_data.get("best_opportunity", {}) if isinstance(opportunity_data, dict) else {}
    opp_score = _safe_float(best_opp.get("opportunity_score", 0.0))
    score += ((opp_score - 50) * 0.12) * weights["upside"]
    if opp_score >= 65:
        positive_drivers.append("Opportunity ranking is supportive.")
    elif opp_score <= 40:
        negative_drivers.append("Opportunity profile is weak.")

    thesis_status = str(thesis_health.get("thesis_status", "Stable"))
    thesis_delta = {
        "Strengthening": 8,
        "Stable": 2,
        "Weakening": -8,
        "Broken": -14,
    }.get(thesis_status, 0)
    score += thesis_delta * weights["upside"]
    if thesis_status in {"Strengthening", "Stable"}:
        positive_drivers.append(f"Thesis health is {thesis_status.lower()}.")
    else:
        negative_drivers.append(f"Thesis health is {thesis_status.lower()}.")

    regime = str(regime_data.get("regime", "Unknown"))
    if regime == "Bull Trend":
        score += 6 * weights["upside"]
        positive_drivers.append("Bull Trend regime improves conviction.")
    elif regime in {"Bear Trend", "High Volatility"}:
        score -= 8 * weights["risk_penalty"]
        negative_drivers.append(f"{regime} regime adds caution.")

    sentiment = str(news_context.get("market_sentiment", "Neutral"))
    if sentiment == "Bullish":
        score += 4 * weights["upside"]
        positive_drivers.append("Bullish news sentiment is supportive.")
    elif sentiment == "Bearish":
        score -= 5 * weights["risk_penalty"]
        negative_drivers.append("Bearish news sentiment reduces conviction.")

    trust_level = str(confidence_data.get("trust_level", "Moderate"))
    confidence_adjusted = _safe_float(confidence_data.get("adjusted_confidence", 5.0))
    score += (confidence_adjusted - 5) * 1.8 * weights["upside"]
    if trust_level in {"High", "Very High"}:
        positive_drivers.append("Confidence calibration is supportive.")
    elif trust_level == "Low":
        negative_drivers.append("Confidence calibration is weak.")

    risk_factor = str((factor_attribution.get("risk_driver") or {}).get("factor", ""))
    if risk_factor in {"Volatility pressure", "Concentration risk", "Regime risk", "Drawdown depth"}:
        score -= 4 * weights["risk_penalty"]
        negative_drivers.append(f"Risk driver flagged: {risk_factor}.")

    dominant_factor = str((factor_attribution.get("dominant_factor") or {}).get("factor", ""))
    if dominant_factor in {"Signal score quality", "Sector strength alignment"}:
        score += 3 * weights["upside"]
        positive_drivers.append(f"Dominant factor supports conviction: {dominant_factor}.")

    score = max(0, min(100, round(score, 1)))
    level = _conviction_level(score)
    priority = _research_priority(level)

    summary = (
        f"{research_mode} mode conviction is {score}/100 ({level}). "
        "This is a research context score, not a prediction or execution signal."
    )

    return {
        "conviction_score": score,
        "conviction_level": level,
        "positive_drivers": positive_drivers,
        "negative_drivers": negative_drivers,
        "research_priority": priority,
        "summary": summary,
    }
