def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def generate_research_brief(
    symbol,
    snapshot,
    risk,
    macro_context,
    sector_context,
    news_context,
    regime_data,
    signal_data,
    opportunity_data,
    exposure_data,
    trade_decision,
    research_memo,
    scenario_results,
    stress_test_results,
    factor_attribution,
):
    """Generate a simple research-only brief from the current workflow context."""
    price = snapshot.get("price", "N/A")
    change_pct = _safe_float(snapshot.get("change_pct", 0.0))
    signal = signal_data.get("signal", "Unknown")
    score = _safe_float(signal_data.get("score", 0.0))
    volatility = _safe_float(risk.get("volatility_pct", 0.0))
    drawdown = _safe_float(risk.get("max_drawdown_pct", 0.0))
    regime = regime_data.get("regime", "Unknown")
    sentiment = news_context.get("market_sentiment", "Neutral")
    macro_state = macro_context.get("macro_state", "Neutral")
    strongest_sector = (sector_context.get("strongest_sector") or {}).get("sector", "Unknown")
    best_opportunity = (opportunity_data.get("best_opportunity") or {}).get("symbol", "N/A")
    action = trade_decision.get("suggested_action", "Watch")
    confidence = trade_decision.get("confidence", "N/A")
    exposure_level = exposure_data.get("exposure_level", "Unknown")
    scenario_summary = scenario_results.get("overall_scenario_summary", "No scenario summary available.")
    stress_summary = stress_test_results.get("summary", "No stress test summary available.")
    factor_summary = factor_attribution.get("summary", "No factor attribution summary available.")
    risk_driver = (factor_attribution.get("risk_driver") or {}).get("factor", "No major risk driver")

    watch_items = [
        f"Monitor volatility at {volatility:.2f}% and drawdown at {drawdown:.2f}%.",
        f"Track regime change risk from current state: {regime}.",
        f"Review sentiment shifts from current news state: {sentiment}.",
        f"Re-check exposure level ({exposure_level}) before any paper-trading changes.",
        f"Watch strongest sector leadership: {strongest_sector}.",
    ]

    return {
        "title": f"Research Brief: {symbol}",
        "summary": (
            f"{symbol} shows {signal} conditions (score {score:.0f}/100) with "
            f"macro state {macro_state} and regime {regime}."
        ),
        "market_context": (
            f"Price is {price}, daily change is {change_pct:+.2f}%, macro state is {macro_state}, "
            f"and strongest sector context is {strongest_sector}."
        ),
        "signal_summary": (
            f"Signal: {signal} ({score:.0f}/100). Best screened opportunity: {best_opportunity}. "
            f"News sentiment is {sentiment}."
        ),
        "risk_summary": (
            f"Volatility {volatility:.2f}%, max drawdown {drawdown:.2f}%, exposure level {exposure_level}. "
            f"Main risk driver: {risk_driver}."
        ),
        "scenario_summary": f"{scenario_summary} {stress_summary}",
        "portfolio_implication": (
            f"{macro_context.get('portfolio_implication', 'Keep allocations balanced.')}"
        ),
        "decision_summary": (
            f"Trade Decision Assistant suggests: {action} with confidence {confidence}/10. "
            f"Research memo stance: {research_memo.get('overall_stance', 'Unknown')}."
        ),
        "watch_items": watch_items,
        "disclaimer": (
            "Research-only brief for learning and paper-trading context. "
            "Not financial advice. No live execution or broker connectivity."
        ),
    }
