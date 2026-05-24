def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mode_cap(research_mode):
    if research_mode == "Conservative":
        return 10.0
    if research_mode == "Aggressive":
        return 20.0
    return 15.0


def _confidence_label(score):
    if score >= 70:
        return "High"
    if score >= 45:
        return "Medium"
    return "Low"


def generate_allocation_timing_recommendation(
    symbol,
    conviction_data,
    signal_data,
    opportunity_data,
    regime_data,
    news_context,
    catalyst_data,
    backtest_results,
    strategy_lab_results,
    benchmark_results,
    risk,
    research_mode="Balanced",
):
    """Generate a research-only allocation and timing recommendation."""
    conviction_score = _safe_float(conviction_data.get("conviction_score", 50))
    signal_score = _safe_float(signal_data.get("score", 50))
    opportunity_score = _safe_float(
        (opportunity_data.get("best_opportunity") or {}).get("opportunity_score", 50)
    )
    regime = str(regime_data.get("regime", "Unknown"))
    sentiment = str(news_context.get("market_sentiment", "Neutral"))
    conviction_risk = str(catalyst_data.get("conviction_risk", "Low"))
    strategy_return = _safe_float(backtest_results.get("strategy_return_pct", 0.0))
    buy_hold_return = _safe_float(backtest_results.get("buy_and_hold_return_pct", 0.0))
    benchmark_edge = _safe_float(benchmark_results.get("edge_vs_benchmark_pct", 0.0))
    volatility = _safe_float(risk.get("volatility_pct", 0.0))
    drawdown = _safe_float(risk.get("max_drawdown_pct", 0.0))

    why = []
    risks = []
    required_conditions = []

    base_score = (
        (conviction_score * 0.35)
        + (signal_score * 0.30)
        + (opportunity_score * 0.15)
        + (50 + benchmark_edge * 2) * 0.20
    ) / 1.0

    if regime == "Bull Trend":
        base_score += 6
        why.append("Bull Trend regime supports constructive timing.")
    elif regime in {"Bear Trend", "High Volatility"}:
        base_score -= 8
        risks.append(f"{regime} regime reduces timing quality.")

    if sentiment == "Bullish":
        base_score += 4
        why.append("Bullish news sentiment supports setup quality.")
    elif sentiment == "Bearish":
        base_score -= 6
        risks.append("Bearish news sentiment is a headwind.")

    if conviction_risk == "High":
        base_score -= 8
        risks.append("Catalyst tracker shows high conviction risk.")
    elif conviction_risk == "Medium":
        base_score -= 3

    if volatility >= 30:
        base_score -= 8
        risks.append("Volatility is elevated and increases downside uncertainty.")
    elif volatility >= 20:
        base_score -= 3

    if drawdown <= -20:
        base_score -= 6
        risks.append("Deep drawdown context reduces allocation confidence.")

    if strategy_return >= buy_hold_return:
        why.append("Strategy backtest is at least as strong as buy-and-hold.")
    else:
        risks.append("Strategy backtest trails buy-and-hold.")

    if benchmark_edge > 0:
        why.append("Current setup is stronger than benchmark context.")
    else:
        risks.append("Benchmark comparison is not favorable right now.")

    cap = _mode_cap(research_mode)
    base_score = max(0, min(100, base_score))
    suggested_allocation_pct = round((base_score / 100) * cap, 2)

    if base_score >= 75 and conviction_risk == "Low":
        action = "Buy Now"
        timing_view = "Momentum and context are aligned for a paper entry."
    elif base_score >= 60:
        action = "Paper Trade Only"
        timing_view = "Constructive setup, but best treated as paper-trading confirmation first."
    elif base_score >= 45:
        action = "Watch"
        timing_view = "Mixed setup; wait for clearer trend and catalyst confirmation."
    elif base_score >= 30:
        action = "Wait for Pullback"
        timing_view = "Risk/reward may improve after volatility cools or pricing resets."
    else:
        action = "Avoid"
        timing_view = "Current setup is weak relative to risk and benchmark context."
        suggested_allocation_pct = 0.0

    if suggested_allocation_pct > cap:
        suggested_allocation_pct = cap
    if suggested_allocation_pct > 0:
        required_conditions.extend(
            [
                "Signal score should remain stable or improve on next review.",
                "Volatility should not rise above current stress threshold.",
                "No major negative catalyst should appear before the next check-in.",
            ]
        )
    else:
        required_conditions.append("Re-run research after regime, volatility, or catalyst conditions improve.")

    benchmark_comparison = (
        f"Strategy return {strategy_return:+.2f}% vs buy-and-hold {buy_hold_return:+.2f}%. "
        f"Estimated edge vs benchmark: {benchmark_edge:+.2f}%."
    )
    confidence_level = _confidence_label(base_score)

    if not why:
        why.append("No strong alignment factors were detected.")
    if not risks:
        risks.append("No major risk flag dominates currently, but uncertainty remains.")

    return {
        "recommended_action": action,
        "suggested_allocation_pct": suggested_allocation_pct,
        "timing_view": timing_view,
        "why": why,
        "risks": risks,
        "benchmark_comparison": benchmark_comparison,
        "confidence_level": confidence_level,
        "required_conditions": required_conditions,
        "disclaimer": "This is research-only decision support, not financial advice or trade execution.",
    }
