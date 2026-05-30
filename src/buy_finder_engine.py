"""Buy finder and portfolio action planning.

This layer separates "not enough trusted data" from "bad opportunity" so the
app can keep looking for buy candidates without treating every data issue as an
Avoid verdict.
"""


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _profile_can_add_risk(profile):
    profile = profile or {}
    income = _safe_float(profile.get("monthly_income"))
    expenses = _safe_float(profile.get("monthly_expenses"))
    emergency = _safe_float(profile.get("emergency_fund"))
    if expenses > 0 and emergency / expenses < 3:
        return False, "Emergency fund is below 3 months."
    if income > 0 and income - expenses <= 0:
        return False, "Monthly surplus is not positive."
    return True, "Profile allows selective risk review."


def _holding_exposure(symbol, holdings, profile):
    total = _safe_float((profile or {}).get("cash"))
    value = 0.0
    for row in holdings or []:
        current = _safe_float(row.get("current_value"))
        total += current
        if str(row.get("symbol", "")).upper() == symbol:
            value += current
    return (value / total * 100) if total > 0 else 0.0


def _is_interesting(row):
    score = _safe_float(row.get("score"))
    growth = _safe_float(row.get("growth_score"))
    ret = _safe_float(row.get("return_pct"))
    theme = bool(row.get("theme"))
    return score >= 55 or growth >= 55 or ret >= 3 or theme


def _negative_evidence(row, accuracy_context):
    score = _safe_float(row.get("score"))
    growth = _safe_float(row.get("growth_score"))
    ret = _safe_float(row.get("return_pct"))
    volatility = _safe_float(row.get("volatility_pct"))
    drawdown = _safe_float(row.get("max_drawdown_pct"))
    accuracy_adjustment = _safe_float((accuracy_context or {}).get("confidence_adjustment"))
    negatives = []
    if score < 40:
        negatives.append("Signal score is weak.")
    if growth < 35:
        negatives.append("Growth discovery score is weak.")
    if ret <= -10:
        negatives.append("Recent trend is materially negative.")
    if volatility >= 45 and ret <= 0:
        negatives.append("High volatility is not being offset by positive trend.")
    if drawdown <= -25:
        negatives.append("Drawdown is deep enough to question timing or thesis.")
    if accuracy_adjustment <= -10:
        negatives.append("Historical accuracy context is weak for similar recommendations.")
    return negatives


def build_buy_finder(scan_rows, final_verdicts, market_timing, profile, holdings, accuracy_context):
    """Rank buy/add/watch/data-research candidates from scan rows."""
    scan_rows = scan_rows or []
    if isinstance(final_verdicts, list):
        final_verdicts = {str(row.get("symbol", "")).upper(): row for row in final_verdicts}
    final_verdicts = final_verdicts or {}
    market_timing = market_timing or {}
    profile = profile or {}
    holdings = holdings or []
    accuracy_context = accuracy_context or {}
    can_add, suitability_note = _profile_can_add_risk(profile)
    max_single = _safe_float(profile.get("max_single_stock_exposure"), 15.0)
    market_risk = market_timing.get("market_risk_level", "Moderate")

    rows = []
    for index, row in enumerate(scan_rows, start=1):
        symbol = str(row.get("symbol", "")).upper()
        if not symbol:
            continue
        gate = row.get("recommendation_gate", "Warning")
        confidence = row.get("data_confidence", "Unknown")
        score = _safe_float(row.get("score"))
        growth = _safe_float(row.get("growth_score"), score)
        volatility = _safe_float(row.get("volatility_pct"))
        exposure = _holding_exposure(symbol, holdings, profile)
        negatives = _negative_evidence(row, accuracy_context)
        final = final_verdicts.get(symbol, {})
        reasons = [
            f"Signal score {score:.1f}/100.",
            f"Growth discovery score {growth:.1f}/100.",
            f"Data gate is {gate}.",
        ]
        unlock = []

        if exposure > max_single:
            action = "Trim"
            reasons.append(f"Current exposure {exposure:.1f}% exceeds max single-stock exposure.")
        elif gate == "Blocked" or confidence == "Low":
            if negatives and not _is_interesting(row):
                action = "Avoid"
                reasons.extend(negatives[:2])
            else:
                action = "Needs Data"
                unlock.append("Data Quality Agent: refresh non-mock price/history and source confidence.")
                if _is_interesting(row):
                    unlock.append("Growth Discovery Agent: verify thesis before any buy label.")
        elif not can_add:
            action = "Agent Research" if _is_interesting(row) else "Hold"
            unlock.append(f"AIOS Assistant Agent: resolve suitability blocker: {suitability_note}")
        elif market_risk == "High" and (score >= 60 or growth >= 60):
            action = "Wait for Pullback"
            reasons.append("Market timing risk is High, so a good setup needs a better entry.")
        elif negatives and score < 45:
            action = "Avoid"
            reasons.extend(negatives[:2])
        elif score >= 72 and growth >= 68 and volatility < 35:
            action = "Buy Candidate"
            reasons.append("Balanced-growth evidence is strong enough for buy review.")
        elif score >= 62 or growth >= 64:
            action = "Add"
            reasons.append("Evidence is constructive but not at highest conviction.")
        elif _is_interesting(row):
            action = "Agent Research"
            unlock.append("Research agents should verify the thesis, catalyst, and risk before a buy label.")
        else:
            action = "Hold"

        if final.get("final_verdict") in {"Buy Candidate", "Add", "Wait for Pullback", "Needs Data", "Agent Research"}:
            action = final.get("final_verdict")
            reasons.append("Existing Final Verdict is used as source-of-truth evidence.")

        rank_score = score * 0.45 + growth * 0.45 + max(0, _safe_float(row.get("return_pct"))) * 0.5
        if action == "Buy Candidate":
            rank_score += 20
        elif action == "Add":
            rank_score += 12
        elif action == "Wait for Pullback":
            rank_score += 6
        elif action in {"Needs Data", "Agent Research"}:
            rank_score += 3 if _is_interesting(row) else -5
        elif action == "Avoid":
            rank_score -= 25

        rows.append(
            {
                "symbol": symbol,
                "company": row.get("company", ""),
                "theme": row.get("theme", ""),
                "action": action,
                "buy_finder_rank_score": round(rank_score, 1),
                "score": round(score, 1),
                "growth_score": round(growth, 1),
                "return_pct": round(_safe_float(row.get("return_pct")), 2),
                "volatility_pct": round(volatility, 2),
                "data_confidence": confidence,
                "recommendation_gate": gate,
                "market_risk": market_risk,
                "current_exposure_pct": round(exposure, 2),
                "paper_trade_eligible": action in {"Buy Candidate", "Add"} and gate != "Blocked" and confidence != "Low" and can_add,
                "reasons": reasons,
                "negative_evidence": negatives,
                "agent_unlocks": unlock,
                "source_row_index": index,
            }
        )

    rows.sort(key=lambda item: item.get("buy_finder_rank_score", 0), reverse=True)
    for idx, row in enumerate(rows, start=1):
        row["buy_finder_rank"] = idx

    grouped = {
        "best_buy_candidates": [row for row in rows if row["action"] == "Buy Candidate"],
        "add_candidates": [row for row in rows if row["action"] == "Add"],
        "wait_for_pullback": [row for row in rows if row["action"] == "Wait for Pullback"],
        "needs_data": [row for row in rows if row["action"] in {"Needs Data", "Agent Research"}],
        "avoid_with_evidence": [row for row in rows if row["action"] == "Avoid"],
        "all_rows": rows,
        "summary": (
            f"Buy Finder reviewed {len(rows)} symbols and found "
            f"{sum(1 for row in rows if row['action'] in {'Buy Candidate', 'Add'})} buy/add candidate(s)."
        ),
    }
    return grouped


def build_portfolio_action_plan(final_verdicts, holdings, profile, market_timing):
    """Convert final/buy-finder verdicts into a ranked non-executing portfolio plan."""
    final_verdicts = final_verdicts or []
    holdings = holdings or []
    profile = profile or {}
    market_timing = market_timing or {}
    max_single = _safe_float(profile.get("max_single_stock_exposure"), 15.0)
    market_risk = market_timing.get("market_risk_level", "Moderate")
    holdings_by_symbol = {str(row.get("symbol", "")).upper(): row for row in holdings}
    actions = []

    for row in final_verdicts:
        symbol = str(row.get("symbol", "")).upper()
        action = row.get("final_verdict") or row.get("action", "Watch")
        exposure = _holding_exposure(symbol, holdings, profile)
        if exposure > max_single:
            action = "Trim"
        if market_risk == "High" and action in {"Buy Candidate", "Add"}:
            action = "Wait for Pullback"
        allocation = "Watchlist only"
        if action == "Buy Candidate":
            allocation = "2-4% starter band"
        elif action == "Add":
            allocation = "1-3% add band"
        elif action == "Trim":
            allocation = f"Reduce toward {max_single:.1f}% max"
        elif action == "Wait for Pullback":
            allocation = "Prepare order idea, wait for risk/entry confirmation"
        elif action == "Needs Data":
            allocation = "0% until data quality improves"

        actions.append(
            {
                "symbol": symbol,
                "portfolio_action": action,
                "target_allocation_band": allocation,
                "current_exposure_pct": round(exposure, 2),
                "priority": row.get("buy_finder_rank", row.get("priority_rank", 999)),
                "paper_trade_eligible": bool(row.get("paper_trade_eligible", False)),
                "reason": " | ".join(row.get("reasons", row.get("why", []))[:2]),
                "has_holding": symbol in holdings_by_symbol,
            }
        )

    actions.sort(key=lambda item: (item["portfolio_action"] not in {"Trim", "Buy Candidate", "Add"}, item["priority"]))
    return {
        "actions": actions,
        "summary": f"Portfolio action plan created {len(actions)} non-executing action row(s).",
        "market_risk": market_risk,
    }
