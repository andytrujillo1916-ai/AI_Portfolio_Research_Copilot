from datetime import date, datetime, time, timedelta, timezone


try:
    from zoneinfo import ZoneInfo

    MARKET_TZ = ZoneInfo("America/New_York")
except Exception:
    MARKET_TZ = timezone(timedelta(hours=-4))


MARKET_OPEN = time(9, 30)
STABILIZATION_START = time(9, 45)
STABILIZATION_END = time(10, 30)
MIDDAY_START = time(11, 30)
MIDDAY_END = time(14, 0)
POWER_HOUR_START = time(15, 0)
CLOSING_AUCTION_START = time(15, 45)
MARKET_CLOSE = time(16, 0)


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, value))


def _as_market_datetime(now=None):
    if now is None:
        return datetime.now(MARKET_TZ)
    if isinstance(now, date) and not isinstance(now, datetime):
        return datetime.combine(now, time(12, 0), tzinfo=MARKET_TZ)
    if now.tzinfo is None:
        return now.replace(tzinfo=MARKET_TZ)
    return now.astimezone(MARKET_TZ)


def _parse_timestamp(value):
    if not value:
        return None
    try:
        if hasattr(value, "to_pydatetime"):
            value = value.to_pydatetime()
        if isinstance(value, datetime):
            parsed = value
        else:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=MARKET_TZ)
        return parsed.astimezone(MARKET_TZ)
    except Exception:
        return None


def make_reason(category, direction, strength, reason, source, freshness="", what_would_change_this=""):
    return {
        "category": category,
        "direction": direction,
        "strength": strength,
        "reason": reason,
        "source": source,
        "freshness": freshness,
        "what_would_change_this": what_would_change_this,
    }


def _month_trading_days(year, month):
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    day = date(year, month, 1)
    days = []
    while day < next_month:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


def classify_intraday_window(now=None):
    market_now = _as_market_datetime(now)
    current_time = market_now.time()
    weekday = market_now.weekday()

    if weekday >= 5:
        return {
            "window": "Market Closed",
            "timing_bias": "No Timing Edge",
            "description": "Regular equity market is closed for the weekend.",
            "score_adjustment": 0.0,
        }
    if current_time < MARKET_OPEN:
        return {
            "window": "Pre-Market",
            "timing_bias": "Wait for Stabilization",
            "description": "Pre-market quotes can be thin and less reliable for research execution timing.",
            "score_adjustment": -6.0,
        }
    if MARKET_OPEN <= current_time < STABILIZATION_START:
        return {
            "window": "Open",
            "timing_bias": "Avoid Open",
            "description": "Opening prints digest overnight news and often carry the widest volatility burst.",
            "score_adjustment": -8.0,
        }
    if STABILIZATION_START <= current_time < STABILIZATION_END:
        return {
            "window": "Stabilization",
            "timing_bias": "Wait for Stabilization",
            "description": "Early volatility is settling; wait for spread, volume, and trend confirmation.",
            "score_adjustment": -2.0,
        }
    if MIDDAY_START <= current_time < MIDDAY_END:
        return {
            "window": "Midday Lull",
            "timing_bias": "Midday Review",
            "description": "Midday can be calmer, but lower liquidity means entries still need confirmation.",
            "score_adjustment": -1.0,
        }
    if POWER_HOUR_START <= current_time < CLOSING_AUCTION_START:
        return {
            "window": "Power Hour",
            "timing_bias": "Prefer Close Review",
            "description": "Late-session liquidity improves, but entries should still follow the trade plan.",
            "score_adjustment": 4.0,
        }
    if CLOSING_AUCTION_START <= current_time <= MARKET_CLOSE:
        return {
            "window": "Closing Auction",
            "timing_bias": "Prefer Close Review",
            "description": "Closing auction is a major liquidity event; use it as timing context only.",
            "score_adjustment": 6.0,
        }
    if current_time > MARKET_CLOSE:
        return {
            "window": "After Hours",
            "timing_bias": "No Timing Edge",
            "description": "Regular-session timing edge is unavailable after the close.",
            "score_adjustment": -4.0,
        }
    return {
        "window": "Regular Session",
        "timing_bias": "No Timing Edge",
        "description": "No distinct open, midday, or close timing edge is active.",
        "score_adjustment": 0.0,
    }


def _day_of_week_context(market_now):
    weekday = market_now.weekday()
    if weekday == 0:
        return {
            "label": "Monday weekend digest",
            "score_adjustment": -2.0,
            "sell_timing_reason": "Weekend news has just been absorbed; avoid treating the first prints as confirmation.",
        }
    if weekday == 1:
        return {
            "label": "Tuesday follow-through check",
            "score_adjustment": 1.0,
            "sell_timing_reason": "Use Tuesday action to confirm or reject Monday's move instead of assuming reversal.",
        }
    if weekday in {2, 3}:
        return {
            "label": "Midweek earnings/catalyst density",
            "score_adjustment": 1.0,
            "sell_timing_reason": "Check scheduled catalysts before holding through overnight earnings risk.",
        }
    if weekday == 4:
        return {
            "label": "Friday weekend-risk review",
            "score_adjustment": -4.0,
            "sell_timing_reason": "Friday raises weekend-gap risk; short-term plans should tighten review or exit timing.",
        }
    return {
        "label": "Market closed weekend",
        "score_adjustment": 0.0,
        "sell_timing_reason": "No regular-session action until the next open.",
    }


def _turn_of_month_context(market_now):
    today = market_now.date()
    trading_days = _month_trading_days(today.year, today.month)
    if not trading_days or today.weekday() >= 5:
        return {
            "active": False,
            "label": "No turn-of-month window",
            "score_adjustment": 0.0,
        }
    index = trading_days.index(today) if today in trading_days else -1
    is_last = today == trading_days[-1]
    is_first_three = 0 <= index <= 2
    if is_last or is_first_three:
        return {
            "active": True,
            "label": "Turn-of-month context",
            "score_adjustment": 2.0,
        }
    return {
        "active": False,
        "label": "No turn-of-month window",
        "score_adjustment": 0.0,
    }


def _assess_liquidity(snapshot=None, quote_data=None, now=None):
    snapshot = snapshot or {}
    quote_data = quote_data or {}
    market_now = _as_market_datetime(now)
    price = _safe_float(quote_data.get("last_price"), _safe_float(snapshot.get("price"), 0.0))
    bid = _safe_float(quote_data.get("bid"), 0.0)
    ask = _safe_float(quote_data.get("ask"), 0.0)
    volume = _safe_float(snapshot.get("volume"), 0.0)
    average_volume = _safe_float(snapshot.get("average_volume"), _safe_float(snapshot.get("avg_volume"), 0.0))
    has_bid_ask = bid > 0 and ask > 0 and ask >= bid
    spread_pct = ((ask - bid) / ((ask + bid) / 2) * 100) if has_bid_ask else None
    volume_ratio = (volume / average_volume) if average_volume > 0 else None
    timestamp = _parse_timestamp(quote_data.get("last_timestamp") or quote_data.get("timestamp"))
    is_stale_quote = False
    if timestamp is not None:
        is_stale_quote = (market_now - timestamp).total_seconds() > 15 * 60
    elif quote_data:
        is_stale_quote = True

    warnings = []
    blockers = []
    score_adjustment = 0.0

    if has_bid_ask:
        if spread_pct > 1.0:
            blockers.append(f"Spread is too wide for autonomous paper execution ({spread_pct:.2f}%).")
            score_adjustment -= 25.0
        elif spread_pct > 0.35:
            warnings.append(f"Spread is elevated ({spread_pct:.2f}%).")
            score_adjustment -= 8.0
        else:
            score_adjustment += 5.0
    else:
        warnings.append("Bid/ask is unavailable; free data can support research but not live readiness.")
        score_adjustment -= 3.0

    if is_stale_quote:
        blockers.append("Intraday quote is stale or missing a usable timestamp.")
        score_adjustment -= 20.0

    if volume_ratio is not None:
        if volume_ratio >= 1.2:
            score_adjustment += 4.0
        elif volume_ratio < 0.5:
            warnings.append(f"Volume is light versus normal ({volume_ratio:.2f}x).")
            score_adjustment -= 5.0

    if blockers:
        quality = "Blocked"
    elif warnings:
        quality = "Warning"
    else:
        quality = "Usable"

    return {
        "quality": quality,
        "has_bid_ask": has_bid_ask,
        "spread_pct": round(spread_pct, 3) if spread_pct is not None else None,
        "volume_ratio": round(volume_ratio, 3) if volume_ratio is not None else None,
        "warnings": warnings,
        "blockers": blockers,
        "score_adjustment": score_adjustment,
        "paper_trade_allowed": not blockers,
    }


def build_microstructure_context(symbol, snapshot=None, price_data=None, quote_data=None, now=None, data_quality=None):
    symbol = str(symbol or "").upper().strip()
    market_now = _as_market_datetime(now)
    data_quality = data_quality or {}
    intraday = classify_intraday_window(market_now)
    day_context = _day_of_week_context(market_now)
    tom_context = _turn_of_month_context(market_now)
    liquidity = _assess_liquidity(snapshot=snapshot, quote_data=quote_data, now=market_now)
    data_gate = data_quality.get("recommendation_gate", "Warning")
    data_confidence = data_quality.get("data_confidence", "Unknown")
    freshness = (
        quote_data.get("last_timestamp")
        if isinstance(quote_data, dict) and quote_data.get("last_timestamp")
        else data_quality.get("last_timestamp", "")
    )

    score = 50.0
    score += intraday["score_adjustment"]
    score += day_context["score_adjustment"]
    score += tom_context["score_adjustment"]
    score += liquidity["score_adjustment"]
    if data_gate == "Blocked" or data_confidence == "Low":
        score -= 20.0
    score = round(_clamp(score), 1)

    warnings = list(liquidity.get("warnings", []))
    blockers = list(liquidity.get("blockers", []))
    if data_gate == "Blocked":
        blockers.append("Data quality gate is blocked; timing context cannot approve action.")
    if intraday["timing_bias"] in {"Avoid Open", "Wait for Stabilization"}:
        warnings.append(intraday["description"])
    if day_context["label"] == "Friday weekend-risk review":
        warnings.append(day_context["sell_timing_reason"])

    preferred_entry = "Follow the trade plan; no distinct timing edge."
    if intraday["timing_bias"] == "Avoid Open":
        preferred_entry = "Avoid the first 15 minutes; wait for stabilization and spread confirmation."
    elif intraday["timing_bias"] == "Wait for Stabilization":
        preferred_entry = "Wait for stabilization before any paper entry review."
    elif intraday["timing_bias"] == "Midday Review":
        preferred_entry = "Use midday only for review; require confirmation because liquidity can be lower."
    elif intraday["timing_bias"] == "Prefer Close Review":
        preferred_entry = "Prefer late-session review only if the trade plan already supports entry."

    preferred_exit = "Use named sell, trim, stop, and invalidation triggers."
    if day_context["label"] == "Friday weekend-risk review":
        preferred_exit = "For short-term plans, review exit or trim before the close to manage weekend-gap risk."
    elif intraday["window"] in {"Power Hour", "Closing Auction"}:
        preferred_exit = "Late-session liquidity is preferred for planned trims/exits when triggers fire."

    calendar_notes = [day_context["label"], tom_context["label"], intraday["window"]]
    direction = "Supports" if score >= 62 and not blockers else "Warns" if warnings or blockers else "Neutral"
    reason_stack = [
        make_reason(
            "Calendar",
            direction,
            "Medium" if direction != "Neutral" else "Low",
            f"{intraday['window']}: {intraday['description']}",
            "Market Microstructure & Calendar Context",
            freshness,
            "Timing context improves when spreads, volume, and the trade plan agree.",
        ),
        make_reason(
            "Risk",
            "Blocks" if blockers else "Warns" if warnings else "Neutral",
            "High" if blockers else "Medium" if warnings else "Low",
            " | ".join(blockers or warnings or ["No major liquidity timing warning."]),
            "Market Microstructure & Calendar Context",
            freshness,
            "Use fresh intraday quote data with acceptable spread before autonomous execution.",
        ),
    ]

    return {
        "symbol": symbol,
        "as_of": market_now.isoformat(),
        "session_window": intraday["window"],
        "intraday_window": intraday["window"],
        "timing_bias": intraday["timing_bias"],
        "day_of_week_context": day_context["label"],
        "turn_of_month_context": tom_context["label"],
        "turn_of_month_active": tom_context["active"],
        "calendar_context": calendar_notes,
        "liquidity_quality": liquidity["quality"],
        "liquidity_warning": " | ".join(blockers or warnings),
        "liquidity": liquidity,
        "preferred_entry_window": preferred_entry,
        "preferred_exit_window": preferred_exit,
        "sell_timing_reason": preferred_exit,
        "microstructure_score": score,
        "paper_trade_allowed": data_gate != "Blocked" and liquidity.get("paper_trade_allowed", True),
        "reason_stack": reason_stack,
        "warnings": warnings,
        "blockers": blockers,
        "summary": (
            f"{symbol or 'Selected asset'} timing context: {intraday['window']} "
            f"({intraday['timing_bias']}), {day_context['label']}, "
            f"{tom_context['label']}; liquidity {liquidity['quality']}."
        ),
    }


def build_reason_stack(
    data_quality=None,
    lane="",
    final_recommendation=None,
    microstructure_context=None,
    risk=None,
    news_context=None,
    fundamentals=None,
    agent_evidence=None,
    trade_plan=None,
):
    data_quality = data_quality or {}
    final_recommendation = final_recommendation or {}
    microstructure_context = microstructure_context or {}
    risk = risk or {}
    news_context = news_context or {}
    fundamentals = fundamentals or {}
    agent_evidence = agent_evidence or []
    trade_plan = trade_plan or {}

    gate = data_quality.get("recommendation_gate", "Warning")
    confidence = data_quality.get("data_confidence", "Unknown")
    stack = [
        make_reason(
            "Data",
            "Blocks" if gate == "Blocked" or confidence == "Low" else "Supports" if gate == "Trusted" else "Warns",
            "High" if gate == "Blocked" else "Medium" if gate == "Warning" else "Low",
            f"Data gate {gate}; confidence {confidence}.",
            data_quality.get("source") or data_quality.get("provider") or "Data Quality Gate",
            data_quality.get("last_timestamp", ""),
            "Refresh source data and remove fallback/mock inputs.",
        )
    ]

    if lane:
        stack.append(
            make_reason(
                "Agent",
                "Supports" if lane not in {"Needs Data", "Avoid"} else "Blocks" if lane == "Needs Data" else "Warns",
                "Medium",
                f"Best lane is {lane}; verdict is {final_recommendation.get('final_verdict', 'Watch')}.",
                "Judge Agent",
                "",
                "Lane changes when agent votes, data quality, or risk-adjusted scores change.",
            )
        )

    if risk:
        volatility = _safe_float(risk.get("volatility_pct"), 0.0)
        drawdown = abs(_safe_float(risk.get("max_drawdown_pct"), 0.0))
        warns = volatility >= 30 or drawdown >= 15
        stack.append(
            make_reason(
                "Technical",
                "Warns" if warns else "Supports",
                "Medium" if warns else "Low",
                f"Volatility {volatility:.1f}%; max drawdown {drawdown:.1f}%.",
                "Technical/Timing Agent",
                "",
                "Entry quality improves when volatility and drawdown return inside the risk budget.",
            )
        )

    if fundamentals:
        quality = fundamentals.get("fundamental_quality", "Neutral")
        stack.append(
            make_reason(
                "Fundamentals",
                "Supports" if quality == "Supportive" else "Warns" if quality == "Weak" else "Neutral",
                "Medium",
                f"Fundamental quality is {quality}.",
                "Fundamentals Agent",
                "",
                "Long-term conviction improves with fresh official profitability, growth, and balance-sheet evidence.",
            )
        )

    if news_context:
        sentiment = news_context.get("market_sentiment", "Neutral")
        flags = news_context.get("risk_flags", []) or []
        stack.append(
            make_reason(
                "News",
                "Warns" if flags or sentiment == "Bearish" else "Supports" if sentiment == "Bullish" else "Neutral",
                "Medium" if flags else "Low",
                f"Sentiment is {sentiment}; risk flags: {', '.join(flags) if flags else 'none'}.",
                "News/Sentiment Agent",
                "",
                "News view changes when fresh headlines or catalysts contradict the thesis.",
            )
        )

    stack.extend(microstructure_context.get("reason_stack", []))

    supportive_agents = [
        row.get("agent_name", "Agent")
        for row in agent_evidence
        if row.get("status") == "Supportive" and row.get("agent_name") != "Bull/Bear Critic"
    ]
    if supportive_agents:
        stack.append(
            make_reason(
                "Agent",
                "Supports",
                "Medium",
                "Supportive agents: " + ", ".join(supportive_agents[:4]) + ".",
                "Agent Research Desk",
                "",
                "Agent support weakens if evidence moves to Needs Review or Against.",
            )
        )

    if trade_plan.get("sell_triggers"):
        stack.append(
            make_reason(
                "Exit",
                "Supports",
                "Medium",
                f"Sell plan has {len(trade_plan.get('sell_triggers', []))} named trigger(s).",
                "Trade Plan",
                "",
                "A plan is invalid without explicit sell, trim, stop, invalidation, and time-stop logic.",
            )
        )

    return stack
