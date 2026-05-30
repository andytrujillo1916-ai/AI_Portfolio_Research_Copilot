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


def optimize_portfolio(
    ranked_assets,
    research_mode="Balanced",
    max_single_position=0.15,
    cash_buffer=0.10,
):
    """Convert ranked research assets into transparent research-only allocation targets."""
    ranked_assets = ranked_assets or []
    if not ranked_assets:
        return {
            "recommended_allocations": [],
            "cash_allocation_pct": round(cash_buffer * 100, 2),
            "portfolio_risk_level": "Low",
            "concentration_warning": "No ranked assets were provided.",
            "summary": "Portfolio optimizer stayed mostly in cash due to missing ranked inputs.",
        }

    mode = str(research_mode or "Balanced")
    mode_cash = cash_buffer
    mode_cap = max_single_position
    upside_mult = 1.0
    risk_mult = 1.0

    if mode == "Conservative":
        mode_cash = max(cash_buffer, 0.20)
        mode_cap = min(max_single_position, 0.10)
        risk_mult = 1.25
    elif mode == "Aggressive":
        mode_cash = min(cash_buffer, 0.05)
        mode_cap = max(max_single_position, 0.20)
        upside_mult = 1.10
        risk_mult = 0.90

    investable_pct = max(0.0, 1.0 - mode_cash)
    scored = []
    for row in ranked_assets:
        symbol = row.get("symbol", "")
        conviction = _safe_float(row.get("conviction", row.get("opportunity_score", row.get("score", 50.0))))
        volatility = _safe_float(row.get("volatility_pct", 0.0))
        drawdown = abs(_safe_float(row.get("max_drawdown_pct", 0.0)))
        regime = str(row.get("regime", "Unknown"))

        base = conviction * upside_mult
        base -= volatility * 0.55 * risk_mult
        base -= drawdown * 0.35 * risk_mult
        if regime in {"Bear Trend", "High Volatility"}:
            base -= 6
        elif regime in {"Bull Trend", "Recovery"}:
            base += 4

        scored.append(
            {
                "symbol": symbol,
                "score": max(0.0, min(base, 100.0)),
                "volatility_pct": volatility,
                "max_drawdown_pct": drawdown,
                "conviction": conviction,
            }
        )

    scored = [row for row in scored if row["score"] > 0]
    if not scored:
        return {
            "recommended_allocations": [],
            "cash_allocation_pct": round(mode_cash * 100, 2),
            "portfolio_risk_level": "Low",
            "concentration_warning": "All assets were penalized to zero by current risk settings.",
            "summary": "No risk-adjusted allocations were produced in this pass.",
        }

    total_score = sum(row["score"] for row in scored)
    allocations = []
    for row in scored:
        raw_weight = (row["score"] / total_score) * investable_pct
        capped = min(raw_weight, mode_cap)
        allocations.append(
            {
                "symbol": row["symbol"],
                "allocation_pct": capped * 100,
                "reason": (
                    f"Conviction {row['conviction']:.1f}, volatility {row['volatility_pct']:.2f}%, "
                    f"drawdown {row['max_drawdown_pct']:.2f}%."
                ),
            }
        )

    allocated = sum(row["allocation_pct"] for row in allocations)
    target_allocated = investable_pct * 100
    if allocated > 0:
        scale = target_allocated / allocated
        for row in allocations:
            row["allocation_pct"] = round(row["allocation_pct"] * scale, 2)

    allocations.sort(key=lambda row: row.get("allocation_pct", 0), reverse=True)

    top_weight = allocations[0]["allocation_pct"] if allocations else 0.0
    top3_weight = sum(row["allocation_pct"] for row in allocations[:3])
    if top_weight > (mode_cap * 100):
        concentration_warning = "Top position exceeds requested cap."
    elif top3_weight > 60:
        concentration_warning = "Top 3 allocations are concentrated; review diversification."
    else:
        concentration_warning = "No major concentration warning."

    avg_vol = sum(row["volatility_pct"] for row in scored) / len(scored)
    if avg_vol >= 30:
        risk_level = "High"
    elif avg_vol >= 18:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    return {
        "recommended_allocations": allocations,
        "cash_allocation_pct": round(mode_cash * 100, 2),
        "portfolio_risk_level": risk_level,
        "concentration_warning": concentration_warning,
        "summary": (
            f"{mode} mode optimizer allocated {target_allocated:.0f}% across ranked assets "
            f"with a {mode_cash*100:.0f}% cash buffer. Research-only, no execution."
        ),
    }
