"""Rule-based growth discovery layer for research-only opportunity ranking."""


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value, low=0, high=100):
    return max(low, min(high, value))


def score_growth_discovery(symbol, market_data, fundamentals=None, catalysts=None, alt_data=None, source_quality=None):
    """Score an up-and-coming candidate using transparent, low-precision inputs."""
    symbol = str(symbol or "").upper()
    market_data = market_data or {}
    fundamentals = fundamentals or {}
    catalysts = catalysts or {}
    alt_data = alt_data or {}
    source_quality = source_quality or {}

    score = 45.0
    positives = []
    risks = []
    factors = []

    return_pct = _safe_float(market_data.get("return_pct"))
    volatility = _safe_float(market_data.get("volatility_pct"))
    drawdown = _safe_float(market_data.get("max_drawdown_pct"))
    signal_score = _safe_float(market_data.get("score"), 50.0)
    gate = source_quality.get("recommendation_gate", market_data.get("recommendation_gate", "Warning"))
    confidence = source_quality.get("data_confidence", market_data.get("data_confidence", "Unknown"))
    listing_type = market_data.get("listing_type", "")
    theme = market_data.get("theme", "")

    if return_pct >= 8:
        score += 16
        positives.append("Strong recent relative momentum.")
        factors.append("Momentum contributed positively.")
    elif return_pct >= 3:
        score += 9
        positives.append("Positive recent trend.")
    elif return_pct <= -8:
        score -= 12
        risks.append("Recent trend is weak or under pressure.")

    if signal_score >= 70:
        score += 12
        positives.append("Signal engine score is supportive.")
    elif signal_score < 45:
        score -= 8
        risks.append("Signal quality is weak.")

    if volatility >= 45:
        score -= 16
        risks.append("Very high volatility makes the setup speculative.")
    elif volatility >= 30:
        score -= 8
        risks.append("Elevated volatility requires smaller sizing and patience.")
    elif 8 <= volatility <= 24:
        score += 5
        positives.append("Volatility is inside a more usable research range.")

    if drawdown <= -25:
        score -= 12
        risks.append("Deep drawdown suggests thesis or timing risk.")
    elif drawdown <= -12 and return_pct > 0:
        score += 4
        positives.append("Potential recovery setup after a drawdown.")

    fundamental_score = _safe_float(fundamentals.get("fundamental_score"), 50.0)
    if fundamental_score >= 70:
        score += 8
        positives.append("Fundamental quality placeholder is supportive.")
    elif fundamental_score < 40:
        score -= 8
        risks.append("Fundamental quality placeholder is weak.")

    catalyst_rows = catalysts.get("catalysts", []) if isinstance(catalysts, dict) else []
    high_urgency = any(str(row.get("urgency", "")).lower() == "high" for row in catalyst_rows if isinstance(row, dict))
    if high_urgency:
        score += 5
        positives.append("Catalyst tracker shows a high-urgency item.")

    alt_score = _safe_float(alt_data.get("alternative_data_score"), 50.0)
    if alt_score >= 65:
        score += 4
        positives.append("Alternative data is modestly supportive.")
    if alt_data.get("risk_flags"):
        score -= min(6, len(alt_data.get("risk_flags", [])) * 2)
        risks.append("Alternative-data risk flags are present.")

    if listing_type == "IPO/recent listing":
        score -= 6
        risks.append("Recent listings need extra proof because price history is limited.")
    if theme:
        positives.append(f"Theme exposure: {theme}.")

    if gate == "Blocked" or confidence == "Low":
        score = min(score, 48)
        risks.append("Data quality blocks high-confidence action labels.")
    elif gate == "Warning":
        score = min(score, 76)
        risks.append("Data quality warning caps conviction.")

    score = round(_clamp(score), 0)
    if gate == "Blocked" or confidence == "Low":
        label = "Avoid" if score < 35 else "Emerging Watchlist"
    elif score >= 78 and volatility < 35:
        label = "Strategic Buy Candidate"
    elif score >= 64:
        label = "Wait for Pullback" if volatility >= 30 or drawdown <= -12 else "Emerging Watchlist"
    elif score >= 45:
        label = "Speculative Research"
    else:
        label = "Avoid"

    if not positives:
        positives.append("No strong positive growth-discovery factor is confirmed yet.")
    if not risks:
        risks.append("No major growth-discovery risk flag from available V1 inputs.")

    return {
        "symbol": symbol,
        "growth_score": score,
        "research_label": label,
        "theme": theme,
        "positive_factors": positives,
        "risk_flags": risks,
        "factor_notes": factors,
        "data_confidence": confidence,
        "recommendation_gate": gate,
        "summary": (
            f"{symbol} is labeled {label} with a {score:.0f}/100 growth-discovery score. "
            "This is research evidence only and does not guarantee growth."
        ),
    }

