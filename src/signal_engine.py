def generate_signal(symbol, snapshot, risk):
    """Generate a simple rule-based research signal."""
    score = 50
    reasons = []
    risks = []

    return_pct = risk.get("return_pct", 0.0)
    volatility_pct = risk.get("volatility_pct", 0.0)
    max_drawdown_pct = risk.get("max_drawdown_pct", 0.0)
    change_pct = snapshot.get("change_pct", 0.0)

    if return_pct > 0:
        score += min(return_pct, 20)
        reasons.append(f"Positive trend return of {return_pct:+.2f}%.")
    else:
        score += max(return_pct, -20)
        risks.append(f"Negative trend return of {return_pct:+.2f}%.")

    if change_pct > 0:
        score += min(change_pct * 2, 6)
        reasons.append(f"Recent daily change is positive at {change_pct:+.2f}%.")
    elif change_pct < 0:
        score += max(change_pct * 2, -6)
        risks.append(f"Recent daily change is negative at {change_pct:+.2f}%.")
    else:
        reasons.append("Daily change is flat, keep monitoring price action.")

    if volatility_pct < 20:
        score += 10
        reasons.append("Volatility is under 20%, which is positive for research signals.")
    elif volatility_pct > 30:
        score -= 10
        risks.append("Volatility is over 30%, which increases uncertainty.")
    else:
        reasons.append("Volatility is in a moderate range.")

    if max_drawdown_pct > -10:
        score += 8
        reasons.append("Max drawdown is shallow, which supports the signal.")
    elif max_drawdown_pct < -20:
        score -= 10
        risks.append(f"Max drawdown of {max_drawdown_pct:.2f}% is deep.")
    else:
        reasons.append("Max drawdown is moderate, monitor downside risk.")

    if score >= 80:
        signal = "Strong Watch"
    elif score >= 60:
        signal = "Watch"
    elif score >= 40:
        signal = "Caution"
    else:
        signal = "Avoid"

    score = max(0, min(100, int(round(score))))

    if not reasons:
        reasons.append("No strong positive signals detected yet.")
    if not risks:
        risks.append("No major risks flagged with current inputs.")

    return {
        "symbol": symbol,
        "signal": signal,
        "score": score,
        "reasons": reasons,
        "risks": risks,
    }
