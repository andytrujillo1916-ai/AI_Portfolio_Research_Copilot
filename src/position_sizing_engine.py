def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mode_caps(research_mode):
    if research_mode == "Conservative":
        return {"max_pct": 5.0, "base_loss": 1.0}
    if research_mode == "Aggressive":
        return {"max_pct": 15.0, "base_loss": 3.0}
    return {"max_pct": 10.0, "base_loss": 2.0}


def calculate_position_size(
    execution_data,
    conviction_data,
    risk,
    portfolio_value=100000,
    research_mode="Balanced",
):
    """Recommend a research-only paper position size with transparent rules."""
    caps = _mode_caps(research_mode)
    execution_score = _safe_float(execution_data.get("execution_score", 0.0))
    readiness = str(execution_data.get("readiness_level", "Not Ready"))
    conviction_score = _safe_float(conviction_data.get("conviction_score", 0.0))
    confidence_level = str(conviction_data.get("confidence_level", "Low"))
    volatility = _safe_float(risk.get("volatility_pct", 0.0))
    drawdown = _safe_float(risk.get("max_drawdown_pct", 0.0))

    sizing_reasoning = []
    caution_flags = []

    if readiness == "Ready for Paper Trade":
        base_pct = 0.7 * caps["max_pct"]
        sizing_reasoning.append("Execution readiness is strong, so base size is increased.")
    elif readiness == "Near Ready":
        base_pct = 0.45 * caps["max_pct"]
        sizing_reasoning.append("Setup is near-ready, so size is moderate.")
    elif readiness == "Watch":
        base_pct = 0.2 * caps["max_pct"]
        sizing_reasoning.append("Watch-level setup keeps size small.")
    else:
        base_pct = 0.0
        sizing_reasoning.append("Not-ready setup suggests no new paper position.")

    if conviction_score >= 75:
        base_pct += 0.15 * caps["max_pct"]
        sizing_reasoning.append("High conviction score supports a small size increase.")
    elif conviction_score <= 45:
        base_pct -= 0.15 * caps["max_pct"]
        caution_flags.append("Low conviction score reduces position size.")

    if volatility >= 30:
        base_pct *= 0.55
        caution_flags.append("High volatility reduces size materially.")
    elif volatility >= 20:
        base_pct *= 0.75
        caution_flags.append("Elevated volatility trims size.")

    if drawdown <= -20:
        base_pct *= 0.7
        caution_flags.append("Deep drawdown context requires smaller size.")

    if confidence_level == "Low":
        base_pct *= 0.7
        caution_flags.append("Low confidence level reduces size.")
    elif confidence_level == "High":
        base_pct *= 1.05
        sizing_reasoning.append("High confidence allows a small sizing lift.")

    recommended_position_pct = max(0.0, min(caps["max_pct"], round(base_pct, 2)))
    recommended_position_value = round((recommended_position_pct / 100) * _safe_float(portfolio_value, 0.0), 2)

    max_loss_tolerance_pct = caps["base_loss"]
    if volatility >= 30 or drawdown <= -20:
        max_loss_tolerance_pct = max(0.5, caps["base_loss"] * 0.75)

    if recommended_position_pct >= 0.75 * caps["max_pct"]:
        risk_bucket = "High"
    elif recommended_position_pct >= 0.35 * caps["max_pct"]:
        risk_bucket = "Medium"
    else:
        risk_bucket = "Low"

    summary = (
        f"{research_mode} mode sizing recommends {recommended_position_pct:.2f}% "
        f"(${recommended_position_value:,.2f}) with risk bucket {risk_bucket}. "
        "This is paper-trading research guidance only."
    )

    return {
        "recommended_position_pct": recommended_position_pct,
        "recommended_position_value": recommended_position_value,
        "max_loss_tolerance_pct": round(max_loss_tolerance_pct, 2),
        "risk_bucket": risk_bucket,
        "sizing_reasoning": sizing_reasoning,
        "caution_flags": caution_flags,
        "summary": summary,
    }
