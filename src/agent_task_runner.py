def _safe_number(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _add_if_present(items, text):
    if text:
        items.append(text)


def run_research_workflow(
    symbol,
    snapshot,
    price_data,
    risk,
    news_context,
    signal_data,
    regime_data,
    exposure_data,
    backtest_results,
    strategy_lab_results,
    trade_decision,
    research_memo,
    research_mode="Balanced",
    analysis_depth="Standard",
):
    """Run a simple research-only agent workflow report."""
    steps_completed = [
        "Market data reviewed",
        "Risk metrics reviewed",
        "News context reviewed",
        "Signal score reviewed",
        "Market regime reviewed",
        "Exposure reviewed",
        "Backtest reviewed",
        "Strategy lab reviewed",
        "Trade decision reviewed",
        "Research memo reviewed",
    ]

    key_findings = []
    concerns = []
    recommended_next_actions = []

    price = snapshot.get("price") if isinstance(snapshot, dict) else None
    change_pct = _safe_number(snapshot.get("change_pct")) if isinstance(snapshot, dict) else 0
    return_pct = _safe_number(risk.get("return_pct")) if isinstance(risk, dict) else 0
    volatility_pct = _safe_number(risk.get("volatility_pct")) if isinstance(risk, dict) else 0
    max_drawdown_pct = _safe_number(risk.get("max_drawdown_pct")) if isinstance(risk, dict) else 0

    _add_if_present(key_findings, f"{symbol} current price reviewed: {price}.")
    _add_if_present(key_findings, f"Recent daily change: {change_pct:+.2f}%.")
    _add_if_present(key_findings, f"Trend return: {return_pct:+.2f}%.")

    if isinstance(news_context, dict):
        sentiment = news_context.get("market_sentiment", "Neutral")
        key_findings.append(f"News sentiment reviewed: {sentiment}.")
        for flag in news_context.get("risk_flags", []):
            concerns.append(f"News risk flag: {flag}")

    if isinstance(signal_data, dict):
        key_findings.append(
            f"Signal reviewed: {signal_data.get('signal', 'Unknown')} "
            f"with score {signal_data.get('score', 0)}/100."
        )
        if signal_data.get("signal") in {"Caution", "Avoid"}:
            concerns.append("Signal is cautious or avoid, so the setup needs more review.")

    if isinstance(regime_data, dict):
        key_findings.append(
            f"Market regime reviewed: {regime_data.get('regime', 'Unknown')}."
        )
        if regime_data.get("regime") in {"High Volatility", "Bear Trend"}:
            concerns.append("Market regime is defensive or volatile.")

    if isinstance(exposure_data, dict):
        exposure_level = exposure_data.get("exposure_level", "Unknown")
        exposure_pct = _safe_number(exposure_data.get("exposure_pct"))
        key_findings.append(f"Exposure reviewed: {exposure_level} ({exposure_pct:.2f}%).")
        if exposure_level == "High":
            concerns.append("Current exposure is high; avoid increasing risk without review.")

    if isinstance(backtest_results, dict):
        strategy_return = _safe_number(backtest_results.get("strategy_return_pct"))
        buy_hold_return = _safe_number(backtest_results.get("buy_and_hold_return_pct"))
        key_findings.append(
            f"Backtest reviewed: strategy {strategy_return:+.2f}% vs buy-and-hold {buy_hold_return:+.2f}%."
        )
        if strategy_return < buy_hold_return:
            concerns.append("Strategy backtest is behind buy-and-hold on this sample.")

    if isinstance(strategy_lab_results, dict):
        key_findings.append(
            f"Strategy lab reviewed: best strategy is {strategy_lab_results.get('best_strategy', 'Unknown')}."
        )

    if isinstance(trade_decision, dict):
        action = trade_decision.get("suggested_action", "Watch")
        confidence = trade_decision.get("confidence", 1)
        key_findings.append(f"Paper decision reviewed: {action} with confidence {confidence}/10.")
        if trade_decision.get("approval_required", True):
            concerns.append("Human approval is required before any paper-trading action.")

    if isinstance(research_memo, dict):
        key_findings.append(
            f"Research memo reviewed: {research_memo.get('overall_stance', 'Unknown')}."
        )

    if volatility_pct >= 30:
        concerns.append("Volatility is elevated.")
    if max_drawdown_pct <= -20:
        concerns.append("Max drawdown is deep enough to require caution.")
    if not concerns:
        concerns.append("No major concerns found, but this still needs human review.")

    recommended_next_actions.extend(
        [
            "Review the signal reasons and risks before saving the research run.",
            "Compare the backtest and strategy lab results against the research memo.",
            "Use paper-trading only if the thesis is clear and risk is acceptable.",
            "Revisit this workflow after new price data is available.",
        ]
    )
    key_findings.append(
        f"Research context reviewed: mode={research_mode}, depth={analysis_depth}."
    )

    if research_mode == "Conservative":
        concerns.append("Conservative mode: keep exposure and confidence tighter than usual.")
    elif research_mode == "Aggressive":
        recommended_next_actions.append(
            "Aggressive mode: double-check volatility and drawdown before scaling paper exposure."
        )

    if analysis_depth == "Quick":
        key_findings = key_findings[:5]
        concerns = concerns[:4]
        recommended_next_actions = recommended_next_actions[:3]
    elif analysis_depth == "Deep":
        recommended_next_actions.append(
            "Deep review: compare this run with recent saved research runs for consistency."
        )

    return {
        "workflow_status": "Complete",
        "steps_completed": steps_completed,
        "key_findings": key_findings,
        "concerns": concerns,
        "recommended_next_actions": recommended_next_actions,
        "needs_human_review": True,
    }
