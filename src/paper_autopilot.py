"""Daily simulated paper-trade autopilot helpers.

Everything here is paper-only. No broker APIs, no live orders, no margin, no
futures contracts, and no guaranteed outcomes.
"""

from datetime import datetime

from agent_research_desk import run_agent_research_desk
from market_data import get_market_snapshot, get_price_history, get_risk_metrics
from paper_trader import add_paper_trade, load_paper_trades


DISCLAIMER = (
    "Simulated paper trade only. No broker APIs, live trading, order placement, "
    "margin, leverage, futures contracts, or guaranteed profit."
)


def _today():
    return datetime.now().strftime("%Y-%m-%d")


def _timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _safe_float(value, default=0.0):
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _candidate_score(row):
    return _safe_float(
        row.get("lane_score", row.get("score", row.get("opportunity_score", row.get("growth_score", 0.0))))
    )


def _same_day_buy_exists(symbol, trades=None, today=None):
    today = today or _today()
    symbol = str(symbol or "").upper()
    for trade in trades if trades is not None else load_paper_trades():
        if (
            str(trade.get("symbol", "")).upper() == symbol
            and str(trade.get("action", "")).lower() == "buy"
            and str(trade.get("date", "")).startswith(today)
        ):
            return True
    return False


def _same_day_autopilot_trades(trades, today):
    rows = []
    for trade in trades or []:
        if (
            str(trade.get("date", "")).startswith(today)
            and str(trade.get("action", "")).lower() == "buy"
            and "PAPER AUTOPILOT" in str(trade.get("reason", "")).upper()
        ):
            rows.append(trade)
    return rows


def _existing_autopilot_allocation_pct(trades, portfolio_value, today):
    if portfolio_value <= 0:
        return 0.0
    value = 0.0
    for trade in _same_day_autopilot_trades(trades, today):
        value += _safe_float(trade.get("quantity")) * _safe_float(trade.get("price"))
    return round((value / portfolio_value) * 100, 2)


def _base_allocation_pct(score):
    if score >= 85:
        return 5.0
    if score >= 75:
        return 3.0
    if score >= 70:
        return 2.0
    return 0.0


def _risk_adjusted_allocation(score, risk):
    allocation = _base_allocation_pct(score)
    volatility = _safe_float((risk or {}).get("volatility_pct"))
    drawdown = _safe_float((risk or {}).get("max_drawdown_pct"))
    if volatility > 30 or drawdown < -15:
        allocation *= 0.5
    return round(allocation, 2)


def _candidate_precheck(row):
    symbol = str((row or {}).get("symbol", "")).upper().strip()
    if not symbol:
        return "Missing symbol."
    if row.get("recommendation_gate") == "Blocked":
        return "Data gate is Blocked."
    if row.get("data_confidence") == "Low":
        return "Data confidence is Low."
    return ""


def build_autopilot_paper_ticket(agent_result, snapshot, risk, paper_context):
    """Convert an agent result into a simulated paper buy ticket."""
    agent_result = agent_result or {}
    snapshot = snapshot or {}
    risk = risk or {}
    paper_context = paper_context or {}

    symbol = str(agent_result.get("symbol", "")).upper().strip()
    score = _safe_float(agent_result.get("score"))
    final_verdict = agent_result.get("final_verdict", "Watch")
    lane = agent_result.get("lane", "Needs Data")
    data_quality = agent_result.get("data_quality", {}) or {}
    data_gate = data_quality.get("recommendation_gate", "Warning")
    data_confidence = data_quality.get("data_confidence", "Unknown")
    price = _safe_float(snapshot.get("price", agent_result.get("price")))
    portfolio_value = _safe_float(paper_context.get("portfolio_value"), 100000.0)
    used_daily_allocation_pct = _safe_float(paper_context.get("used_daily_allocation_pct"), 0.0)
    max_daily_allocation_pct = _safe_float(paper_context.get("max_daily_allocation_pct"), 10.0)
    existing_trades = paper_context.get("existing_trades")
    today = paper_context.get("today") or _today()

    requested_allocation_pct = _risk_adjusted_allocation(score, risk)
    remaining_daily_pct = max(0.0, max_daily_allocation_pct - used_daily_allocation_pct)
    allocation_pct = round(min(requested_allocation_pct, remaining_daily_pct), 2)
    position_value = round(portfolio_value * allocation_pct / 100, 2)
    quantity = round(position_value / price, 4) if price > 0 else 0.0

    passed = []
    failed = []
    if final_verdict in {"Buy Candidate", "Add"}:
        passed.append(f"Agent verdict is {final_verdict}.")
    else:
        failed.append(f"Agent verdict is {final_verdict}; only Buy Candidate/Add can auto-buy.")
    if data_gate != "Blocked":
        passed.append(f"Data gate is {data_gate}.")
    else:
        failed.append("Data gate is Blocked.")
    if data_confidence != "Low":
        passed.append(f"Data confidence is {data_confidence}.")
    else:
        failed.append("Data confidence is Low.")
    if score >= 70:
        passed.append(f"Agent score is {score:.1f}.")
    else:
        failed.append(f"Agent score {score:.1f} is below 70.")
    if lane != "Needs Data":
        passed.append(f"Lane is {lane}.")
    else:
        failed.append("Lane is Needs Data.")
    if not _same_day_buy_exists(symbol, trades=existing_trades, today=today):
        passed.append("No same-day paper buy exists for this symbol.")
    else:
        failed.append("Duplicate same-day paper buy exists.")
    if price > 0:
        passed.append(f"Price is valid at {price:.2f}.")
    else:
        failed.append("Price is missing or invalid.")
    if allocation_pct > 0 and quantity > 0:
        passed.append(f"Dynamic paper allocation is {allocation_pct:.2f}%.")
    else:
        failed.append("Daily exposure cap or risk gates leave no allocation.")

    return {
        "symbol": symbol,
        "timestamp": _timestamp(),
        "action": "buy",
        "paper_trade_action": "buy" if not failed else "none",
        "final_verdict": final_verdict,
        "lane": lane,
        "score": round(score, 2),
        "price": price,
        "quantity": quantity,
        "allocation_pct": allocation_pct,
        "position_value": position_value,
        "requested_allocation_pct": requested_allocation_pct,
        "data_gate": data_gate,
        "data_confidence": data_confidence,
        "risk_controls_passed": passed,
        "risk_controls_failed": failed,
        "paper_trade_eligible": not failed,
        "benchmark_context": "Compare this paper idea against ETF baselines before trusting it.",
        "reason": f"Daily paper autopilot from agent verdict {final_verdict} in {lane} lane.",
        "disclaimer": DISCLAIMER,
    }


def save_autopilot_paper_trade(ticket, save_trade_fn=None):
    """Save a simulated paper trade if the ticket passed all autopilot gates."""
    ticket = ticket or {}
    if not ticket.get("paper_trade_eligible"):
        return {"saved": False, "message": "Autopilot gates blocked the simulated paper trade.", "ticket": ticket}
    if ticket.get("paper_trade_action") != "buy":
        return {"saved": False, "message": "Only simulated paper buys are auto-saved.", "ticket": ticket}
    if _safe_float(ticket.get("quantity")) <= 0 or _safe_float(ticket.get("price")) <= 0:
        return {"saved": False, "message": "Invalid price or quantity.", "ticket": ticket}

    saver = save_trade_fn or add_paper_trade
    trade = saver(
        symbol=ticket.get("symbol"),
        action="buy",
        quantity=ticket.get("quantity"),
        price=ticket.get("price"),
        reason=f"PAPER AUTOPILOT: {ticket.get('reason', '')}",
    )
    return {"saved": True, "message": "Autopilot simulated paper buy saved.", "trade": trade, "ticket": ticket}


def _bullet_list(items):
    if not items:
        return "- None noted."
    return "\n".join(f"- {item}" for item in items)


def build_paper_trade_checklist_markdown(ticket, agent_result):
    """Build a Markdown checklist for a simulated paper trade."""
    ticket = ticket or {}
    agent_result = agent_result or {}
    lines = [
        f"# Paper Trade Checklist: {ticket.get('symbol', agent_result.get('symbol', 'N/A'))}",
        "",
        "## Summary",
        f"- Timestamp: {ticket.get('timestamp') or _timestamp()}",
        f"- Action: simulated paper {ticket.get('action', 'N/A')}",
        f"- Agent verdict: {ticket.get('final_verdict', agent_result.get('final_verdict', 'N/A'))}",
        f"- Lane: {ticket.get('lane', agent_result.get('lane', 'N/A'))}",
        f"- Score: {ticket.get('score', agent_result.get('score', 'N/A'))}",
        f"- Data gate: {ticket.get('data_gate', (agent_result.get('data_quality') or {}).get('recommendation_gate', 'N/A'))}",
        f"- Data confidence: {ticket.get('data_confidence', (agent_result.get('data_quality') or {}).get('data_confidence', 'N/A'))}",
        "",
        "## Paper Order",
        f"- Price: {ticket.get('price', 'N/A')}",
        f"- Quantity: {ticket.get('quantity', 'N/A')}",
        f"- Allocation %: {ticket.get('allocation_pct', 'N/A')}",
        f"- Position value: {ticket.get('position_value', 'N/A')}",
        "",
        "## Bull Case",
        _bullet_list(agent_result.get("bull_case", [])),
        "",
        "## Bear Case",
        _bullet_list(agent_result.get("bear_case", [])),
        "",
        "## Invalidation Triggers",
        _bullet_list(agent_result.get("invalidation_triggers", [])),
        "",
        "## Safety Gates Passed",
        _bullet_list(ticket.get("risk_controls_passed", [])),
        "",
        "## Safety Gates Failed",
        _bullet_list(ticket.get("risk_controls_failed", [])),
        "",
        "## Benchmark Note",
        ticket.get("benchmark_context", "Compare this against ETF baselines."),
        "",
        "## Research-Only Disclaimer",
        ticket.get("disclaimer", DISCLAIMER),
        "",
    ]
    return "\n".join(lines)


def run_daily_paper_autopilot(
    candidates,
    profile,
    period,
    paper_context,
    max_trades=3,
    agent_runner=None,
    save_trade_fn=None,
    today=None,
):
    """Run daily agent research and save up to max_trades simulated paper buys."""
    today = today or _today()
    paper_context = dict(paper_context or {})
    paper_context["today"] = today
    paper_context.setdefault("portfolio_value", 100000.0)
    paper_context.setdefault("max_daily_allocation_pct", 10.0)
    paper_context.setdefault("existing_trades", load_paper_trades())
    existing_autopilot_trades = _same_day_autopilot_trades(paper_context["existing_trades"], today)
    existing_allocation_pct = _existing_autopilot_allocation_pct(
        paper_context["existing_trades"],
        _safe_float(paper_context.get("portfolio_value"), 100000.0),
        today,
    )
    paper_context["used_daily_allocation_pct"] = max(
        _safe_float(paper_context.get("used_daily_allocation_pct"), 0.0),
        existing_allocation_pct,
    )
    runner = agent_runner or run_agent_research_desk
    remaining_trade_slots = max(0, int(max_trades) - len(existing_autopilot_trades))

    ranked = sorted(candidates or [], key=_candidate_score, reverse=True)
    evaluated = []
    saved_trades = []
    skipped = []
    checklists = []

    for row in ranked:
        if len(saved_trades) >= remaining_trade_slots:
            break
        symbol = str((row or {}).get("symbol", "")).upper().strip()
        precheck = _candidate_precheck(row)
        if precheck:
            skipped.append({"symbol": symbol, "reason": precheck})
            continue

        agent_result = runner(symbol, run_type="Daily Autopilot", profile=profile or {}, save_memory=True)
        evaluated.append(agent_result)

        try:
            snapshot = get_market_snapshot(symbol)
            price_data = get_price_history(symbol, period=period)
            chart_input = price_data.get("data") if isinstance(price_data, dict) else price_data
            risk = get_risk_metrics(chart_input)
        except Exception as exc:
            skipped.append({"symbol": symbol, "reason": f"Could not load sizing data: {exc}"})
            continue

        ticket = build_autopilot_paper_ticket(agent_result, snapshot, risk, paper_context)
        checklist = build_paper_trade_checklist_markdown(ticket, agent_result)
        checklists.append({"symbol": symbol, "markdown": checklist, "ticket": ticket})

        result = save_autopilot_paper_trade(ticket, save_trade_fn=save_trade_fn)
        if result.get("saved"):
            saved_trades.append(result)
            paper_context["used_daily_allocation_pct"] += _safe_float(ticket.get("allocation_pct"))
            paper_context["existing_trades"].append(
                {
                    "symbol": symbol,
                    "action": "buy",
                    "date": today,
                    "quantity": ticket.get("quantity"),
                    "price": ticket.get("price"),
                }
            )
        else:
            skipped.append({"symbol": symbol, "reason": result.get("message", "Autopilot skipped."), "ticket": ticket})

    return {
        "date": today,
        "evaluated_candidates": evaluated,
        "saved_trades": saved_trades,
        "skipped_candidates": skipped,
        "checklists": checklists,
        "summary": f"Autopilot evaluated {len(evaluated)} candidate(s) and saved {len(saved_trades)} simulated paper buy/buys.",
        "disclaimer": DISCLAIMER,
    }
