import json
from datetime import datetime

from data_quality_engine import evaluate_data_quality
from db_service import (
    load_agent_evidence,
    load_agent_runs,
    load_ticker_memory,
    save_agent_evidence,
    save_agent_run,
    save_ticker_memory,
)
from final_recommendation_engine import build_final_recommendation
from fundamental_catalyst_engine import generate_fundamental_catalyst_context
from market_microstructure_engine import build_microstructure_context, build_reason_stack
from market_data import get_market_snapshot, get_price_history, get_risk_metrics
from multi_horizon_router import route_multi_horizon_opportunity
from regime_engine import detect_market_regime
from signal_engine import generate_signal
from research_data_hub import build_source_manifest_item


FUTURES_PROXY_SYMBOLS = {
    "SPY": "S&P 500 index proxy",
    "QQQ": "Nasdaq 100 index proxy",
    "IWM": "Russell 2000 index proxy",
    "DIA": "Dow Jones index proxy",
    "GLD": "Gold proxy",
    "SLV": "Silver proxy",
    "USO": "Crude oil proxy",
    "UNG": "Natural gas proxy",
    "TLT": "Long-duration Treasury proxy",
    "IEF": "Intermediate Treasury proxy",
    "UUP": "US dollar proxy",
    "XLE": "Energy sector proxy",
    "XLF": "Financial sector proxy",
    "XLK": "Technology sector proxy",
}

LANES = {"Long Term", "Short Term", "Futures Proxy", "Needs Data"}


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, value))


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _json_list(value):
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else [value]
        except Exception:
            return [value] if value else []
    return value or []


def _status_from_score(score):
    if score >= 70:
        return "Supportive"
    if score >= 50:
        return "Cautious"
    if score >= 35:
        return "Needs Review"
    return "Against"


def _combine_quality(snapshot, price_data):
    snapshot_quality = evaluate_data_quality(snapshot)
    price_quality = evaluate_data_quality(price_data)
    gates = {snapshot_quality.get("recommendation_gate"), price_quality.get("recommendation_gate")}
    confidences = {snapshot_quality.get("data_confidence"), price_quality.get("data_confidence")}

    if "Blocked" in gates:
        gate = "Blocked"
    elif "Warning" in gates:
        gate = "Warning"
    else:
        gate = "Trusted"

    if "Low" in confidences:
        confidence = "Low"
    elif "Medium" in confidences:
        confidence = "Medium"
    else:
        confidence = "High"

    issues = snapshot_quality.get("issues", []) + price_quality.get("issues", [])
    return {
        "recommendation_gate": gate,
        "data_confidence": confidence,
        "snapshot_quality": snapshot_quality,
        "price_quality": price_quality,
        "issues": issues,
        "summary": (
            f"Snapshot gate {snapshot_quality.get('recommendation_gate')}; "
            f"history gate {price_quality.get('recommendation_gate')}."
        ),
    }


def _build_lane_scores(symbol, signal_data, risk, fundamentals, regime_data, news_context, data_quality, profile):
    symbol = str(symbol or "").upper()
    signal_score = _safe_float(signal_data.get("score"), 50.0)
    fundamental_score = _safe_float(fundamentals.get("fundamental_score"), 50.0)
    volatility = _safe_float(risk.get("volatility_pct"), 0.0)
    drawdown = abs(_safe_float(risk.get("max_drawdown_pct"), 0.0))
    return_pct = _safe_float(risk.get("return_pct"), 0.0)
    sentiment = news_context.get("market_sentiment", "Neutral")
    regime = regime_data.get("regime", "Unknown")

    router = route_multi_horizon_opportunity(
        symbol,
        {**signal_data, "recommendation_gate": data_quality.get("recommendation_gate")},
        risk,
        fundamentals,
        {},
        {},
        profile or {},
    )

    short_score = signal_score + min(return_pct, 12.0) - volatility * 0.45 - drawdown * 0.2
    long_score = signal_score * 0.35 + fundamental_score * 0.55 - drawdown * 0.15
    futures_score = signal_score * 0.45 + max(0.0, 100.0 - volatility * 1.2) * 0.25
    futures_score += 8.0 if symbol in FUTURES_PROXY_SYMBOLS else -18.0
    futures_score += 5.0 if regime in {"Bull Trend", "Recovery", "Sideways / Range"} else -5.0
    futures_score += 3.0 if sentiment == "Bullish" else -3.0 if sentiment == "Bearish" else 0.0

    scores = {
        "Short Term": round(_clamp(short_score), 1),
        "Long Term": round(_clamp(long_score), 1),
        "Futures Proxy": round(_clamp(futures_score), 1),
    }
    if data_quality.get("recommendation_gate") == "Blocked":
        return {
            "lane": "Needs Data",
            "score": min(scores.values()) if scores else 0.0,
            "scores": scores,
            "router": router,
            "reason": "Data quality blocks opportunity lanes until fresh non-mock data is available.",
        }

    lane = max(scores, key=scores.get)
    return {
        "lane": lane,
        "score": scores[lane],
        "scores": scores,
        "router": router,
        "reason": f"{lane} has the strongest risk-adjusted evidence in this run.",
    }


def _agent_result(agent_name, score, key_points, concerns=None, sources=None, memory=None, recommendation=""):
    return {
        "agent_name": agent_name,
        "status": _status_from_score(score),
        "score": round(_clamp(score), 1),
        "key_points": key_points,
        "concerns": concerns or [],
        "sources_used": sources or [],
        "memory_references": memory or [],
        "recommendation": recommendation,
    }


def _build_agent_evidence(
    symbol,
    lane_data,
    data_quality,
    news_context,
    fundamentals,
    risk,
    regime_data,
    profile,
    prior_memory,
    microstructure_context=None,
):
    symbol = str(symbol or "").upper()
    memory_refs = []
    if prior_memory:
        memory_refs.append(
            f"Prior verdict {prior_memory.get('last_verdict', 'Unknown')} in {prior_memory.get('last_lane', 'Unknown')} lane."
        )

    data_score = {"High": 82, "Medium": 58, "Low": 25}.get(data_quality.get("data_confidence"), 45)
    data_concerns = list(data_quality.get("issues", []))
    evidence = [
        _agent_result(
            "Data Quality Agent",
            data_score,
            [data_quality.get("summary", "Data quality reviewed.")],
            data_concerns,
            ["market snapshot", "price history"],
            memory_refs,
            "Block buy/add labels until data gate is not Blocked."
            if data_quality.get("recommendation_gate") == "Blocked"
            else "Data is usable for research with the displayed confidence gate.",
        )
    ]

    sentiment = news_context.get("market_sentiment", "Neutral")
    news_score = 72 if sentiment == "Bullish" else 48 if sentiment == "Neutral" else 32
    news_score -= min(18, len(news_context.get("risk_flags", []) or []) * 6)
    evidence.append(
        _agent_result(
            "News/Sentiment Agent",
            news_score,
            [
                f"Sentiment is {sentiment}.",
                "Events: " + (", ".join(news_context.get("event_tags", []) or []) or "None."),
            ],
            [f"Risk flag: {flag}" for flag in news_context.get("risk_flags", []) or []],
            ["recent headlines", "news sentiment rules"],
            memory_refs,
            "Use news as context, not proof.",
        )
    )

    fundamental_score = _safe_float(fundamentals.get("fundamental_score"), 50.0)
    evidence.append(
        _agent_result(
            "Fundamentals Agent",
            fundamental_score,
            [
                f"Fundamental quality is {fundamentals.get('fundamental_quality', 'Neutral')}.",
                fundamentals.get("summary", "Fundamentals reviewed."),
            ],
            fundamentals.get("risk_flags", []),
            ["SEC/company facts when available", "fundamental catalyst engine"],
            memory_refs,
            "Favor long-term lane only when fundamentals are supportive and data limitations are clear.",
        )
    )

    technical_score = lane_data.get("scores", {}).get("Short Term", 50.0)
    evidence.append(
        _agent_result(
            "Technical/Timing Agent",
            technical_score,
            [
                f"Return {risk.get('return_pct', 0.0):+.2f}%.",
                f"Volatility {risk.get('volatility_pct', 0.0):.2f}%; drawdown {risk.get('max_drawdown_pct', 0.0):.2f}%.",
                f"Regime is {regime_data.get('regime', 'Unknown')}.",
            ],
            ["High volatility weakens entry quality."] if _safe_float(risk.get("volatility_pct")) >= 30 else [],
            ["price history", "regime engine", "risk metrics"],
            memory_refs,
            "Prefer wait/pullback labels when volatility or drawdown are elevated.",
        )
    )

    microstructure_context = microstructure_context or {}
    micro_score = _safe_float(microstructure_context.get("microstructure_score"), 45.0)
    micro_concerns = list(microstructure_context.get("blockers", [])) + list(microstructure_context.get("warnings", []))
    evidence.append(
        _agent_result(
            "Microstructure/Calendar Agent",
            micro_score,
            [
                microstructure_context.get("summary", "Market microstructure and calendar context reviewed."),
                f"Timing bias: {microstructure_context.get('timing_bias', 'No Timing Edge')}.",
                f"Entry window: {microstructure_context.get('preferred_entry_window', 'Follow the trade plan.')}",
                f"Exit window: {microstructure_context.get('preferred_exit_window', 'Use named exit triggers.')}",
            ],
            micro_concerns,
            ["session clock", "day-of-week context", "turn-of-month context", "liquidity checks"],
            memory_refs,
            "Use timing context only as a weak-to-moderate modifier; it cannot create a buy/add verdict by itself.",
        )
    )

    futures_score = lane_data.get("scores", {}).get("Futures Proxy", 0.0)
    proxy_note = FUTURES_PROXY_SYMBOLS.get(symbol, "Not a direct futures proxy symbol.")
    evidence.append(
        _agent_result(
            "Futures Proxy Agent",
            futures_score,
            [proxy_note, "Futures exposure is proxy-only through ETFs or broad market instruments."],
            [] if symbol in FUTURES_PROXY_SYMBOLS else ["Single-name stocks are not futures proxies."],
            ["ETF/proxy classification", "market regime"],
            memory_refs,
            "No direct futures contracts, leverage, margin, or execution.",
        )
    )

    risk_tolerance = (profile or {}).get("risk_tolerance", "Moderate")
    risk_score = 65 if risk_tolerance == "High" else 55 if risk_tolerance == "Moderate" else 42
    if _safe_float(risk.get("volatility_pct")) >= 30:
        risk_score -= 12
    evidence.append(
        _agent_result(
            "Risk/Portfolio Agent",
            risk_score,
            [
                f"Profile risk tolerance: {risk_tolerance}.",
                f"Selected lane: {lane_data.get('lane')}.",
            ],
            ["Human review required before any real-world action."],
            ["financial profile", "risk metrics"],
            memory_refs,
            "Keep sizing conservative and compare against benchmark before adding risk.",
        )
    )

    exit_score = 68.0 if data_quality.get("recommendation_gate") != "Blocked" else 35.0
    evidence.append(
        _agent_result(
            "Exit Plan Agent",
            exit_score,
            [
                "Sell if the thesis breaks, the stop is hit, the time stop expires, or market risk downgrades.",
                "Trim at the first target or when conviction weakens while still profitable.",
                microstructure_context.get("sell_timing_reason", "Use named sell/trim triggers rather than time-of-day alone."),
            ],
            ["Exit plan still requires human review before any real-world action."],
            ["trade plan rules", "microstructure timing context", "risk metrics"],
            memory_refs,
            "No plan is valid unless sell, trim, stop, invalidation, and review timing are named.",
        )
    )

    bull_points = []
    bear_points = []
    for item in evidence:
        if item["status"] == "Supportive":
            bull_points.extend(item.get("key_points", [])[:1])
        if item["status"] in {"Against", "Needs Review"} or item.get("concerns"):
            bear_points.extend((item.get("concerns") or item.get("key_points", []))[:1])
    if not bull_points:
        bull_points.append("No strong bull case yet; setup needs more evidence.")
    if not bear_points:
        bear_points.append("Main bearish case is that research evidence can change quickly.")

    evidence.append(
        {
            "agent_name": "Bull/Bear Critic",
            "status": "Needs Review",
            "score": 50.0,
            "key_points": ["Bull case: " + " | ".join(bull_points[:3])],
            "concerns": ["Bear case: " + " | ".join(bear_points[:3])],
            "sources_used": ["specialist agent evidence"],
            "memory_references": memory_refs,
            "recommendation": "Force both sides of the thesis before accepting the judge verdict.",
            "bull_case": bull_points,
            "bear_case": bear_points,
            "invalidation_triggers": [
                "Data gate becomes Blocked.",
                "Signal score falls below 45.",
                "Volatility or drawdown moves outside risk budget.",
                "News or fundamentals contradict the thesis.",
            ],
        }
    )
    return evidence


def _judge_explanation(final, data_quality, lane_data, microstructure_context, reason_stack):
    support = [row for row in reason_stack if row.get("direction") == "Supports"][:3]
    caution = [row for row in reason_stack if row.get("direction") in {"Warns", "Blocks"}][:3]
    return {
        "data_gate": (
            f"Data gate {data_quality.get('recommendation_gate', 'Warning')} "
            f"with {data_quality.get('data_confidence', 'Unknown')} confidence."
        ),
        "best_lane": lane_data.get("lane", "Needs Data"),
        "top_supporting_reasons": [row.get("reason", "") for row in support],
        "top_caution_reasons": [row.get("reason", "") for row in caution],
        "entry_timing": microstructure_context.get("preferred_entry_window", "Follow the trade plan."),
        "sell_trim_timing": microstructure_context.get("preferred_exit_window", "Use named sell/trim triggers."),
        "what_would_change_this": final.get("what_would_change_this", []),
    }


def _memory_delta(prior_memory, final_verdict, lane):
    if not prior_memory:
        return "No prior narrative memory for this ticker."
    changes = []
    if prior_memory.get("last_verdict") != final_verdict:
        changes.append(f"Verdict changed from {prior_memory.get('last_verdict') or 'Unknown'} to {final_verdict}.")
    if prior_memory.get("last_lane") != lane:
        changes.append(f"Lane changed from {prior_memory.get('last_lane') or 'Unknown'} to {lane}.")
    if not changes:
        changes.append("Verdict and lane are consistent with prior memory.")
    return " ".join(changes)


def run_agent_research_desk(
    symbol,
    run_type="On Demand",
    snapshot=None,
    price_data=None,
    risk=None,
    news_context=None,
    signal_data=None,
    regime_data=None,
    fundamentals=None,
    profile=None,
    save_memory=False,
    microstructure_context=None,
    quote_data=None,
    now=None,
):
    """Run the specialist-agent research desk and optionally persist memory."""
    symbol = str(symbol or "").upper().strip()
    if not symbol:
        return {"symbol": "", "final_verdict": "Needs Data", "summary": "No symbol provided."}

    snapshot = snapshot or get_market_snapshot(symbol)
    price_data = price_data or get_price_history(symbol, period="1mo")
    chart_input = price_data.get("data") if isinstance(price_data, dict) else price_data
    risk = risk or get_risk_metrics(chart_input)
    if news_context is None:
        from news_engine import generate_news_context

        news_context = generate_news_context(symbol)
    signal_data = signal_data or generate_signal(symbol, snapshot, risk, news_context=news_context)
    regime_data = regime_data or detect_market_regime(price_data, risk)
    fundamentals = fundamentals or generate_fundamental_catalyst_context(symbol)
    profile = profile or {}

    prior_memory = load_ticker_memory(symbol)
    prior_runs = load_agent_runs(symbol=symbol, limit=5)
    data_quality = _combine_quality(snapshot, price_data)
    data_source_manifest = [
        build_source_manifest_item(symbol, "snapshot", snapshot),
        build_source_manifest_item(symbol, "history", price_data),
    ]
    lane_data = _build_lane_scores(symbol, signal_data, risk, fundamentals, regime_data, news_context, data_quality, profile)
    microstructure_context = microstructure_context or build_microstructure_context(
        symbol,
        snapshot=snapshot,
        price_data=price_data,
        quote_data=quote_data,
        now=now,
        data_quality=data_quality,
    )
    evidence = _build_agent_evidence(
        symbol,
        lane_data,
        data_quality,
        news_context,
        fundamentals,
        risk,
        regime_data,
        profile,
        prior_memory,
        microstructure_context=microstructure_context,
    )

    engine_votes = []
    for item in evidence:
        if item["agent_name"] == "Bull/Bear Critic":
            continue
        action = "Buy Candidate" if item["score"] >= 74 else "Watch" if item["score"] >= 45 else "Avoid"
        if item["agent_name"] == "Data Quality Agent" and data_quality.get("recommendation_gate") == "Blocked":
            action = "Needs Data"
        if item["agent_name"] == "Microstructure/Calendar Agent":
            if microstructure_context.get("blockers"):
                action = "Needs Data"
            elif microstructure_context.get("timing_bias") in {"Avoid Open", "Wait for Stabilization"}:
                action = "Wait for Pullback"
            else:
                action = "Watch"
        if item["agent_name"] == "Exit Plan Agent":
            action = "Needs Data" if data_quality.get("recommendation_gate") == "Blocked" else "Watch"
        if item["agent_name"] == "Futures Proxy Agent" and lane_data.get("lane") == "Futures Proxy":
            action = "Buy Candidate" if item["score"] >= 70 else "Watch"
        engine_votes.append(
            {
                "engine": item["agent_name"],
                "action": action,
                "score": item["score"],
                "reason": item["recommendation"],
            }
        )

    portfolio_context = {
        "score": lane_data.get("score", signal_data.get("score", 50)),
        "volatility_pct": risk.get("volatility_pct", 0.0),
        "max_drawdown_pct": risk.get("max_drawdown_pct", 0.0),
        "time_horizon": lane_data.get("lane", "Needs Data"),
        "target_allocation_band": "Research queue only",
        "risk_budget": "No real-world risk; paper/research review only.",
        "recommendation_gate": data_quality.get("recommendation_gate", "Warning"),
        "data_confidence": data_quality.get("data_confidence", "Unknown"),
    }
    final = build_final_recommendation(
        symbol,
        engine_votes,
        portfolio_context,
        data_quality,
        {"status": "Risk allowed"},
        {"confidence_adjustment": 0.0},
    )
    if data_quality.get("recommendation_gate") == "Blocked":
        final["final_verdict"] = "Needs Data"
        final["paper_trade_eligible"] = False

    critic = next((item for item in evidence if item["agent_name"] == "Bull/Bear Critic"), {})
    reason_stack = build_reason_stack(
        data_quality=data_quality,
        lane=lane_data.get("lane", "Needs Data"),
        final_recommendation=final,
        microstructure_context=microstructure_context,
        risk=risk,
        news_context=news_context,
        fundamentals=fundamentals,
        agent_evidence=evidence,
    )
    judge_explanation = _judge_explanation(final, data_quality, lane_data, microstructure_context, reason_stack)
    memory_delta = _memory_delta(prior_memory, final.get("final_verdict", "Watch"), lane_data.get("lane", "Needs Data"))
    thesis_snapshot = (
        f"{symbol}: {final.get('final_verdict', 'Watch')} in {lane_data.get('lane', 'Needs Data')} lane. "
        f"{final.get('summary', '')}"
    )
    result = {
        "symbol": symbol,
        "run_type": run_type,
        "lane": lane_data.get("lane", "Needs Data"),
        "lane_scores": lane_data.get("scores", {}),
        "data_quality": data_quality,
        "final_verdict": final.get("final_verdict", "Watch"),
        "confidence": final.get("confidence", "Low"),
        "score": round(_safe_float(lane_data.get("score")), 1),
        "price": snapshot.get("price") if isinstance(snapshot, dict) else None,
        "market_regime": regime_data.get("regime", "Unknown"),
        "summary": final.get("summary", ""),
        "agent_evidence": evidence,
        "bull_case": critic.get("bull_case", []),
        "bear_case": critic.get("bear_case", []),
        "invalidation_triggers": critic.get("invalidation_triggers", []),
        "microstructure_context": microstructure_context,
        "reason_stack": reason_stack,
        "judge_explanation": judge_explanation,
        "data_source_manifest": data_source_manifest,
        "memory": prior_memory,
        "prior_runs": prior_runs,
        "memory_delta": memory_delta,
        "thesis_snapshot": thesis_snapshot,
        "human_review_required": True,
        "disclaimer": "Research-only agent output. No broker APIs, live trading, margin, leverage, direct futures contracts, or guaranteed profit.",
    }

    if save_memory:
        run_row = save_agent_run(
            symbol=symbol,
            run_type=run_type,
            lane=result["lane"],
            data_confidence=data_quality.get("data_confidence", "Unknown"),
            final_verdict=result["final_verdict"],
            confidence=result["confidence"],
            score=result["score"],
            summary=result["summary"],
            thesis_snapshot=thesis_snapshot,
            memory_delta=memory_delta,
            human_review_required=True,
        )
        result["run_id"] = run_row.get("id")
        for item in evidence:
            save_agent_evidence(run_id=result["run_id"], **item)
        lessons = prior_memory.get("lessons", "") if prior_memory else ""
        save_ticker_memory(
            symbol=symbol,
            thesis=thesis_snapshot,
            bull_case=" | ".join(result["bull_case"][:4]),
            bear_case=" | ".join(result["bear_case"][:4]),
            last_verdict=result["final_verdict"],
            last_lane=result["lane"],
            lessons=lessons,
        )

    return result


def generate_daily_agent_queue(scan_rows, limit=12):
    """Create a review queue across long-term, short-term, and futures-proxy lanes."""
    rows = []
    seen = set()
    for row in sorted(scan_rows or [], key=lambda item: _safe_float(item.get("score")), reverse=True):
        symbol = str(row.get("symbol", "")).upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        gate = row.get("recommendation_gate", "Warning")
        confidence = row.get("data_confidence", "Unknown")
        signal_score = _safe_float(row.get("score"), 50.0)
        volatility = _safe_float(row.get("volatility_pct"), 0.0)
        drawdown = abs(_safe_float(row.get("max_drawdown_pct"), 0.0))
        futures_bonus = 12 if symbol in FUTURES_PROXY_SYMBOLS else -12
        lane_scores = {
            "Short Term": round(_clamp(signal_score - volatility * 0.4 - drawdown * 0.15), 1),
            "Long Term": round(_clamp(signal_score * 0.75 - drawdown * 0.1), 1),
            "Futures Proxy": round(_clamp(signal_score * 0.65 + futures_bonus), 1),
        }
        if gate == "Blocked":
            lane = "Needs Data"
        elif symbol in FUTURES_PROXY_SYMBOLS:
            lane = "Futures Proxy"
        else:
            lane = max(lane_scores, key=lane_scores.get)
        rows.append(
            {
                "symbol": symbol,
                "run_type": "Daily Queue",
                "lane": lane,
                "score": lane_scores.get(lane, signal_score),
                "data_confidence": confidence,
                "recommendation_gate": gate,
                "reason": "Proxy-only futures lane." if lane == "Futures Proxy" else "Highest current lane score.",
            }
        )
        if len(rows) >= limit:
            break
    return {
        "queue": rows,
        "summary": f"Generated {len(rows)} agent research candidate(s) for review.",
    }


def evaluate_agent_research_memory(agent_runs=None, evidence_rows=None, recommendation_log=None):
    """Summarize which agent lanes and verdicts are working from evaluated recommendations."""
    agent_runs = agent_runs if agent_runs is not None else load_agent_runs(limit=500)
    evidence_rows = evidence_rows if evidence_rows is not None else load_agent_evidence(limit=1000)
    recommendation_log = recommendation_log or []

    evaluated = []
    for row in recommendation_log:
        realized = row.get("realized_return_pct")
        if realized in {None, ""}:
            continue
        engine_inputs = row.get("engine_inputs", {})
        if isinstance(engine_inputs, str):
            try:
                engine_inputs = json.loads(engine_inputs)
            except Exception:
                engine_inputs = {}
        evaluated.append(
            {
                **row,
                "realized_return_pct": _safe_float(realized),
                "lane": engine_inputs.get("lane", row.get("horizon", "Unknown")),
                "data_confidence": engine_inputs.get("data_confidence", row.get("data_gate", "Unknown")),
            }
        )

    def grouped(field):
        groups = {}
        for row in evaluated:
            key = row.get(field) or "Unknown"
            groups.setdefault(key, []).append(row)
        output = []
        for key, rows in groups.items():
            wins = [row for row in rows if _safe_float(row.get("realized_return_pct")) > 0]
            avg_return = sum(_safe_float(row.get("realized_return_pct")) for row in rows) / len(rows)
            output.append(
                {
                    field: key,
                    "count": len(rows),
                    "hit_rate": round((len(wins) / len(rows)) * 100, 2),
                    "average_return_pct": round(avg_return, 2),
                }
            )
        output.sort(key=lambda item: (item["average_return_pct"], item["hit_rate"]), reverse=True)
        return output

    agent_counts = {}
    for row in evidence_rows:
        name = row.get("agent_name", "Unknown Agent")
        agent_counts[name] = agent_counts.get(name, 0) + 1

    if evaluated:
        avg = sum(row["realized_return_pct"] for row in evaluated) / len(evaluated)
        confidence_adjustment = 6.0 if avg > 0 and len(evaluated) >= 5 else -6.0 if avg < 0 else 0.0
    else:
        confidence_adjustment = 0.0

    return {
        "total_agent_runs": len(agent_runs or []),
        "total_agent_evidence": len(evidence_rows or []),
        "evaluated_recommendations": len(evaluated),
        "lane_stats": grouped("lane"),
        "verdict_stats": grouped("action"),
        "data_confidence_stats": grouped("data_confidence"),
        "agent_activity": [
            {"agent_name": key, "evidence_count": value}
            for key, value in sorted(agent_counts.items(), key=lambda item: item[1], reverse=True)
        ],
        "confidence_adjustment": max(-10.0, min(10.0, confidence_adjustment)),
        "summary": (
            "No evaluated agent-linked recommendations yet."
            if not evaluated
            else f"Evaluated {len(evaluated)} agent-linked recommendation(s)."
        ),
    }
