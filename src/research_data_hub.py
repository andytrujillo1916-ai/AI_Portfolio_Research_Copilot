import hashlib
import json
from datetime import datetime, timezone

from data_quality_engine import evaluate_data_quality
from data_source_registry import get_data_source_metadata
from opportunity_universe import build_opportunity_universe
from sp500_universe import get_sp500_style_universe


SAVED_SCREEN_PRESETS = {
    "Long-Term Quality": "Quality, growth, lower drawdown, and usable fundamentals.",
    "Short-Term Momentum": "Momentum, trend, news/catalyst support, and manageable volatility.",
    "Pullback Watchlist": "Good enough thesis, but timing or volatility says wait.",
    "High Risk / Avoid": "Weak evidence, high volatility, deep drawdown, or data problems.",
    "Short-Sale Research": "Weak trend and bearish evidence; research-only, no margin or execution.",
    "Needs Data": "Fallback, stale, or missing source fields block recommendations.",
}


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, value))


def _normalize_symbol(symbol):
    return str(symbol or "").upper().strip()


def _now():
    return datetime.now(timezone.utc).isoformat()


def _stable_signature(symbols):
    payload = json.dumps(sorted(set(symbols or [])))
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def _origin_priority(origin):
    return {
        "selected": 0,
        "manual": 1,
        "dynamic_scan": 2,
        "best_opportunity": 3,
        "holding": 4,
        "agent_queue": 5,
        "opportunity_seed": 6,
        "sp500_seed": 7,
        "watchlist_seed": 8,
    }.get(origin, 50)


def _merge_row(existing, incoming):
    output = dict(existing or {})
    origins = set(output.get("origins", []))
    origins.update(incoming.get("origins", []))
    if incoming.get("origin"):
        origins.add(incoming.get("origin"))
    for key, value in incoming.items():
        if key in {"origins"}:
            continue
        if value not in {None, ""}:
            output[key] = value
    output["origins"] = sorted(origins, key=_origin_priority)
    output["origin"] = output["origins"][0] if output["origins"] else incoming.get("origin", "")
    return output


def _add_universe_row(rows_by_symbol, row, origin):
    if isinstance(row, str):
        row = {"symbol": row}
    row = dict(row or {})
    symbol = _normalize_symbol(row.get("symbol"))
    if not symbol:
        return
    row["symbol"] = symbol
    row["origin"] = origin
    row["origins"] = [origin]
    rows_by_symbol[symbol] = _merge_row(rows_by_symbol.get(symbol, {}), row)


def build_source_manifest_item(symbol, dataset, data_result=None, row=None):
    """Normalize source, freshness, trust, and allowed-use details for one dataset."""
    data_result = data_result or {}
    row = row or {}
    source = (
        data_result.get("source")
        or row.get("data_source")
        or row.get("source")
        or row.get("data_provider")
        or "unknown"
    )
    quality = evaluate_data_quality(data_result or {"source": source, "last_timestamp": row.get("last_timestamp", "")})
    metadata = get_data_source_metadata(source)
    trust = metadata.get("trust_level", "Warning")
    fallback = bool(quality.get("is_fallback") or source == "mock" or row.get("recommendation_gate") == "Blocked")
    missing_fields = quality.get("missing_fields", [])
    gate = row.get("recommendation_gate") or quality.get("recommendation_gate", "Warning")
    freshness = quality.get("data_confidence", row.get("data_confidence", "Unknown"))
    if fallback or gate == "Blocked":
        allowed_use = "display_only"
    elif trust == "Trusted" and freshness == "High":
        allowed_use = "research_and_recommendation"
    else:
        allowed_use = "research_only"
    return {
        "dataset": dataset,
        "symbol": _normalize_symbol(symbol),
        "provider": metadata.get("provider", source),
        "source": source,
        "source_url": metadata.get("source_url", ""),
        "timestamp": quality.get("last_timestamp") or row.get("last_timestamp", ""),
        "freshness": freshness,
        "freshness_confidence": freshness,
        "trust": trust,
        "source_trust": trust,
        "fallback": fallback,
        "missing_fields": missing_fields,
        "recommendation_gate": gate,
        "allowed_use": allowed_use,
        "issues": quality.get("issues", []) or str(row.get("data_issues", "")).split(" | "),
    }


def merge_research_universe(
    watchlist=None,
    dynamic_rows=None,
    best_opportunity_rows=None,
    paper_positions=None,
    real_holdings=None,
    agent_queue=None,
    manual_symbols=None,
    selected_symbol="",
):
    """Merge all symbol sources into one deduped universe with origin tags."""
    rows_by_symbol = {}
    _add_universe_row(rows_by_symbol, selected_symbol, "selected")
    for symbol in manual_symbols or []:
        _add_universe_row(rows_by_symbol, symbol, "manual")
    for row in dynamic_rows or []:
        _add_universe_row(rows_by_symbol, row, "dynamic_scan")
    for row in best_opportunity_rows or []:
        _add_universe_row(rows_by_symbol, row, "best_opportunity")

    positions = paper_positions or {}
    position_rows = positions.get("positions", positions) if isinstance(positions, dict) else positions
    if isinstance(position_rows, dict):
        for symbol, row in position_rows.items():
            payload = {"symbol": symbol, **(row if isinstance(row, dict) else {})}
            _add_universe_row(rows_by_symbol, payload, "holding")
    elif isinstance(position_rows, list):
        for row in position_rows:
            _add_universe_row(rows_by_symbol, row, "holding")
    for row in real_holdings or []:
        _add_universe_row(rows_by_symbol, row, "holding")
    for row in agent_queue or []:
        _add_universe_row(rows_by_symbol, row, "agent_queue")
    for row in build_opportunity_universe(scope="US_ADR", include_etfs=True, include_ipos=True):
        _add_universe_row(rows_by_symbol, row, "opportunity_seed")
    for row in get_sp500_style_universe():
        _add_universe_row(rows_by_symbol, row, "sp500_seed")
    for symbol in watchlist or []:
        _add_universe_row(rows_by_symbol, symbol, "watchlist_seed")

    rows = list(rows_by_symbol.values())
    rows.sort(key=lambda row: (_origin_priority(row.get("origin")), row.get("symbol", "")))
    return rows


def _quality_penalty(row):
    gate = row.get("recommendation_gate", "Warning")
    confidence = row.get("data_confidence", "Unknown")
    if gate == "Blocked" or confidence == "Low":
        return 35.0
    if gate == "Warning" or confidence == "Medium":
        return 8.0
    return 0.0


def _lane_label(score, gate):
    if gate == "Blocked":
        return "Needs Data"
    if score >= 70:
        return "Research Candidate"
    if score >= 55:
        return "Wait"
    if score >= 40:
        return "Watch"
    return "Avoid"


def rank_discovery_candidates(candidate_rows, market_timing=None):
    """Rank long-term buy, short-term buy, and short-sale research lanes from shared candidates."""
    market_timing = market_timing or {}
    ranked = []
    for row in candidate_rows or []:
        symbol = _normalize_symbol(row.get("symbol"))
        if not symbol:
            continue
        signal = _safe_float(row.get("score"), 50.0)
        growth = _safe_float(row.get("growth_score"), _safe_float(row.get("fundamental_score"), 50.0))
        fundamental = _safe_float(row.get("fundamental_score"), growth)
        return_pct = _safe_float(row.get("return_pct"), 0.0)
        volatility = _safe_float(row.get("volatility_pct"), 0.0)
        drawdown = abs(_safe_float(row.get("max_drawdown_pct"), 0.0))
        sentiment = row.get("news_sentiment", "Neutral")
        gate = row.get("recommendation_gate", "Warning")
        penalty = _quality_penalty(row)
        market_risk = market_timing.get("market_risk_level", "")

        sentiment_bonus = 5.0 if sentiment == "Bullish" else -6.0 if sentiment == "Bearish" else 0.0
        long_term = (fundamental * 0.45) + (growth * 0.25) + (signal * 0.20) + max(0, 15 - drawdown) * 0.5
        long_term -= max(0, volatility - 22) * 0.35
        short_term = signal + min(return_pct, 15.0) * 0.9 + sentiment_bonus
        short_term -= max(0, volatility - 18) * 0.55 + drawdown * 0.25
        short_sale = 45.0
        short_sale += max(0, -return_pct) * 1.1
        short_sale += max(0, drawdown - 8) * 0.8
        short_sale += 9.0 if sentiment == "Bearish" else -4.0 if sentiment == "Bullish" else 0.0
        short_sale += max(0, 45 - signal) * 0.6
        short_sale += 5.0 if market_risk in {"High", "Elevated"} else 0.0

        long_term -= penalty
        short_term -= penalty
        short_sale -= penalty * 0.8
        if gate == "Blocked":
            long_term = short_term = short_sale = 20.0

        lane_scores = {
            "Long-Term Buy Research": round(_clamp(long_term), 1),
            "Short-Term Buy Research": round(_clamp(short_term), 1),
            "Short-Sale Research": round(_clamp(short_sale), 1),
        }
        best_lane = max(lane_scores, key=lane_scores.get)
        best_score = lane_scores[best_lane]
        if gate == "Blocked":
            best_lane = "Needs Data"
        label = _lane_label(best_score, gate)
        source_manifest = build_source_manifest_item(symbol, "candidate", row=row)
        drivers = [
            f"signal {signal:.1f}",
            f"return {return_pct:+.1f}%",
            f"volatility {volatility:.1f}%",
            f"drawdown {drawdown:.1f}%",
            f"fundamental {fundamental:.1f}",
            f"sentiment {sentiment}",
        ]
        if source_manifest.get("allowed_use") != "research_and_recommendation":
            drivers.append(f"source allows {source_manifest.get('allowed_use')}")
        ranked.append(
            {
                **row,
                "symbol": symbol,
                "best_lane": best_lane,
                "discovery_score": best_score,
                "opportunity_label": label,
                "long_term_score": lane_scores["Long-Term Buy Research"],
                "short_term_buy_score": lane_scores["Short-Term Buy Research"],
                "short_sale_score": lane_scores["Short-Sale Research"],
                "source_manifest": source_manifest,
                "source_trust": source_manifest.get("source_trust"),
                "freshness_confidence": source_manifest.get("freshness_confidence"),
                "allowed_use": source_manifest.get("allowed_use"),
                "why_is_this_here": (
                    f"{best_lane}: " + ", ".join(drivers[:5]) + ". "
                    f"Origin: {', '.join(row.get('origins', [row.get('origin', 'unknown')]))}."
                ),
                "what_removes_it": (
                    "Fresh non-fallback data is required." if gate == "Blocked"
                    else "Remove or downgrade if score drivers weaken, source quality falls, or a better ranked setup replaces it."
                ),
                "short_sale_research_only": best_lane == "Short-Sale Research",
            }
        )
    ranked.sort(key=lambda item: item.get("discovery_score", 0), reverse=True)
    return ranked


def filter_candidates_by_preset(rows, preset):
    rows = rows or []
    if preset == "Long-Term Quality":
        return [row for row in rows if row.get("best_lane") == "Long-Term Buy Research"]
    if preset == "Short-Term Momentum":
        return [row for row in rows if row.get("best_lane") == "Short-Term Buy Research"]
    if preset == "Pullback Watchlist":
        return [row for row in rows if row.get("opportunity_label") in {"Wait", "Watch"}]
    if preset == "High Risk / Avoid":
        return [row for row in rows if row.get("opportunity_label") == "Avoid" or _safe_float(row.get("volatility_pct")) >= 30]
    if preset == "Short-Sale Research":
        return [row for row in rows if row.get("best_lane") == "Short-Sale Research"]
    if preset == "Needs Data":
        return [row for row in rows if row.get("opportunity_label") == "Needs Data" or row.get("recommendation_gate") == "Blocked"]
    return rows


def build_research_data_context(
    selected_symbol,
    period,
    watchlist=None,
    dynamic_rows=None,
    best_opportunity_rows=None,
    paper_positions=None,
    real_holdings=None,
    agent_queue=None,
    manual_symbols=None,
    snapshot=None,
    price_data=None,
    market_timing=None,
    previous_signature="",
    previous_period="",
    last_scan_at="",
):
    """Build the single source-of-truth context passed to primary dashboard panels."""
    dynamic_rows = dynamic_rows or []
    best_opportunity_rows = best_opportunity_rows or []
    selected_symbol = _normalize_symbol(selected_symbol)
    universe_rows = merge_research_universe(
        watchlist=watchlist,
        dynamic_rows=dynamic_rows,
        best_opportunity_rows=best_opportunity_rows,
        paper_positions=paper_positions,
        real_holdings=real_holdings,
        agent_queue=agent_queue,
        manual_symbols=manual_symbols,
        selected_symbol=selected_symbol,
    )
    universe_symbols = [row["symbol"] for row in universe_rows]
    candidate_source_rows = best_opportunity_rows or dynamic_rows
    if not candidate_source_rows:
        candidate_source_rows = [row for row in universe_rows if row.get("origin") in {"selected", "manual", "holding"}]
    candidate_rows = []
    universe_by_symbol = {row.get("symbol"): row for row in universe_rows}
    for row in candidate_source_rows:
        symbol = _normalize_symbol(row.get("symbol") if isinstance(row, dict) else row)
        merged = _merge_row(universe_by_symbol.get(symbol, {}), row if isinstance(row, dict) else {"symbol": symbol})
        candidate_rows.append(merged)
    discovery_rows = rank_discovery_candidates(candidate_rows, market_timing=market_timing)

    data_source_manifest = [
        build_source_manifest_item(selected_symbol, "snapshot", snapshot or {}),
        build_source_manifest_item(selected_symbol, "history", price_data or {}),
    ]
    for row in discovery_rows:
        data_source_manifest.append(row.get("source_manifest", {}))

    signature = _stable_signature(universe_symbols)
    stale_reasons = []
    if previous_period and previous_period != period:
        stale_reasons.append("Period changed since the last shared scan.")
    if previous_signature and previous_signature != signature:
        stale_reasons.append("Universe changed since the last shared scan.")
    if not last_scan_at:
        stale_reasons.append("No dynamic scan timestamp is recorded yet.")
    if not discovery_rows:
        stale_reasons.append("No ranked discovery candidates are available.")

    return {
        "selected_symbol": selected_symbol,
        "universe_rows": universe_rows,
        "universe_symbols": universe_symbols,
        "candidate_rows": candidate_rows,
        "discovery_rows": discovery_rows,
        "scan_period": period,
        "last_scan_at": last_scan_at or _now(),
        "signature": signature,
        "data_source_manifest": data_source_manifest,
        "market_timing": market_timing or {},
        "stale_reason": " ".join(stale_reasons),
        "is_stale": bool(stale_reasons),
        "saved_screens": [{"name": key, "description": value} for key, value in SAVED_SCREEN_PRESETS.items()],
        "source_summary": {
            "total": len(data_source_manifest),
            "blocked": sum(1 for item in data_source_manifest if item.get("recommendation_gate") == "Blocked"),
            "fallback": sum(1 for item in data_source_manifest if item.get("fallback")),
            "research_only": sum(1 for item in data_source_manifest if item.get("allowed_use") == "research_only"),
        },
    }
