"""Market timing and crash-risk context.

This module estimates risk conditions from broad market proxies and scan breadth.
It does not predict crashes with certainty.
"""


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _average(values):
    values = [value for value in values if value is not None]
    return sum(values) / len(values) if values else 0.0


def build_market_timing_context(index_data, scan_results, sector_context, macro_context, profile):
    """Build a broad market crash-risk and buy-zone dashboard context."""
    index_data = index_data or {}
    scan_results = scan_results or []
    sector_context = sector_context or {}
    macro_context = macro_context or {}
    profile = profile or {}

    warnings = []
    positives = []

    index_rows = []
    if isinstance(index_data, dict):
        index_rows = index_data.get("rows", [])
    if not index_rows:
        index_rows = [row for row in scan_results if row.get("symbol") in {"SPY", "QQQ", "IWM"}]

    avg_index_return = _average([_safe_float(row.get("return_pct")) for row in index_rows])
    avg_index_vol = _average([_safe_float(row.get("volatility_pct")) for row in index_rows])
    worst_index_drawdown = min([_safe_float(row.get("max_drawdown_pct")) for row in index_rows] or [0.0])

    advancers = sum(1 for row in scan_results if _safe_float(row.get("return_pct")) > 0)
    decliners = sum(1 for row in scan_results if _safe_float(row.get("return_pct")) < 0)
    breadth_pct = (advancers / len(scan_results) * 100) if scan_results else 0.0
    blocked_count = sum(1 for row in scan_results if row.get("recommendation_gate") == "Blocked")

    risk_points = 0
    if avg_index_return < -5:
        risk_points += 2
        warnings.append("Broad index trend is negative.")
    elif avg_index_return > 3:
        positives.append("Broad index trend is positive.")

    if avg_index_vol >= 30:
        risk_points += 2
        warnings.append("Broad market volatility is elevated.")
    elif 0 < avg_index_vol <= 18:
        positives.append("Broad market volatility is contained.")

    if worst_index_drawdown <= -15:
        risk_points += 2
        warnings.append("Broad index drawdown is deep enough to require caution.")
    elif worst_index_drawdown <= -8:
        risk_points += 1
        warnings.append("Broad index drawdown is meaningful but not yet a severe stress signal.")

    if breadth_pct < 35 and scan_results:
        risk_points += 2
        warnings.append("Market breadth is weak across the scanned universe.")
    elif breadth_pct >= 55:
        positives.append("Market breadth is supportive across the scanned universe.")

    macro_state = macro_context.get("macro_state", "Neutral")
    if macro_state == "Risk-Off":
        risk_points += 1
        warnings.append("Macro context is risk-off.")
    elif macro_state == "Risk-On":
        positives.append("Macro context is risk-on.")

    monthly_surplus = _safe_float(profile.get("monthly_income")) - _safe_float(profile.get("monthly_expenses"))
    emergency_fund = _safe_float(profile.get("emergency_fund"))
    monthly_expenses = _safe_float(profile.get("monthly_expenses"))
    emergency_months = emergency_fund / monthly_expenses if monthly_expenses > 0 else 0.0
    if monthly_surplus < 0 or (monthly_expenses > 0 and emergency_months < 3):
        risk_points += 2
        warnings.append("Personal cash safety is weak, so market timing should favor cash first.")

    if risk_points >= 6:
        market_risk_level = "High"
        timing_regime = "Stress"
        cash_plan = "Keep a larger cash buffer; only paper-test or watch strategic buy zones."
    elif risk_points >= 4:
        market_risk_level = "Elevated"
        timing_regime = "Risk-Off"
        cash_plan = "Deploy slowly in tranches only when data and suitability gates pass."
    elif risk_points >= 2:
        market_risk_level = "Moderate"
        timing_regime = "Mixed"
        cash_plan = "Use selective adds and keep dry powder for pullbacks."
    elif avg_index_return > 0 and breadth_pct >= 50:
        market_risk_level = "Low"
        timing_regime = "Risk-On"
        cash_plan = "Risk deployment can be considered for high-quality final verdicts."
    else:
        market_risk_level = "Moderate"
        timing_regime = "Recovery"
        cash_plan = "Favor staged entries and avoid chasing extended moves."

    strategic_buy_zones = [
        "Fresh data gate plus positive final verdict.",
        "Pullback toward support with volatility cooling.",
        "Broad market risk not High, or position size reduced for stress conditions.",
        "Thesis and catalyst remain intact after the pullback.",
    ]
    if market_risk_level in {"Elevated", "High"}:
        strategic_buy_zones.insert(0, "Wait for panic-free stabilization before adding new risk.")

    if not warnings:
        warnings.append("No major crash-risk warning from V1 timing inputs.")
    if not positives:
        positives.append("No strong broad-market positive timing signal is confirmed yet.")

    return {
        "market_risk_level": market_risk_level,
        "timing_regime": timing_regime,
        "breadth_pct": round(breadth_pct, 1),
        "advancers": advancers,
        "decliners": decliners,
        "avg_index_return_pct": round(avg_index_return, 2),
        "avg_index_volatility_pct": round(avg_index_vol, 2),
        "worst_index_drawdown_pct": round(worst_index_drawdown, 2),
        "blocked_data_count": blocked_count,
        "crash_warning_flags": warnings,
        "positive_timing_factors": positives,
        "strategic_buy_zones": strategic_buy_zones,
        "cash_deployment_plan": cash_plan,
        "sector_context_summary": sector_context.get("summary", "Sector context is supporting evidence only."),
        "summary": (
            f"Market timing regime is {timing_regime} with {market_risk_level} crash-risk conditions. "
            "This is a risk dashboard, not a guaranteed crash prediction."
        ),
    }

