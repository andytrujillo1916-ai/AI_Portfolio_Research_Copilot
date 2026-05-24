from asset_sector_map import map_asset_to_sector


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mode_thresholds(research_mode):
    if research_mode == "Conservative":
        return {"high_corr_count": 2, "med_corr_count": 1}
    if research_mode == "Aggressive":
        return {"high_corr_count": 4, "med_corr_count": 2}
    return {"high_corr_count": 3, "med_corr_count": 2}


def _infer_cluster_label(symbol, sector):
    if symbol in {"SPY", "VOO", "DIA"}:
        return "Broad Market Cluster"
    if symbol in {"QQQ", "XLK", "AAPL", "MSFT", "NVDA"} or sector == "Technology":
        return "Technology Cluster"
    if symbol in {"BTC", "ETH"}:
        return "Crypto Cluster"
    if sector and sector != "Unknown":
        return f"{sector} Cluster"
    return "Mixed Cluster"


def analyze_cross_asset_correlation(
    screened_assets,
    portfolio_allocations=None,
    research_mode="Balanced",
):
    """Estimate simple cross-asset correlation and overlap risk for research-only use."""
    screened_assets = screened_assets or []
    portfolio_allocations = portfolio_allocations or []
    thresholds = _mode_thresholds(research_mode)

    row_by_symbol = {row.get("symbol"): row for row in screened_assets if row.get("symbol")}

    if portfolio_allocations:
        symbols = [row.get("symbol") for row in portfolio_allocations if row.get("symbol")]
    else:
        symbols = [row.get("symbol") for row in screened_assets[:8] if row.get("symbol")]

    group_map = {}
    high_vol_count = 0
    bull_like_count = 0

    for symbol in symbols:
        row = row_by_symbol.get(symbol, {})
        sector = map_asset_to_sector(symbol)
        label = _infer_cluster_label(symbol, sector)
        group_map.setdefault(label, []).append(symbol)

        vol = _safe_float(row.get("volatility_pct", 0.0))
        if vol >= 30:
            high_vol_count += 1

        regime = str(row.get("regime", "Unknown"))
        if regime in {"Bull Trend", "Recovery"}:
            bull_like_count += 1

    correlation_groups = []
    for group_name, assets in sorted(group_map.items(), key=lambda item: len(item[1]), reverse=True):
        if len(assets) >= thresholds["high_corr_count"]:
            risk_level = "High"
            reasoning = f"{len(assets)} assets share similar behavior in {group_name.lower()}."
        elif len(assets) >= thresholds["med_corr_count"]:
            risk_level = "Medium"
            reasoning = f"{len(assets)} assets overlap in {group_name.lower()}."
        else:
            risk_level = "Low"
            reasoning = f"Limited overlap in {group_name.lower()}."

        correlation_groups.append(
            {
                "group_name": group_name,
                "assets": assets,
                "risk_level": risk_level,
                "reasoning": reasoning,
            }
        )

    most_correlated_cluster = correlation_groups[0] if correlation_groups else {}

    # Diversification score: simple transparent rubric
    unique_groups = len(group_map)
    total_assets = len(symbols)
    overlap_penalty = max(0, total_assets - unique_groups) * 10
    high_vol_penalty = high_vol_count * 4
    regime_alignment_penalty = max(0, bull_like_count - 2) * 3
    diversification_score = max(0, min(100, 80 + unique_groups * 5 - overlap_penalty - high_vol_penalty - regime_alignment_penalty))

    if not symbols:
        hidden_concentration_risk = "No assets were provided for correlation analysis."
    elif most_correlated_cluster and len(most_correlated_cluster.get("assets", [])) >= thresholds["high_corr_count"]:
        hidden_concentration_risk = (
            f"Elevated overlap detected in {most_correlated_cluster.get('group_name', 'a major cluster')}."
        )
    elif high_vol_count >= max(2, thresholds["med_corr_count"]):
        hidden_concentration_risk = "Volatility clustering may increase hidden drawdown risk."
    else:
        hidden_concentration_risk = "No major hidden concentration cluster detected."

    summary = (
        f"{research_mode} mode correlation review found {len(correlation_groups)} groups, "
        f"diversification score {diversification_score}/100."
    )

    return {
        "correlation_groups": correlation_groups,
        "most_correlated_cluster": most_correlated_cluster,
        "hidden_concentration_risk": hidden_concentration_risk,
        "diversification_score": diversification_score,
        "summary": summary,
    }
