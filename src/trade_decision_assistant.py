def generate_trade_decision(symbol, snapshot, risk, signal_data, news_context, backtest_results, paper_positions):
    """Create a research-only paper-trading suggestion from current signals and context."""
    score = int(signal_data.get("score", 0))
    volatility_pct = risk.get("volatility_pct", 0.0)
    max_drawdown_pct = risk.get("max_drawdown_pct", 0.0)
    strategy_return = backtest_results.get("strategy_return_pct", 0.0)
    buy_hold_return = backtest_results.get("buy_and_hold_return_pct", 0.0)
    sentiment = news_context.get("market_sentiment", "Neutral") if news_context else "Neutral"
    held_shares = paper_positions.get("total_shares", 0) if paper_positions else 0

    reasons = []
    risks = []
    confidence = 5

    if score >= 75:
        confidence += 2
        reasons.append("Signal score is strong.")
    elif score >= 55:
        confidence += 1
        reasons.append("Signal score is above neutral.")
    else:
        confidence -= 1
        risks.append("Signal score is weak.")

    if sentiment == "Bullish":
        confidence += 1
        reasons.append("News sentiment is bullish.")
    elif sentiment == "Bearish":
        confidence -= 1
        risks.append("News sentiment is bearish.")

    if strategy_return >= buy_hold_return:
        confidence += 1
        reasons.append("Backtest result is at least as strong as buy-and-hold.")
    else:
        confidence -= 1
        risks.append("Backtest result is weaker than buy-and-hold.")

    if volatility_pct > 30:
        confidence -= 1
        risks.append("Volatility is elevated, so the signal is less stable.")

    if max_drawdown_pct < -20:
        confidence -= 1
        risks.append("Drawdown is deep, so downside risk is elevated.")

    if held_shares >= 1:
        confidence -= 1
        reasons.append("A paper position is already open, so the safest action is to hold.")

    if confidence > 10:
        confidence = 10
    if confidence < 1:
        confidence = 1

    strong_buy_setup = (
        score >= 75
        and sentiment == "Bullish"
        and volatility_pct <= 25
        and max_drawdown_pct >= -15
        and strategy_return >= buy_hold_return
    )
    weak_sell_setup = (
        score <= 40
        and (
            sentiment == "Bearish"
            or strategy_return < buy_hold_return
            or volatility_pct > 30
            or max_drawdown_pct < -20
        )
    )
    neutral_watch_setup = score >= 55 and sentiment != "Bearish"

    if held_shares >= 1:
        suggested_action = "Hold"
    elif strong_buy_setup:
        suggested_action = "Buy"
    elif weak_sell_setup:
        suggested_action = "Sell"
    elif neutral_watch_setup:
        suggested_action = "Watch"
    elif sentiment == "Bearish":
        suggested_action = "Watch"
    else:
        suggested_action = "Sell"

    if suggested_action == "Buy":
        reasons.append("The signal, news, and backtest context are aligned for a paper entry.")
    elif suggested_action == "Sell":
        reasons.append("The current setup is weak enough to justify reducing paper exposure.")
    elif suggested_action == "Hold":
        reasons.append("Existing paper exposure is already in place, so holding avoids unnecessary churn.")
    else:
        reasons.append("Current conditions are mixed, so the safest next step is to watch the setup.")

    if not reasons:
        reasons.append("No strong signal edge was found.")
    if not risks:
        risks.append("No major risks were flagged in the current context.")

    return {
        "suggested_action": suggested_action,
        "confidence": confidence,
        "reasons": reasons,
        "risks": risks,
        "approval_required": True,
    }
