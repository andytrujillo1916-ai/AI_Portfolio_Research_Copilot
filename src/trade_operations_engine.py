from datetime import datetime, timedelta

from paper_trader import add_paper_trade, load_paper_trades


FREE_RESEARCH_SOURCES = {"yfinance", "sec_edgar", "manual", "local_universe"}
FALLBACK_SOURCES = {"mock", "unknown", ""}
LIVE_DISABLED_REASON = "Live broker execution is disabled until supervised pilot gates pass."


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _today():
    return datetime.now().strftime("%Y-%m-%d")


def _next_review(strategy_type):
    hours = 4 if strategy_type == "Short Term" else 24 if strategy_type == "Futures Proxy" else 72
    return (datetime.now() + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M")


def _source_from_quality(data_quality):
    data_quality = data_quality or {}
    source = data_quality.get("source") or data_quality.get("data_source") or ""
    if not source and data_quality.get("provider"):
        source = data_quality.get("provider")
    return str(source or "unknown")


def assess_market_data_readiness(data_quality, quote_data=None):
    """Classify whether data can support research, paper, or live trading."""
    data_quality = data_quality or {}
    quote_data = quote_data or {}
    source = _source_from_quality(data_quality)
    gate = data_quality.get("recommendation_gate", "Warning")
    confidence = data_quality.get("data_confidence", "Unknown")
    issues = list(data_quality.get("issues", []))
    has_bid_ask = quote_data.get("bid") not in {None, ""} and quote_data.get("ask") not in {None, ""}
    is_realtime = bool(quote_data.get("is_realtime", False))

    research_allowed = gate != "Blocked"
    paper_allowed = gate != "Blocked" and confidence != "Low"
    live_allowed = False
    required_for_live = []

    if source in FALLBACK_SOURCES or gate == "Blocked":
        required_for_live.append("Replace mock/blocked data with fresh non-fallback market data.")
    if source in FREE_RESEARCH_SOURCES:
        required_for_live.append("Use broker or paid market data before live order routing.")
    if not has_bid_ask:
        required_for_live.append("Live readiness requires bid/ask quote availability.")
    if not is_realtime:
        required_for_live.append("Live readiness requires realtime or broker-approved quote freshness.")
    required_for_live.append(LIVE_DISABLED_REASON)

    if source in FALLBACK_SOURCES:
        data_tier = "Fallback"
    elif source in FREE_RESEARCH_SOURCES:
        data_tier = "Free research"
    else:
        data_tier = "Broker/Paid candidate"

    return {
        "source": source,
        "data_tier": data_tier,
        "data_confidence": confidence,
        "recommendation_gate": gate,
        "research_allowed": research_allowed,
        "paper_allowed": paper_allowed,
        "live_allowed": live_allowed,
        "has_bid_ask": has_bid_ask,
        "is_realtime": is_realtime,
        "issues": issues,
        "required_for_live": required_for_live,
        "summary": (
            f"{data_tier} data is allowed for "
            f"{'paper/research' if paper_allowed else 'research only' if research_allowed else 'display only'}; "
            "live trading is disabled."
        ),
    }


def _long_term_action(final_verdict, strategy_type, data_quality):
    if data_quality.get("recommendation_gate") == "Blocked":
        return "Needs Data"
    if strategy_type != "Long Term":
        return ""
    if final_verdict == "Buy Candidate":
        return "Buy Now"
    if final_verdict == "Add":
        return "Accumulate Slowly"
    if final_verdict == "Wait for Pullback":
        return "Wait for Pullback"
    if final_verdict in {"Watch", "Hold"}:
        return "Watch"
    return "Needs Data" if final_verdict == "Needs Data" else "Watch"


def build_trade_plan(
    symbol,
    snapshot,
    final_recommendation,
    entry_exit_data,
    position_size_data,
    risk,
    data_quality,
    market_timing=None,
    asset_class="Equity",
    strategy_type="Short Term",
    existing_position=None,
    benchmark_symbol="SPY",
):
    """Build the central audited trade plan object used before any order intent."""
    symbol = str(symbol or "").upper()
    snapshot = snapshot or {}
    final_recommendation = final_recommendation or {}
    entry_exit_data = entry_exit_data or {}
    position_size_data = position_size_data or {}
    risk = risk or {}
    data_quality = data_quality or {}
    market_timing = market_timing or {}
    existing_position = existing_position or {}

    price = _safe_float(snapshot.get("price"))
    stop_pct = _safe_float(entry_exit_data.get("stop_loss_guidance_pct"), 6.0)
    stop_loss = round(price * (1 - stop_pct / 100), 2) if price > 0 else 0.0
    take_profit = round(price * 1.12, 2) if strategy_type == "Short Term" and price > 0 else round(price * 1.25, 2) if price > 0 else 0.0
    final_verdict = final_recommendation.get("final_verdict", "Watch")
    data_gate = data_quality.get("recommendation_gate", "Warning")
    data_confidence = data_quality.get("data_confidence", "Unknown")
    market_risk = market_timing.get("market_risk_level", "")
    has_position = _safe_float(existing_position.get("shares", 0.0)) > 0

    sell_triggers = [
        "Thesis break: final verdict moves to Avoid, Sell Candidate, or Needs Data.",
        f"Stop hit: price closes below {stop_loss:.2f}.",
        "Time stop: max holding window expires without confirmation.",
        f"Target hit: price reaches {take_profit:.2f} and trim rules apply.",
        "Trailing stop: give back more than half of open paper profit after target is reached.",
        "Volatility spike: volatility exceeds the strategy limit in the entry/exit engine.",
        "Market-risk downgrade: market risk moves to High/Stress.",
        "Better alternative: benchmark or ranked opportunity materially improves versus this setup.",
    ]
    trim_rules = [
        "Trim 50% at first target or if conviction weakens while still profitable.",
        "Trim instead of add when exposure or diversification gates weaken.",
    ]
    invalidation = [
        "Data gate becomes Blocked.",
        "Signal score falls below neutral.",
        "Benchmark-relative alpha turns negative.",
        "News/fundamental catalyst contradicts the thesis.",
    ]

    if strategy_type == "Long Term":
        max_holding_window = "90 days before thesis review; multi-year only after repeated review."
        entry_trigger = "Staged buy only when data is usable and final verdict is Buy Candidate/Add/Wait for Pullback."
    else:
        max_holding_window = "10 trading days for short-term paper trade before mandatory review."
        entry_trigger = entry_exit_data.get("entry_zone", "No-Trade Zone")

    status = "Draft"
    if data_gate == "Blocked" or data_confidence == "Low":
        status = "Needs Data"
    elif market_risk == "High" and final_verdict in {"Buy Candidate", "Add"}:
        status = "Wait for Pullback"
    elif final_verdict in {"Buy Candidate", "Add"}:
        status = "Approved for Paper"
    elif final_verdict in {"Trim", "Sell Candidate"} and has_position:
        status = "Approved for Paper Exit"
    elif final_verdict in {"Watch", "Hold", "Wait for Pullback"}:
        status = "Watch"

    return {
        "symbol": symbol,
        "asset_class": asset_class,
        "strategy_type": strategy_type,
        "entry_trigger": entry_trigger,
        "entry_plan": entry_exit_data.get("summary", "Entry requires final verdict, data, sizing, and safety gates."),
        "exit_plan": "Exit or trim only when a named sell trigger fires.",
        "sell_triggers": sell_triggers,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "trim_rules": trim_rules,
        "time_stop": max_holding_window,
        "max_holding_window": max_holding_window,
        "next_review_time": _next_review(strategy_type),
        "max_position_size": position_size_data.get("recommended_position_pct", 0.0),
        "risk_budget": position_size_data.get("risk_budget", "No new risk until reviewed."),
        "confidence": final_recommendation.get("confidence", "Low"),
        "data_confidence": data_confidence,
        "market_regime": final_recommendation.get("market_regime", ""),
        "market_risk_level": market_risk,
        "final_verdict": final_verdict,
        "long_term_action": _long_term_action(final_verdict, strategy_type, data_quality),
        "invalidation_triggers": invalidation,
        "status": status,
        "benchmark_symbol": benchmark_symbol,
        "human_review_required": True,
        "live_trading_enabled": False,
        "summary": f"{symbol} trade plan is {status}. Live trading remains disabled.",
    }


def build_order_intent(trade_plan, snapshot=None, existing_position=None, live_requested=False):
    """Build an order intent. This never routes live broker orders."""
    trade_plan = trade_plan or {}
    snapshot = snapshot or {}
    existing_position = existing_position or {}
    price = _safe_float(snapshot.get("price"))
    shares = _safe_float(existing_position.get("shares", 0.0))
    max_position_pct = _safe_float(trade_plan.get("max_position_size"), 0.0)

    intent_type = "none"
    quantity = 0.0
    if trade_plan.get("status") == "Approved for Paper" and price > 0 and max_position_pct > 0:
        intent_type = "paper_buy"
        paper_value = max(1000.0 * (max_position_pct / 100), 0.0)
        quantity = round(paper_value / price, 4)
    elif trade_plan.get("status") == "Approved for Paper Exit" and shares > 0:
        intent_type = "paper_trim" if trade_plan.get("final_verdict") == "Trim" else "paper_sell"
        quantity = round(shares * (0.5 if intent_type == "paper_trim" else 1.0), 4)
    elif live_requested:
        intent_type = "live_candidate"

    live_blockers = []
    if intent_type == "live_candidate":
        live_blockers.extend(
            [
                LIVE_DISABLED_REASON,
                "Only stocks/ETFs can enter a future supervised live pilot.",
                "Live candidate requires broker/paid realtime quote data and explicit user approval.",
            ]
        )

    return {
        "intent_type": intent_type,
        "source_trade_plan_id": trade_plan.get("id", ""),
        "symbol": trade_plan.get("symbol", ""),
        "risk_budget": trade_plan.get("risk_budget", "No real-world risk."),
        "quantity": quantity,
        "limit_price": price,
        "expiry": trade_plan.get("next_review_time", ""),
        "kill_switch_checked": False,
        "live_blockers": live_blockers,
        "paper_only": intent_type in {"paper_buy", "paper_sell", "paper_trim"},
        "summary": f"Created {intent_type} order intent. No live broker routing is available.",
    }


def evaluate_autopilot_safety(order_intent, paper_performance=None, paper_positions=None, controls=None, existing_trades=None):
    """Apply paper-autopilot limits before saving a simulated paper order."""
    order_intent = order_intent or {}
    paper_performance = paper_performance or {}
    paper_positions = paper_positions or {}
    controls = controls or {}
    existing_trades = existing_trades if existing_trades is not None else load_paper_trades()

    max_daily_loss = _safe_float(controls.get("max_daily_loss_pct"), 2.0)
    max_weekly_loss = _safe_float(controls.get("max_weekly_loss_pct"), 5.0)
    max_trades_per_day = int(_safe_float(controls.get("max_trades_per_day"), 3))
    max_exposure_pct = _safe_float(controls.get("max_total_exposure_pct"), 25.0)
    kill_switch = bool(controls.get("kill_switch", False))

    today = _today()
    today_trades = [row for row in existing_trades if str(row.get("date", "")).startswith(today)]
    duplicate = any(
        row.get("symbol") == order_intent.get("symbol")
        and str(row.get("action", "")).lower() in {"buy", "sell"}
        for row in today_trades
    )
    pnl_pct = _safe_float(paper_performance.get("total_unrealized_pnl_pct"), 0.0)
    exposure_value = _safe_float(paper_positions.get("market_value"), 0.0)
    exposure_pct = _safe_float(controls.get("current_exposure_pct"), 0.0)
    if exposure_pct <= 0 and exposure_value > 0:
        exposure_pct = min(100.0, exposure_value / max(_safe_float(controls.get("portfolio_value"), 100000.0), 1.0) * 100)

    passed = []
    failed = []
    if kill_switch:
        failed.append("Emergency kill switch is active.")
    else:
        passed.append("Emergency kill switch is off.")
    if pnl_pct <= -max_daily_loss:
        failed.append(f"Daily loss limit breached at {pnl_pct:.2f}%.")
    else:
        passed.append("Daily loss limit not breached.")
    if pnl_pct <= -max_weekly_loss:
        failed.append(f"Weekly loss limit breached at {pnl_pct:.2f}%.")
    else:
        passed.append("Weekly loss limit not breached.")
    if len(today_trades) >= max_trades_per_day:
        failed.append("Max trades per day reached.")
    else:
        passed.append("Trade count is inside daily limit.")
    if exposure_pct > max_exposure_pct and order_intent.get("intent_type") == "paper_buy":
        failed.append("Max total exposure would be breached.")
    else:
        passed.append("Exposure gate passed.")
    if duplicate:
        failed.append("Duplicate same-day paper trade is blocked.")
    else:
        passed.append("No duplicate same-day trade detected.")
    if order_intent.get("intent_type") not in {"paper_buy", "paper_sell", "paper_trim"}:
        failed.append("Only paper order intents can be executed by autopilot.")

    return {
        "allowed": not failed,
        "passed": passed,
        "failed": failed,
        "kill_switch_checked": True,
        "summary": "Paper autopilot allowed." if not failed else "Paper autopilot blocked by safety gates.",
    }


def execute_paper_order_intent(order_intent, safety_result):
    """Save a paper trade only after safety gates pass."""
    order_intent = order_intent or {}
    safety_result = safety_result or {}
    if not safety_result.get("allowed"):
        return {"saved": False, "message": safety_result.get("summary", "Safety gates blocked order intent.")}
    intent_type = order_intent.get("intent_type")
    if intent_type not in {"paper_buy", "paper_sell", "paper_trim"}:
        return {"saved": False, "message": "Only paper order intents can be saved."}
    action = "buy" if intent_type == "paper_buy" else "sell"
    trade = add_paper_trade(
        symbol=order_intent.get("symbol"),
        action=action,
        quantity=order_intent.get("quantity", 0.0),
        price=order_intent.get("limit_price", 0.0),
        reason=f"TRADE OPS PAPER AUTOPILOT: {order_intent.get('summary', '')}",
    )
    return {"saved": True, "message": "Paper order intent saved.", "trade": trade}
