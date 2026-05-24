from asset_sector_map import map_asset_to_sector


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value, low, high):
    return max(low, min(high, value))


def _mode_settings(research_mode):
    if research_mode == "Conservative":
        return {"risk_penalty": 0.95, "drawdown_penalty": 0.6, "max_weight": 35, "cash": 20}
    if research_mode == "Aggressive":
        return {"risk_penalty": 0.45, "drawdown_penalty": 0.3, "max_weight": 55, "cash": 5}
    return {"risk_penalty": 0.65, "drawdown_penalty": 0.45, "max_weight": 45, "cash": 10}


def _extract_sector_extremes(sector_context):
    strongest = {}
    weakest = {}
    if isinstance(sector_context, dict):
        strongest = sector_context.get("strongest_sector", {}) or {}
        weakest = sector_context.get("weakest_sector", {}) or {}
    return strongest.get("sector", ""), weakest.get("sector", "")


def generate_portfolio_allocation(
    screened_assets,
    research_mode="Balanced",
    sector_context=None,
):
    """Create simple research-only portfolio allocation ideas from screened assets."""
    if not screened_assets:
        return {
            "allocations": [],
            "cash_buffer_pct": 100,
            "portfolio_risk_level": "Low",
            "summary": "No screened assets were available, so allocation stays in cash for research safety.",
        }

    settings = _mode_settings(research_mode)
    strongest_sector, weakest_sector = _extract_sector_extremes(sector_context)
    scored = []

    for row in screened_assets:
        symbol = row.get("symbol", "Unknown")
        signal_score = _safe_float(row.get("score", 0))
        volatility = _safe_float(row.get("volatility_pct", 0))
        drawdown = abs(_safe_float(row.get("max_drawdown_pct", 0)))
        regime = str(row.get("regime", "Unknown"))
        sentiment = str(row.get("news_sentiment", "Neutral"))
        mapped_sector = map_asset_to_sector(symbol)

        base = signal_score
        base -= volatility * settings["risk_penalty"]
        base -= drawdown * settings["drawdown_penalty"]

        if regime == "Bull Trend":
            base += 5
        elif regime in {"Bear Trend", "High Volatility"}:
            base -= 5

        if sentiment == "Bullish":
            base += 3
        elif sentiment == "Bearish":
            base -= 3

        sector_adjustment = 0.0
        if mapped_sector != "Unknown":
            if mapped_sector == strongest_sector:
                sector_adjustment = 2.0
            elif mapped_sector == weakest_sector:
                sector_adjustment = -2.0
        base += sector_adjustment

        scored.append(
            {
                "symbol": symbol,
                "raw_score": _clamp(base, 0, 100),
                "volatility_pct": volatility,
                "max_drawdown_pct": drawdown,
                "regime": regime,
                "signal_score": signal_score,
                "mapped_sector": mapped_sector,
                "sector_adjustment": sector_adjustment,
            }
        )

    scored = [item for item in scored if item["raw_score"] > 0]
    if not scored:
        return {
            "allocations": [],
            "cash_buffer_pct": settings["cash"],
            "portfolio_risk_level": "Low",
            "summary": "All screened assets were too weak after risk penalties, so the model keeps a high cash posture.",
        }

    total_score = sum(item["raw_score"] for item in scored)
    investable_pct = 100 - settings["cash"]
    allocations = []

    for item in scored:
        uncapped_weight = (item["raw_score"] / total_score) * investable_pct
        weight_pct = min(uncapped_weight, settings["max_weight"])
        reason = (
            f"Signal {item['signal_score']:.0f}, volatility {item['volatility_pct']:.2f}%, "
            f"drawdown {item['max_drawdown_pct']:.2f}%, regime {item['regime']}."
        )
        if item["mapped_sector"] != "Unknown":
            reason += (
                f" Sector context: {item['mapped_sector']} "
                f"({item['sector_adjustment']:+.1f} score adjustment)."
            )
        allocations.append(
            {
                "symbol": item["symbol"],
                "weight_pct": weight_pct,
                "reason": reason,
            }
        )

    allocated = sum(item["weight_pct"] for item in allocations)
    if allocated > 0:
        scale = investable_pct / allocated
        for item in allocations:
            item["weight_pct"] *= scale

    allocations = sorted(allocations, key=lambda item: item["weight_pct"], reverse=True)
    rounded_total = 0
    for item in allocations:
        item["weight_pct"] = round(item["weight_pct"], 2)
        rounded_total += item["weight_pct"]

    if allocations:
        adjustment = round(investable_pct - rounded_total, 2)
        allocations[0]["weight_pct"] = round(allocations[0]["weight_pct"] + adjustment, 2)

    avg_vol = sum(item["volatility_pct"] for item in scored) / len(scored)
    if avg_vol >= 30:
        risk_level = "High"
    elif avg_vol >= 18:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    summary = (
        f"{research_mode} mode keeps a {settings['cash']}% cash buffer and allocates the rest using "
        "signal strength with volatility/drawdown penalties."
    )
    if sector_context:
        summary += " Sector context included with small score nudges for stronger/weaker sectors."

    return {
        "allocations": allocations,
        "cash_buffer_pct": settings["cash"],
        "portfolio_risk_level": risk_level,
        "summary": summary,
    }
