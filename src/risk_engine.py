def calculate_position_size(
    total_portfolio_value,
    current_price,
    confidence=5,
    volatility_pct=0.0,
    current_symbol_exposure=0.0,
    symbol=None,
    asset_class=None,
):
    """Calculate a research-only position size and risk summary."""
    total_portfolio_value = float(total_portfolio_value or 0)
    current_price = float(current_price or 0)
    volatility_pct = float(volatility_pct or 0)
    current_symbol_exposure = float(current_symbol_exposure or 0)

    if total_portfolio_value <= 0 or current_price <= 0:
        return {
            "recommended_position_value": 0.0,
            "recommended_shares": 0,
            "portfolio_risk_pct": 0.0,
            "risk_warning": "Need a valid portfolio value and current price to size a position.",
            "reasoning": [],
            "sizing_reasoning": [],
        }

    confidence = max(1, min(10, int(confidence)))
    base_risk_pct = 0.015
    if confidence >= 8:
        base_risk_pct = 0.05
    elif confidence >= 5:
        base_risk_pct = 0.035
    elif confidence >= 3:
        base_risk_pct = 0.025

    adjustment = 1.0
    sizing_reasoning = []

    if confidence >= 7:
        sizing_reasoning.append(
            "Confidence is strong, so the position is allowed a larger risk budget."
        )
    else:
        sizing_reasoning.append(
            "Confidence is moderate, so the risk budget stays conservative."
        )

    if volatility_pct >= 35:
        adjustment *= 0.5
        sizing_reasoning.append("Volatility is elevated, so the size is reduced.")
    elif volatility_pct >= 20:
        adjustment *= 0.75
        sizing_reasoning.append("Volatility is above normal, so the size is trimmed.")

    exposure_pct = (current_symbol_exposure / total_portfolio_value) * 100
    if exposure_pct >= 30:
        adjustment *= 0.5
        sizing_reasoning.append("Current exposure is already high, so the new position is capped.")
    elif exposure_pct >= 15:
        adjustment *= 0.75
        sizing_reasoning.append("Current exposure is elevated, so the new position is reduced.")

    recommended_position_value = total_portfolio_value * base_risk_pct * adjustment
    recommended_shares = int(recommended_position_value // current_price)
    if recommended_position_value > 0 and recommended_shares == 0:
        recommended_shares = 1

    portfolio_risk_pct = recommended_position_value / total_portfolio_value
    if portfolio_risk_pct > 0.05:
        risk_warning = "Position size exceeds the 5% guardrail and should be treated as research-only."
    elif volatility_pct >= 35:
        risk_warning = "High volatility detected; use a smaller position or wait for confirmation."
    elif exposure_pct >= 15:
        risk_warning = "Current exposure is elevated; keep the proposed position small."
    else:
        risk_warning = "Research-only sizing is within a conservative risk budget."

    return {
        "symbol": symbol,
        "recommended_position_value": round(recommended_position_value, 2),
        "recommended_shares": recommended_shares,
        "portfolio_risk_pct": round(portfolio_risk_pct, 4),
        "risk_warning": risk_warning,
        "reasoning": sizing_reasoning,
        "sizing_reasoning": sizing_reasoning,
    }
