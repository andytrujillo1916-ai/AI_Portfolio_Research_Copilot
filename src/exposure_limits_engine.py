from asset_sector_map import map_asset_to_sector


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mode_limits(research_mode):
    if research_mode == "Conservative":
        return {
            "sector_limit": 30.0,
            "single_limit": 15.0,
            "top3_limit": 45.0,
            "high_vol_limit": 25.0,
        }
    if research_mode == "Aggressive":
        return {
            "sector_limit": 40.0,
            "single_limit": 20.0,
            "top3_limit": 60.0,
            "high_vol_limit": 40.0,
        }
    return {
        "sector_limit": 35.0,
        "single_limit": 17.5,
        "top3_limit": 50.0,
        "high_vol_limit": 32.5,
    }


def evaluate_portfolio_exposure_limits(
    portfolio_allocations,
    screened_assets,
    conviction_data=None,
    research_mode="Balanced",
):
    """Evaluate simple portfolio concentration and exposure limits for research-only use."""
    portfolio_allocations = portfolio_allocations or []
    screened_assets = screened_assets or []
    limits = _mode_limits(research_mode)

    symbol_to_row = {row.get("symbol"): row for row in screened_assets if row.get("symbol")}
    symbol_to_weight = {
        row.get("symbol"): _safe_float(row.get("weight_pct", 0.0))
        for row in portfolio_allocations
        if row.get("symbol")
    }

    # Sector aggregation
    sector_totals = {}
    high_vol_exposure_pct = 0.0
    for symbol, weight in symbol_to_weight.items():
        sector = map_asset_to_sector(symbol)
        sector_totals[sector] = sector_totals.get(sector, 0.0) + weight

        vol = _safe_float((symbol_to_row.get(symbol) or {}).get("volatility_pct", 0.0))
        if vol >= 30:
            high_vol_exposure_pct += weight

    sector_exposure = [
        {"sector": sector, "exposure_pct": round(exposure, 2)}
        for sector, exposure in sorted(sector_totals.items(), key=lambda x: x[1], reverse=True)
    ]

    sorted_weights = sorted(symbol_to_weight.items(), key=lambda x: x[1], reverse=True)
    top_position_concentration_pct = round(sorted_weights[0][1], 2) if sorted_weights else 0.0
    top_3_concentration_pct = round(sum(weight for _, weight in sorted_weights[:3]), 2)

    risk_flags = []
    suggested_reductions = []

    for row in sector_exposure:
        if row["exposure_pct"] > limits["sector_limit"]:
            risk_flags.append(
                f"Sector concentration elevated: {row['sector']} at {row['exposure_pct']:.2f}%."
            )
            suggested_reductions.append(
                f"Reduce {row['sector']} exposure toward {limits['sector_limit']:.1f}% or below."
            )

    if top_position_concentration_pct > limits["single_limit"]:
        risk_flags.append(
            f"Top position concentration is high at {top_position_concentration_pct:.2f}%."
        )
        suggested_reductions.append(
            f"Trim largest position toward {limits['single_limit']:.1f}% or below."
        )

    if top_3_concentration_pct > limits["top3_limit"]:
        risk_flags.append(
            f"Top 3 concentration is elevated at {top_3_concentration_pct:.2f}%."
        )
        suggested_reductions.append(
            f"Reduce top-3 concentration toward {limits['top3_limit']:.1f}% or below."
        )

    high_vol_exposure_pct = round(high_vol_exposure_pct, 2)
    if high_vol_exposure_pct > limits["high_vol_limit"]:
        risk_flags.append(
            f"High-volatility exposure is elevated at {high_vol_exposure_pct:.2f}%."
        )
        suggested_reductions.append(
            "Shift some allocation from high-volatility assets into lower-volatility assets."
        )

    # Simple correlated exposure proxy: same-sector clustering
    if sector_exposure and sector_exposure[0]["exposure_pct"] > limits["sector_limit"]:
        risk_flags.append("Correlated sector overlap appears elevated.")

    if conviction_data:
        conviction_score = _safe_float(conviction_data.get("conviction_score", 0.0))
        if conviction_score >= 80 and top_3_concentration_pct > limits["top3_limit"] - 5:
            risk_flags.append("High-conviction clustering may be driving concentration risk.")

    if not risk_flags:
        exposure_status = "Healthy"
    elif len(risk_flags) == 1:
        exposure_status = "Moderate"
    elif len(risk_flags) <= 3:
        exposure_status = "Elevated"
    else:
        exposure_status = "High Risk"

    summary = (
        f"{research_mode} mode exposure check: top position {top_position_concentration_pct:.2f}%, "
        f"top 3 {top_3_concentration_pct:.2f}%, high-vol exposure {high_vol_exposure_pct:.2f}%."
    )

    return {
        "sector_exposure": sector_exposure,
        "high_vol_exposure_pct": high_vol_exposure_pct,
        "top_position_concentration_pct": top_position_concentration_pct,
        "top_3_concentration_pct": top_3_concentration_pct,
        "risk_flags": risk_flags,
        "exposure_status": exposure_status,
        "suggested_reductions": suggested_reductions,
        "summary": summary,
    }
