def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mode_weights(research_mode):
    if research_mode == "Conservative":
        return {"upside": 0.9, "risk_penalty": 1.2}
    if research_mode == "Aggressive":
        return {"upside": 1.1, "risk_penalty": 0.9}
    return {"upside": 1.0, "risk_penalty": 1.0}


def _tier_from_score(score):
    if score >= 70:
        return "Core", "Increase"
    if score >= 55:
        return "Secondary", "Hold"
    if score >= 40:
        return "Watch", "Limit"
    return "Avoid", "Avoid"


def build_capital_allocation_hierarchy(
    screened_assets,
    portfolio_allocations=None,
    conviction_data=None,
    execution_data=None,
    alpha_data=None,
    correlation_data=None,
    research_mode="Balanced",
):
    """Build a transparent, research-only priority hierarchy for capital attention."""
    screened_assets = screened_assets or []
    portfolio_allocations = portfolio_allocations or []
    conviction_data = conviction_data or {}
    execution_data = execution_data or {}
    alpha_data = alpha_data or {}
    correlation_data = correlation_data or {}

    weights = _mode_weights(research_mode)

    conviction_score = _safe_float(conviction_data.get("conviction_score", 50.0))
    execution_score = _safe_float(execution_data.get("execution_score", 50.0))
    alpha_pct = _safe_float(alpha_data.get("alpha_pct", 0.0))
    diversification_score = _safe_float(correlation_data.get("diversification_score", 50.0))
    hidden_risk_text = str(correlation_data.get("hidden_concentration_risk", "")).lower()
    hidden_risk_penalty = 8.0 if "elevated" in hidden_risk_text or "risk" in hidden_risk_text else 0.0

    alloc_map = {row.get("symbol"): _safe_float(row.get("weight_pct", 0.0)) for row in portfolio_allocations}

    hierarchy = []
    for row in screened_assets:
        symbol = row.get("symbol", "")
        if not symbol:
            continue

        signal_score = _safe_float(row.get("score", 50.0))
        volatility = _safe_float(row.get("volatility_pct", 25.0))
        drawdown = abs(_safe_float(row.get("max_drawdown_pct", 10.0)))
        regime = str(row.get("regime", "Unknown"))
        current_weight = alloc_map.get(symbol, 0.0)

        positive = (
            signal_score * 0.45
            + conviction_score * 0.20
            + execution_score * 0.15
            + max(-10.0, min(10.0, alpha_pct * 2.0)) * 1.0
            + diversification_score * 0.10
        ) * weights["upside"]

        regime_bonus = 4.0 if regime in {"Bull Trend", "Recovery"} else -3.0 if regime == "Bear Trend" else 0.0
        concentration_penalty = max(0.0, current_weight - 15.0) * 0.8
        risk_penalty = (volatility * 0.30 + drawdown * 0.25 + concentration_penalty + hidden_risk_penalty) * weights["risk_penalty"]

        final_score = max(0.0, min(100.0, positive + regime_bonus - risk_penalty))
        tier, bias = _tier_from_score(final_score)

        reasoning = (
            f"Signal {signal_score:.0f}, vol {volatility:.1f}%, drawdown {drawdown:.1f}%, "
            f"regime {regime}, allocation {current_weight:.1f}%."
        )

        hierarchy.append(
            {
                "symbol": symbol,
                "capital_priority": 0,
                "tier": tier,
                "allocation_bias": bias,
                "reasoning": reasoning,
                "_score": round(final_score, 2),
                "_volatility_pct": volatility,
            }
        )

    hierarchy.sort(key=lambda item: item.get("_score", 0.0), reverse=True)
    for idx, item in enumerate(hierarchy, start=1):
        item["capital_priority"] = idx
        item.pop("_score", None)

    top_candidate = hierarchy[0] if hierarchy else {}
    lowest_priority = hierarchy[-1] if hierarchy else {}

    avg_vol = 0.0
    if screened_assets:
        avg_vol = sum(_safe_float(row.get("volatility_pct", 0.0)) for row in screened_assets) / len(screened_assets)

    if diversification_score >= 70 and avg_vol < 30:
        efficiency = "Portfolio ideas are fairly efficient: quality signals with manageable clustering."
    elif diversification_score >= 50:
        efficiency = "Portfolio efficiency is mixed: opportunities exist, but concentration should stay monitored."
    else:
        efficiency = "Portfolio efficiency is weaker: correlation and risk clustering deserve caution."

    summary = (
        f"{research_mode} hierarchy built across {len(hierarchy)} assets. "
        f"Top tier count: {sum(1 for item in hierarchy if item.get('tier') == 'Core')}."
    )

    return {
        "capital_hierarchy": hierarchy,
        "top_capital_candidate": top_candidate,
        "lowest_priority_asset": lowest_priority,
        "portfolio_efficiency_view": efficiency,
        "summary": summary,
    }
