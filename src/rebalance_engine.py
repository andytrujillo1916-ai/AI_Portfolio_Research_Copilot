from asset_sector_map import map_asset_to_sector


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mode_settings(research_mode):
    if research_mode == "Conservative":
        return {"threshold": 3.0, "max_shift": 10.0}
    if research_mode == "Aggressive":
        return {"threshold": 1.5, "max_shift": 15.0}
    return {"threshold": 2.0, "max_shift": 12.0}


def _sector_shift_note(symbol, sector_context):
    if not sector_context:
        return ""
    strongest = (sector_context.get("strongest_sector") or {}).get("sector", "")
    weakest = (sector_context.get("weakest_sector") or {}).get("sector", "")
    sector = map_asset_to_sector(symbol)
    if sector and sector != "Unknown":
        if sector == strongest:
            return " Sector context supports this shift."
        if sector == weakest:
            return " Sector context suggests extra caution."
    return ""


def generate_rebalance_plan(
    current_allocations,
    recommended_allocations,
    research_mode="Balanced",
    sector_context=None,
):
    """Generate a simple research-only rebalance suggestion plan."""
    current_allocations = current_allocations or {}
    recommended_allocations = recommended_allocations or []
    settings = _mode_settings(research_mode)

    target_map = {
        item.get("symbol"): _safe_float(item.get("weight_pct", 0.0))
        for item in recommended_allocations
        if item.get("symbol")
    }
    symbols = sorted(set(current_allocations.keys()) | set(target_map.keys()))

    actions = []
    total_turnover = 0.0
    for symbol in symbols:
        current_weight = _safe_float(current_allocations.get(symbol, 0.0))
        target_raw = _safe_float(target_map.get(symbol, 0.0))
        raw_change = target_raw - current_weight

        # Keep shifts readable and avoid excessive churn.
        if abs(raw_change) < settings["threshold"]:
            target_weight = current_weight
            change_pct = 0.0
            action = "Hold"
            reasoning = "Difference is below rebalance threshold, so no action is suggested."
        else:
            capped_change = max(-settings["max_shift"], min(settings["max_shift"], raw_change))
            target_weight = round(current_weight + capped_change, 2)
            change_pct = round(capped_change, 2)
            action = "Increase" if change_pct > 0 else "Reduce"
            reasoning = (
                f"Current {current_weight:.2f}% vs target {target_raw:.2f}% with "
                f"{research_mode} mode shift cap {settings['max_shift']:.1f}%."
            )
            reasoning += _sector_shift_note(symbol, sector_context)

        total_turnover += abs(change_pct)
        actions.append(
            {
                "symbol": symbol,
                "action": action,
                "current_weight": round(current_weight, 2),
                "target_weight": round(target_weight, 2),
                "change_pct": change_pct,
                "reasoning": reasoning,
            }
        )

    actions.sort(key=lambda row: abs(row.get("change_pct", 0.0)), reverse=True)
    largest_shift = actions[0] if actions else {}
    portfolio_turnover_pct = round(total_turnover / 2, 2)

    if portfolio_turnover_pct >= 20:
        risk_note = "Turnover is high; consider phasing changes over multiple research reviews."
    elif portfolio_turnover_pct >= 10:
        risk_note = "Turnover is moderate; verify that shifts are consistent with current risk context."
    else:
        risk_note = "Turnover is modest and aligned with a measured rebalance approach."

    summary = (
        f"{research_mode} mode rebalance uses small, threshold-based shifts and avoids forced reallocation."
    )

    return {
        "rebalance_actions": actions,
        "largest_shift": largest_shift,
        "portfolio_turnover_pct": portfolio_turnover_pct,
        "risk_note": risk_note,
        "summary": summary,
    }
