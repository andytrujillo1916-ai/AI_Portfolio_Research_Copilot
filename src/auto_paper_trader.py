from datetime import datetime

from paper_trader import add_paper_trade, load_paper_trades


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _today():
    return datetime.now().strftime("%Y-%m-%d")


def _has_same_day_trade(symbol, action):
    today = _today()
    for trade in load_paper_trades():
        if (
            trade.get("symbol") == symbol
            and str(trade.get("action", "")).lower() == action.lower()
            and str(trade.get("date", "")).startswith(today)
        ):
            return True
    return False


def build_auto_paper_trade_ticket(
    symbol,
    snapshot,
    meta_decision,
    execution_data,
    position_size_data,
    entry_exit_data,
    exposure_limits_data,
    correlation_data,
    benchmark_data,
    data_confidence="Medium",
    existing_position=None,
    research_mode="Balanced",
):
    """Build a simulated trade ticket from the full research gate stack."""
    snapshot = snapshot or {}
    meta_decision = meta_decision or {}
    execution_data = execution_data or {}
    position_size_data = position_size_data or {}
    entry_exit_data = entry_exit_data or {}
    exposure_limits_data = exposure_limits_data or {}
    correlation_data = correlation_data or {}
    benchmark_data = benchmark_data or {}
    existing_position = existing_position or {}

    price = _safe_float(snapshot.get("price", 0.0))
    position_pct = _safe_float(position_size_data.get("recommended_position_pct", 0.0))
    position_value = _safe_float(position_size_data.get("recommended_position_value", 0.0))
    existing_shares = _safe_float(existing_position.get("shares", 0.0))
    final_verdict = meta_decision.get("final_verdict", "Watch")
    readiness = execution_data.get("readiness_level", "Not Ready")
    exposure_status = exposure_limits_data.get("exposure_status", "Moderate")
    diversification = _safe_float(correlation_data.get("diversification_score", 50.0))
    entry_action = entry_exit_data.get("recommended_action", "Watch")

    passed = []
    failed = []

    if data_confidence != "Low":
        passed.append("Data confidence is acceptable.")
    else:
        failed.append("Data confidence is Low.")

    if final_verdict in {"Research Candidate", "Strong Research Candidate"}:
        passed.append(f"Meta verdict is {final_verdict}.")
    else:
        failed.append(f"Meta verdict is {final_verdict}.")

    if readiness in {"Near Ready", "Ready for Paper Trade"}:
        passed.append(f"Execution readiness is {readiness}.")
    else:
        failed.append(f"Execution readiness is {readiness}.")

    if position_pct > 0 and position_value > 0:
        passed.append(f"Position sizing allows {position_pct:.2f}%.")
    else:
        failed.append("Position sizing recommends no new exposure.")

    if exposure_status != "High Risk":
        passed.append(f"Exposure status is {exposure_status}.")
    else:
        failed.append("Exposure status is High Risk.")

    if diversification >= 40:
        passed.append(f"Diversification score is {diversification:.0f}/100.")
    else:
        failed.append("Diversification score is severely weak.")

    action = "Skip"
    quantity = 0.0
    reason = "Full gate stack did not pass."

    if entry_action in {"Trim", "Exit"} and existing_shares > 0:
        action = "Trim" if entry_action == "Trim" else "Exit"
        quantity = round(existing_shares * (0.5 if action == "Trim" else 1.0), 4)
        reason = f"{entry_action} triggered by entry/exit framework."
    elif not failed and price > 0:
        action = "Enter Paper Trade"
        quantity = round(position_value / price, 4)
        reason = "All entry gates passed for a simulated long-only paper trade."
    elif existing_shares > 0:
        action = "Hold"
        reason = "Existing paper position remains open; no new simulated trade saved."

    best_benchmark = (benchmark_data.get("best_benchmark") or {}).get("symbol", "N/A")
    return {
        "symbol": symbol,
        "action": action,
        "paper_trade_action": "buy" if action == "Enter Paper Trade" else "sell" if action in {"Trim", "Exit"} else "none",
        "price": price,
        "quantity": quantity,
        "suggested_paper_allocation_pct": round(position_pct, 2),
        "reason": reason,
        "risk_controls_passed": passed,
        "risk_controls_failed": failed,
        "benchmark_context": f"Compared against best ETF benchmark: {best_benchmark}.",
        "data_confidence": data_confidence,
        "research_mode": research_mode,
        "disclaimer": "Simulated paper trade only. No broker APIs, live trading, leverage, shorts, or real execution.",
    }


def save_auto_paper_trade(ticket):
    """Save a simulated trade ticket if it is actionable and not duplicated today."""
    ticket = ticket or {}
    action = ticket.get("paper_trade_action", "none")
    symbol = ticket.get("symbol", "")

    if action not in {"buy", "sell"}:
        return {"saved": False, "message": "No simulated trade was saved because action is not actionable."}
    if _has_same_day_trade(symbol, action):
        return {"saved": False, "message": "Duplicate same-day simulated trade blocked."}
    if _safe_float(ticket.get("quantity", 0.0)) <= 0 or _safe_float(ticket.get("price", 0.0)) <= 0:
        return {"saved": False, "message": "Invalid price or quantity; simulated trade not saved."}

    trade = add_paper_trade(
        symbol=symbol,
        action=action,
        quantity=ticket.get("quantity", 0.0),
        price=ticket.get("price", 0.0),
        reason=f"AUTO PAPER: {ticket.get('reason', '')}",
    )
    return {"saved": True, "message": "Simulated auto paper trade saved.", "trade": trade}
