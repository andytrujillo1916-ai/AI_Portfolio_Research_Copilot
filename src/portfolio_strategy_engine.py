from asset_sector_map import map_asset_to_sector
from fundamental_catalyst_engine import generate_fundamental_catalyst_context
from multi_horizon_router import route_multi_horizon_opportunity


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _profile_risk_score(profile):
    risk = str((profile or {}).get("risk_tolerance", "Moderate"))
    return {"Low": 30, "Moderate": 55, "High": 75}.get(risk, 55)


def _monthly_surplus(profile):
    return _safe_float(profile.get("monthly_income")) - _safe_float(profile.get("monthly_expenses"))


def _emergency_months(profile):
    expenses = _safe_float(profile.get("monthly_expenses"))
    if expenses <= 0:
        return 0.0
    return _safe_float(profile.get("emergency_fund")) / expenses


def _data_gate(row):
    gate = row.get("recommendation_gate", "Warning")
    if gate == "Blocked" or row.get("data_confidence") == "Low":
        return "Blocked"
    if gate == "Trusted" and row.get("data_confidence") == "High":
        return "Trusted"
    return "Warning"


def _portfolio_value(profile, holdings):
    holdings_value = sum(_safe_float(row.get("current_value")) for row in holdings or [])
    return holdings_value + _safe_float((profile or {}).get("cash"))


def _holding_by_symbol(holdings):
    return {str(row.get("symbol", "")).upper(): row for row in holdings or []}


def _base_candidate(row):
    return {
        "symbol": row.get("symbol", ""),
        "score": round(_safe_float(row.get("score")), 1),
        "action": "",
        "data_confidence": row.get("data_confidence", "Unknown"),
        "recommendation_gate": row.get("recommendation_gate", "Warning"),
        "reasons": [],
        "risks": [],
        "suitability_notes": [],
        "human_review_required": True,
        "confidence_level": "Low",
        "target_allocation_band": "0%",
        "risk_budget": "No new risk",
        "time_horizon": "Review",
        "invalidation_triggers": [],
        "accuracy_context": {},
    }


def _decorate_candidate(candidate, router, accuracy_context, action):
    confidence = router.get("confidence_level", "Low")
    if action in {"Buy Candidate", "Add"}:
        if confidence == "High":
            allocation = "3-6% max starter band"
            risk_budget = "Risk no more than 1.0% of portfolio value on thesis failure."
        elif confidence == "Moderate":
            allocation = "1-3% starter band"
            risk_budget = "Risk no more than 0.5% of portfolio value on thesis failure."
        else:
            allocation = "Watchlist only"
            risk_budget = "No new risk until evidence improves."
    elif action == "Trim":
        allocation = "Reduce toward profile cap"
        risk_budget = "Lower concentration before adding risk."
    elif action == "Sell Candidate":
        allocation = "Exit candidate after review"
        risk_budget = "Avoid adding risk to weak thesis."
    else:
        allocation = "Maintain current exposure"
        risk_budget = "Do not increase risk."

    candidate["confidence_level"] = confidence
    candidate["target_allocation_band"] = allocation
    candidate["risk_budget"] = risk_budget
    candidate["time_horizon"] = router.get("best_horizon", "Swing")
    candidate["expected_holding_period"] = router.get("expected_holding_period", "2-12 weeks")
    candidate["invalidation_triggers"] = [
        "Data gate becomes Blocked or source quality deteriorates.",
        "Signal score falls below 45.",
        "Position breaches max exposure or drawdown budget.",
        "Benchmark-relative performance weakens materially.",
    ]
    candidate["accuracy_context"] = {
        "confidence_adjustment": accuracy_context.get("confidence_adjustment", 0.0),
        "hit_rate": accuracy_context.get("hit_rate", 0.0),
        "evaluated_count": accuracy_context.get("evaluated_count", 0),
    }
    if router.get("blocked_reasons"):
        candidate["risks"].extend(router.get("blocked_reasons", []))
    candidate["reasons"].extend(router.get("why", [])[:2])
    return candidate


def evaluate_financial_suitability(profile):
    """Summarize personal-finance constraints before investment recommendations."""
    profile = profile or {}
    surplus = _monthly_surplus(profile)
    emergency_months = _emergency_months(profile)
    debt = _safe_float(profile.get("debt"))
    risk_score = _profile_risk_score(profile)
    notes = []
    risk_actions = []

    emergency_fund_low = emergency_months < 3
    if emergency_fund_low:
        notes.append("Emergency fund is below 3 months of expenses.")
        risk_actions.append("Prioritize emergency cash before adding new stock exposure.")
    elif emergency_months < 6:
        notes.append("Emergency fund is between 3 and 6 months; keep cash buffer meaningful.")
    else:
        notes.append("Emergency fund is at least 6 months based on entered expenses.")

    if surplus <= 0:
        notes.append("Monthly cash flow is not positive based on entered income and expenses.")
        risk_actions.append("Avoid new buys until monthly cash flow is positive.")
    if debt > _safe_float(profile.get("cash")) + _safe_float(profile.get("emergency_fund")):
        notes.append("Debt is high relative to cash and emergency fund.")
        risk_actions.append("Review debt payoff before increasing portfolio risk.")

    horizon = str(profile.get("investment_horizon", "3-5 years"))
    if "0-1" in horizon or "1-3" in horizon:
        risk_actions.append("Short time horizon favors cash, broad ETFs, or lower-volatility holdings.")

    if risk_score <= 35:
        risk_actions.append("Low risk tolerance favors smaller single-stock allocations.")

    status = "Ready for selective investing"
    if emergency_fund_low or len(risk_actions) >= 2:
        status = "De-risk first"
    elif risk_actions:
        status = "Proceed cautiously"

    return {
        "status": status,
        "monthly_surplus": round(surplus, 2),
        "emergency_months": round(emergency_months, 1),
        "risk_score": risk_score,
        "suitability_notes": notes,
        "risk_actions": risk_actions,
    }


def build_portfolio_strategy(
    financial_profile,
    real_holdings,
    scan_results,
    benchmark_truth=None,
    decision_intelligence=None,
    accuracy_context=None,
):
    """Build advisor-style, non-executing portfolio strategy from local inputs."""
    financial_profile = financial_profile or {}
    real_holdings = real_holdings or []
    scan_results = scan_results or []
    benchmark_truth = benchmark_truth or {}
    decision_intelligence = decision_intelligence or {}
    accuracy_context = accuracy_context or {}

    suitability = evaluate_financial_suitability(financial_profile)
    holdings_by_symbol = _holding_by_symbol(real_holdings)
    total_value = _portfolio_value(financial_profile, real_holdings)
    max_single = _safe_float(financial_profile.get("max_single_stock_exposure"), 15.0)
    max_sector = _safe_float(financial_profile.get("max_sector_exposure"), 35.0)

    buy_candidates = []
    sell_candidates = []
    hold_candidates = []
    trim_candidates = []
    risk_actions = list(suitability.get("risk_actions", []))
    sector_values = {}

    for holding in real_holdings:
        symbol = str(holding.get("symbol", "")).upper()
        value = _safe_float(holding.get("current_value"))
        sector = map_asset_to_sector(symbol)
        sector_values[sector] = sector_values.get(sector, 0.0) + value
        exposure_pct = (value / total_value * 100) if total_value > 0 else 0.0
        match = next((row for row in scan_results if row.get("symbol") == symbol), {})
        gate = _data_gate(match) if match else "Warning"
        score = _safe_float(match.get("score"), 50.0) if match else 50.0

        candidate = _base_candidate({"symbol": symbol, **match})
        fundamentals = generate_fundamental_catalyst_context(symbol)
        router = route_multi_horizon_opportunity(
            symbol,
            {**match, "recommendation_gate": gate, "score": score},
            match,
            fundamentals,
            {},
            accuracy_context,
            financial_profile,
        )
        candidate["current_exposure_pct"] = round(exposure_pct, 2)
        candidate["reasons"].append(f"Current position exposure is {exposure_pct:.1f}% of entered portfolio.")

        if exposure_pct > max_single:
            candidate["action"] = "Trim"
            candidate["risks"].append(f"Position exceeds max single-stock exposure of {max_single:.1f}%.")
            candidate["suitability_notes"].append("Trim sizing before adding new exposure.")
            trim_candidates.append(_decorate_candidate(candidate, router, accuracy_context, "Trim"))
        elif gate == "Blocked":
            candidate["action"] = "Hold"
            candidate["risks"].append("Data quality blocks sell/buy recommendation; review manually.")
            hold_candidates.append(_decorate_candidate(candidate, router, accuracy_context, "Hold"))
        elif score < 40:
            candidate["action"] = "Sell Candidate"
            candidate["risks"].append("Weak current score with acceptable data gate.")
            candidate["suitability_notes"].append("Human review required before any real sell decision.")
            sell_candidates.append(_decorate_candidate(candidate, router, accuracy_context, "Sell Candidate"))
        else:
            candidate["action"] = "Hold"
            candidate["reasons"].append("Existing holding does not trigger trim or sell rules.")
            hold_candidates.append(_decorate_candidate(candidate, router, accuracy_context, "Hold"))

    for sector, value in sector_values.items():
        exposure = (value / total_value * 100) if total_value > 0 else 0.0
        if exposure > max_sector:
            risk_actions.append(f"{sector} exposure is {exposure:.1f}%, above max sector target {max_sector:.1f}%.")

    owned = set(holdings_by_symbol.keys())
    can_add_risk = suitability.get("status") == "Ready for selective investing"
    for row in sorted(scan_results, key=lambda item: item.get("score", 0), reverse=True):
        symbol = str(row.get("symbol", "")).upper()
        if symbol in owned:
            continue
        if len(buy_candidates) >= 8:
            break

        gate = _data_gate(row)
        score = _safe_float(row.get("score"))
        candidate = _base_candidate(row)
        fundamentals = generate_fundamental_catalyst_context(symbol)
        router = route_multi_horizon_opportunity(
            symbol,
            {**row, "recommendation_gate": gate},
            row,
            fundamentals,
            {},
            accuracy_context,
            financial_profile,
        )
        candidate["reasons"].append(f"Screen score is {score:.1f}/100.")
        candidate["reasons"].append(f"Data gate is {gate}.")
        if gate == "Blocked":
            candidate["action"] = "Avoid"
            candidate["risks"].append("Blocked data gate prevents buy recommendation.")
            continue
        if not can_add_risk:
            candidate["action"] = "Keep Cash"
            candidate["suitability_notes"].append("Personal suitability layer says de-risk or proceed cautiously.")
            continue
        if score >= 70 and gate in {"Trusted", "Warning"}:
            candidate["action"] = "Buy Candidate"
            candidate["suitability_notes"].append("Small starter allocation only after human review.")
            buy_candidates.append(_decorate_candidate(candidate, router, accuracy_context, "Buy Candidate"))
        elif score >= 60:
            candidate["action"] = "Add"
            candidate["suitability_notes"].append("Watch for a better entry or stronger confirmation.")
            buy_candidates.append(_decorate_candidate(candidate, router, accuracy_context, "Add"))

    cash = _safe_float(financial_profile.get("cash"))
    if suitability.get("status") == "De-risk first":
        cash_action = "Keep Cash"
        cash_reason = "Profile suggests emergency fund, cash flow, or debt should be handled before new buys."
    elif cash <= 0:
        cash_action = "No cash available"
        cash_reason = "No available cash was entered for new allocations."
    else:
        cash_action = "Selective deployment"
        cash_reason = "Use cash only for highest-ranked candidates that pass data and suitability gates."

    portfolio_summary = (
        f"Strategy reviewed {len(scan_results)} scanned symbols and {len(real_holdings)} real holding(s). "
        f"Suitability status: {suitability.get('status')}. "
        f"Human review required before any real-world action. No broker APIs or auto execution."
    )

    return {
        "buy_candidates": buy_candidates,
        "sell_candidates": sell_candidates,
        "hold_candidates": hold_candidates,
        "trim_candidates": trim_candidates,
        "cash_strategy": {
            "action": cash_action,
            "cash": round(cash, 2),
            "reason": cash_reason,
        },
        "risk_actions": risk_actions,
        "suitability": suitability,
        "benchmark_context": benchmark_truth.get("summary", "No benchmark truth summary available."),
        "decision_context": decision_intelligence.get("summary", "No decision intelligence summary available."),
        "accuracy_context": {
            "hit_rate": accuracy_context.get("hit_rate", 0.0),
            "average_return_pct": accuracy_context.get("average_return_pct", 0.0),
            "confidence_adjustment": accuracy_context.get("confidence_adjustment", 0.0),
            "summary": accuracy_context.get("summary", "No accuracy context available yet."),
        },
        "portfolio_summary": portfolio_summary,
        "human_review_required": True,
        "disclaimer": "Advisor-style research support only. Not financial advice; no live trading, broker APIs, auto execution, or guaranteed profit claims.",
    }
