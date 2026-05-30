def generate_signal(
    symbol,
    snapshot,
    risk,
    news_context=None,
    adaptive_context=None,
    asset_class=None,
    alternative_data_context=None,
):
    """Generate a simple rule-based research signal with optional supporting context."""

    def _apply_adaptive_adjustments(quant_score, news_score, volatility_pct, max_drawdown_pct):
        if not adaptive_context:
            return quant_score, news_score

        adjustments = adaptive_context.get("suggested_weight_adjustments", {})

        if "quant_score" in adjustments:
            quant_score = int(round(quant_score * float(adjustments["quant_score"])))
        if "news_score" in adjustments:
            news_score = int(round(news_score * float(adjustments["news_score"])))
        if volatility_pct > 30 and "volatility" in adjustments:
            quant_score -= max(1, int(round((1.0 - float(adjustments["volatility"])) * 5)))
        if max_drawdown_pct < -20 and "max_drawdown" in adjustments:
            quant_score -= max(1, int(round((1.0 - float(adjustments["max_drawdown"])) * 5)))

        quant_score = max(0, quant_score)
        news_score = max(-20, min(20, news_score))
        return quant_score, news_score

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

    news_score = 0
    if news_context:
        sentiment = news_context.get("market_sentiment", "Neutral")
        if sentiment == "Bullish":
            news_score += 5
        elif sentiment == "Bearish":
            news_score -= 5

        positive_tags = {"earnings", "ai", "product", "guidance"}
        tags = set([t.lower() for t in news_context.get("event_tags", [])])
        for tag in tags:
            if tag in positive_tags:
                news_score += 2

        risk_flags = news_context.get("risk_flags", [])
        news_score -= 3 * len(risk_flags)

    alternative_data_score = 0
    if alternative_data_context:
        alt_score = alternative_data_context.get("alternative_data_score", 50)
        risk_flags = alternative_data_context.get("risk_flags", [])
        if alt_score >= 65:
            alternative_data_score += 3
            reasons.append(
                "Alternative data context is modestly supportive, used only as supporting evidence."
            )
        elif alt_score <= 40:
            alternative_data_score -= 3
            risks.append(
                "Alternative data context is weak or noisy, so the signal receives a small penalty."
            )

        if risk_flags:
            penalty = min(len(risk_flags), 3)
            alternative_data_score -= penalty
            risks.append(
                "Alternative data has risk flags; delayed/noisy data keeps the weight small."
            )

    quant_score, news_score = _apply_adaptive_adjustments(
        quant_score,
        news_score,
        volatility_pct,
        max_drawdown_pct,
    )

    raw_score = quant_score + news_score + alternative_data_score
    final_score = max(0, min(100, int(round(raw_score))))

    if final_score >= 80:
        signal = "Strong Watch"
    elif final_score >= 60:
        signal = "Watch"
    elif final_score >= 40:
        signal = "Caution"
    else:
        signal = "Avoid"

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
        "alternative_data_score": int(round(alternative_data_score)),
        "reasons": reasons,
        "risks": risks,
    }
