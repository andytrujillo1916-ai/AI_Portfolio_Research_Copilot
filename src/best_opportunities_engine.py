from asset_sector_map import map_asset_to_sector
from data_quality_engine import evaluate_data_quality
from final_recommendation_engine import build_final_recommendation
from fundamental_catalyst_engine import generate_fundamental_catalyst_context
from market_data import get_market_snapshot, get_price_history, get_risk_metrics
from multi_horizon_router import route_multi_horizon_opportunity
from regime_engine import detect_market_regime
from sec_edgar_fundamentals import get_sec_fundamental_context
from signal_engine import generate_signal


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _combined_quality(snapshot, price_data, row=None):
    row = row or {}
    snapshot_quality = evaluate_data_quality(snapshot)
    price_quality = evaluate_data_quality(price_data)
    gate = row.get("recommendation_gate")
    confidence = row.get("data_confidence")
    if not gate:
        gates = {snapshot_quality.get("recommendation_gate"), price_quality.get("recommendation_gate")}
        gate = "Blocked" if "Blocked" in gates else "Warning" if "Warning" in gates else "Trusted"
    if not confidence:
        confidences = {snapshot_quality.get("data_confidence"), price_quality.get("data_confidence")}
        confidence = "Low" if "Low" in confidences else "Medium" if "Medium" in confidences else "High"
    return {
        "recommendation_gate": gate,
        "data_confidence": confidence,
        "issues": snapshot_quality.get("issues", []) + price_quality.get("issues", []),
        "summary": f"Data gate {gate}; confidence {confidence}.",
    }


def _fundamental_proxy_from_row(row):
    score = row.get("fundamental_score")
    if score is None:
        growth_score = _safe_float(row.get("growth_score"), 50.0)
        score = 50.0 + ((growth_score - 50.0) * 0.35)
    if score >= 65:
        quality = "Supportive"
    elif score <= 40:
        quality = "Weak"
    else:
        quality = "Neutral"
    return {
        "fundamental_quality": quality,
        "fundamental_score": round(max(0.0, min(100.0, _safe_float(score, 50.0))), 1),
        "summary": "Free-first proxy fundamentals from available growth/catalyst context.",
        "risk_flags": [] if row.get("growth_risk_flags") in {None, ""} else [str(row.get("growth_risk_flags"))],
    }


def _generate_news_context(symbol):
    from news_engine import generate_news_context

    return generate_news_context(symbol)


def _get_sec_fundamental_context(symbol):
    return get_sec_fundamental_context(symbol)


def rank_best_opportunities(scan_rows, profile=None, accuracy_context=None, market_timing=None, limit=30):
    """Rank rows into long-term, short-term, and futures-proxy opportunity lanes."""
    profile = profile or {}
    accuracy_context = accuracy_context or {}
    market_timing = market_timing or {}
    ranked = []
    for row in scan_rows or []:
        symbol = str(row.get("symbol", "")).upper()
        if not symbol:
            continue
        fundamentals = _fundamental_proxy_from_row(row)
        router = route_multi_horizon_opportunity(
            symbol,
            {
                "score": row.get("score", 50),
                "recommendation_gate": row.get("recommendation_gate", "Warning"),
                "market_risk_level": market_timing.get("market_risk_level", ""),
            },
            row,
            fundamentals,
            {"catalysts": row.get("catalysts", []) if isinstance(row.get("catalysts"), list) else []},
            accuracy_context,
            profile,
        )
        ranked.append(
            {
                **row,
                "symbol": symbol,
                "best_lane": router.get("best_lane"),
                "best_holding_period": router.get("best_holding_period"),
                "entry_state": router.get("entry_state"),
                "lane_score": router.get("best_score"),
                "short_term_score": router.get("short_term_score"),
                "long_term_score": router.get("long_term_score"),
                "futures_proxy_score": router.get("futures_proxy_score"),
                "fundamental_score": fundamentals.get("fundamental_score"),
                "fundamental_quality": fundamentals.get("fundamental_quality"),
                "lane_reason": " | ".join(router.get("why", [])[:3]),
                "blocked_reasons": " | ".join(router.get("blocked_reasons", [])),
            }
        )
    ranked.sort(key=lambda item: item.get("lane_score", 0), reverse=True)
    by_lane = {
        "Long Term": [row for row in ranked if row.get("best_lane") == "Long Term"][:limit],
        "Short Term": [row for row in ranked if row.get("best_lane") == "Short Term"][:limit],
        "Futures Proxy": [row for row in ranked if row.get("best_lane") == "Futures Proxy"][:limit],
        "Needs Data": [row for row in ranked if row.get("best_lane") == "Needs Data"][:limit],
    }
    return {
        "ranked": ranked[:limit],
        "by_lane": by_lane,
        "summary": (
            f"Ranked {len(ranked)} opportunities across long-term, short-term, "
            "futures-proxy, and needs-data lanes."
        ),
    }


def run_any_ticker_research(symbol, profile=None, accuracy_context=None, market_timing=None, period="1mo"):
    """Return a compact source-labeled research packet for any ticker."""
    symbol = str(symbol or "").upper().strip()
    if not symbol:
        return {
            "symbol": "",
            "final_verdict": "Needs Data",
            "best_lane": "Needs Data",
            "summary": "No symbol provided.",
        }
    profile = profile or {}
    accuracy_context = accuracy_context or {}
    market_timing = market_timing or {}
    snapshot = get_market_snapshot(symbol)
    price_data = get_price_history(symbol, period=period)
    chart_input = price_data.get("data") if isinstance(price_data, dict) else price_data
    risk = get_risk_metrics(chart_input)
    quality = _combined_quality(snapshot, price_data)
    news_context = _generate_news_context(symbol)
    signal_data = generate_signal(symbol, snapshot, risk, news_context=news_context)
    regime_data = detect_market_regime(price_data, risk)
    sec_facts = _get_sec_fundamental_context(symbol)
    fundamentals = generate_fundamental_catalyst_context(symbol, sec_facts=sec_facts)
    router = route_multi_horizon_opportunity(
        symbol,
        {
            **signal_data,
            "recommendation_gate": quality.get("recommendation_gate"),
            "market_risk_level": market_timing.get("market_risk_level", ""),
        },
        risk,
        fundamentals,
        {},
        accuracy_context,
        profile,
    )
    engine_votes = [
        {
            "engine": "Best Opportunities Router",
            "action": router.get("entry_state", "Watch"),
            "score": router.get("best_score", 0),
            "reason": router.get("summary", ""),
        },
        {
            "engine": "Signal Engine",
            "action": signal_data.get("signal", "Watch"),
            "score": signal_data.get("score", 0),
            "reason": "Signal score, price trend, volatility, and news context.",
        },
        {
            "engine": "Data Quality Gate",
            "action": "Needs Data" if quality.get("recommendation_gate") == "Blocked" else "Watch",
            "score": quality.get("data_confidence", ""),
            "reason": quality.get("summary", ""),
        },
    ]
    final = build_final_recommendation(
        symbol,
        engine_votes,
        {
            "score": router.get("best_score", signal_data.get("score", 50)),
            "volatility_pct": risk.get("volatility_pct", 0.0),
            "max_drawdown_pct": risk.get("max_drawdown_pct", 0.0),
            "time_horizon": router.get("best_lane", "Needs Data"),
            "target_allocation_band": "Research/watchlist only",
            "risk_budget": "No real-world risk; human review required.",
            "recommendation_gate": quality.get("recommendation_gate"),
            "data_confidence": quality.get("data_confidence"),
        },
        quality,
        {"status": "Risk allowed"},
        accuracy_context,
        market_timing_context=market_timing,
    )
    if quality.get("recommendation_gate") == "Blocked":
        final["final_verdict"] = "Needs Data"
        final["paper_trade_eligible"] = False

    return {
        "symbol": symbol,
        "snapshot": snapshot,
        "risk": risk,
        "news_context": news_context,
        "signal_data": signal_data,
        "regime": regime_data.get("regime", "Unknown"),
        "fundamentals": fundamentals,
        "data_quality": quality,
        "best_lane": "Needs Data" if quality.get("recommendation_gate") == "Blocked" else router.get("best_lane"),
        "best_holding_period": router.get("best_holding_period"),
        "entry_state": router.get("entry_state"),
        "final_verdict": final.get("final_verdict", "Watch"),
        "confidence": final.get("confidence", "Low"),
        "score": router.get("best_score"),
        "lane_scores": {
            "Short Term": router.get("short_term_score"),
            "Long Term": router.get("long_term_score"),
            "Futures Proxy": router.get("futures_proxy_score"),
        },
        "evidence": router.get("why", []) + signal_data.get("reasons", [])[:2],
        "risks": quality.get("issues", []) + signal_data.get("risks", [])[:3] + fundamentals.get("risk_flags", [])[:2],
        "what_would_change_this": final.get("what_would_change_this", []),
        "watchlist_view": "Add to watchlist for research" if final.get("final_verdict") in {"Buy Candidate", "Add", "Watch", "Wait for Pullback"} else "Do not prioritize until data/evidence improves",
        "sector": map_asset_to_sector(symbol),
        "summary": final.get("summary", ""),
        "disclaimer": "Research-only packet; no broker APIs, live trading, direct futures contracts, margin, leverage, or guaranteed returns.",
    }
