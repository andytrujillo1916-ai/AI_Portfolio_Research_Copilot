from asset_sector_map import map_asset_to_sector


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _impact_label(score):
    if score >= 8:
        return "High"
    if score >= 4:
        return "Medium"
    return "Low"


def analyze_factor_attribution(
    screened_assets,
    portfolio_allocations=None,
    research_mode="Balanced",
):
    """Explain key upside and risk factors with simple research-only rules."""
    screened_assets = screened_assets or []
    portfolio_allocations = portfolio_allocations or []

    if not screened_assets:
        return {
            "positive_factors": [],
            "negative_factors": [],
            "dominant_factor": {},
            "risk_driver": {},
            "summary": "No screened assets were available for factor attribution.",
        }

    avg_score = sum(_safe_float(a.get("score", 0.0)) for a in screened_assets) / len(screened_assets)
    avg_vol = sum(_safe_float(a.get("volatility_pct", 0.0)) for a in screened_assets) / len(screened_assets)
    avg_drawdown = sum(abs(_safe_float(a.get("max_drawdown_pct", 0.0))) for a in screened_assets) / len(screened_assets)
    bearish_regime_count = sum(
        1 for a in screened_assets if str(a.get("regime", "")) in {"Bear Trend", "High Volatility"}
    )
    bearish_news_count = sum(
        1 for a in screened_assets if str(a.get("news_sentiment", "")) == "Bearish"
    )

    positive_factors = []
    negative_factors = []

    top_assets = sorted(screened_assets, key=lambda x: _safe_float(x.get("score", 0.0)), reverse=True)[:3]
    strong_sector_assets = [a for a in top_assets if map_asset_to_sector(a.get("symbol", "")) in {"Technology", "Energy", "Healthcare"}]
    if avg_score >= 65:
        positive_factors.append(
            {
                "factor": "Signal score quality",
                "impact": _impact_label(9 if research_mode == "Aggressive" else 7),
                "reasoning": f"Average signal score is {avg_score:.2f}, which supports upside research setups.",
            }
        )
    if strong_sector_assets:
        positive_factors.append(
            {
                "factor": "Sector strength alignment",
                "impact": _impact_label(7),
                "reasoning": "Top-ranked assets are aligned with historically strong sector proxies in the current screen.",
            }
        )
    if bearish_news_count <= 1:
        positive_factors.append(
            {
                "factor": "News sentiment balance",
                "impact": _impact_label(5),
                "reasoning": "Most screened assets are not showing strongly bearish news sentiment.",
            }
        )

    concentration = 0.0
    if portfolio_allocations:
        concentration = max(_safe_float(item.get("weight_pct", 0.0)) for item in portfolio_allocations)
    if avg_vol >= 25:
        negative_factors.append(
            {
                "factor": "Volatility pressure",
                "impact": _impact_label(9 if research_mode == "Conservative" else 7),
                "reasoning": f"Average volatility is {avg_vol:.2f}%, which increases uncertainty and downside swings.",
            }
        )
    if avg_drawdown >= 12:
        negative_factors.append(
            {
                "factor": "Drawdown depth",
                "impact": _impact_label(7),
                "reasoning": f"Average max drawdown is {avg_drawdown:.2f}%, so caution is warranted on downside risk.",
            }
        )
    if bearish_regime_count >= max(2, len(screened_assets) // 3):
        negative_factors.append(
            {
                "factor": "Regime risk",
                "impact": _impact_label(8),
                "reasoning": "A meaningful share of assets are in weak or high-volatility regimes.",
            }
        )
    if concentration >= 35:
        negative_factors.append(
            {
                "factor": "Concentration risk",
                "impact": _impact_label(8),
                "reasoning": f"Largest allocation is {concentration:.2f}%, which can magnify single-asset risk.",
            }
        )

    if research_mode == "Conservative":
        negative_factors.append(
            {
                "factor": "Conservative risk emphasis",
                "impact": "Medium",
                "reasoning": "Conservative mode prioritizes capital protection and highlights risk drivers.",
            }
        )
    elif research_mode == "Aggressive":
        positive_factors.append(
            {
                "factor": "Aggressive upside emphasis",
                "impact": "Medium",
                "reasoning": "Aggressive mode gives slightly more weight to upside signal quality.",
            }
        )

    dominant_factor = positive_factors[0] if positive_factors else {
        "factor": "Balanced signals",
        "impact": "Low",
        "reasoning": "No single positive factor is currently dominant."
    }
    risk_driver = negative_factors[0] if negative_factors else {
        "factor": "No major risk driver",
        "impact": "Low",
        "reasoning": "Current screen does not show a dominant risk cluster."
    }

    summary = (
        f"{research_mode} mode attribution suggests "
        f"{len(positive_factors)} positive and {len(negative_factors)} caution factors. "
        "Use this as qualitative research context, not a prediction."
    )

    return {
        "positive_factors": positive_factors,
        "negative_factors": negative_factors,
        "dominant_factor": dominant_factor,
        "risk_driver": risk_driver,
        "summary": summary,
    }
