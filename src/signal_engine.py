def generate_signal(symbol, snapshot, risk, news_context=None):
    """Generate a simple rule-based research signal with optional news scoring.

    Returns a dict with `quant_score`, `news_score`, and final `score`.
    """
    # Quant portion (original logic) — compute as quant_score
    quant_score = 50
    reasons = []
    risks = []

    return_pct = risk.get("return_pct", 0.0)
    volatility_pct = risk.get("volatility_pct", 0.0)
    max_drawdown_pct = risk.get("max_drawdown_pct", 0.0)
    change_pct = snapshot.get("change_pct", 0.0)

    if return_pct > 0:
        quant_score += min(return_pct, 20)
        reasons.append(f"Positive trend return of {return_pct:+.2f}%.")
    else:
        quant_score += max(return_pct, -20)
        risks.append(f"Negative trend return of {return_pct:+.2f}%.")

    if change_pct > 0:
        quant_score += min(change_pct * 2, 6)
        reasons.append(f"Recent daily change is positive at {change_pct:+.2f}%.")
    elif change_pct < 0:
        quant_score += max(change_pct * 2, -6)
        risks.append(f"Recent daily change is negative at {change_pct:+.2f}%.")
    else:
        reasons.append("Daily change is flat, keep monitoring price action.")

    if volatility_pct < 20:
        quant_score += 10
        reasons.append("Volatility is under 20%, which is positive for research signals.")
    elif volatility_pct > 30:
        quant_score -= 10
        risks.append("Volatility is over 30%, which increases uncertainty.")
    else:
        reasons.append("Volatility is in a moderate range.")

    if max_drawdown_pct > -10:
        quant_score += 8
        reasons.append("Max drawdown is shallow, which supports the signal.")
    elif max_drawdown_pct < -20:
        quant_score -= 10
        risks.append(f"Max drawdown of {max_drawdown_pct:.2f}% is deep.")
    else:
        reasons.append("Max drawdown is moderate, monitor downside risk.")

    # News scoring
    news_score = 0
    if news_context:
        sentiment = news_context.get("market_sentiment", "Neutral")
        if sentiment == "Bullish":
            news_score += 5
        elif sentiment == "Bearish":
            news_score -= 5

        # positive event tags
        positive_tags = {"earnings", "ai", "product", "guidance"}
        tags = set([t.lower() for t in news_context.get("event_tags", [])])
        for tag in tags:
            if tag in positive_tags:
                news_score += 2

        # risk flags penalize
        risk_flags = news_context.get("risk_flags", [])
        news_score -= 3 * len(risk_flags)

    # Combined score: quant_score + news_score, then mapped to 0-100
    raw_score = quant_score + news_score
    final_score = max(0, min(100, int(round(raw_score))))

    # Signal labels based on final_score
    if final_score >= 80:
        signal = "Strong Watch"
    elif final_score >= 60:
        signal = "Watch"
    elif final_score >= 40:
        signal = "Caution"
    else:
        signal = "Avoid"

    # Ensure at least one reason/risk message
    if not reasons:
        reasons.append("No strong positive signals detected yet.")
    if not risks:
        risks.append("No major risks flagged with current inputs.")

    return {
        "symbol": symbol,
        "signal": signal,
        "score": final_score,
        "quant_score": int(round(quant_score)),
        "news_score": int(round(news_score)),
        "reasons": reasons,
        "risks": risks,
    }
