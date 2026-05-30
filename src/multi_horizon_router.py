def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, value))


FUTURES_PROXY_SYMBOLS = {
    "SPY": "S&P 500 futures proxy",
    "QQQ": "Nasdaq futures proxy",
    "IWM": "Russell 2000 futures proxy",
    "DIA": "Dow futures proxy",
    "GLD": "Gold futures proxy",
    "SLV": "Silver futures proxy",
    "USO": "Crude oil futures proxy",
    "UNG": "Natural gas futures proxy",
    "TLT": "Treasury duration proxy",
    "IEF": "Intermediate Treasury proxy",
    "UUP": "US dollar proxy",
    "XLE": "Energy sector proxy",
    "XLF": "Financial sector proxy",
    "XLK": "Technology sector proxy",
}


def _entry_state(best_score, gate, volatility, drawdown, market_risk_level=""):
    if gate == "Blocked":
        return "Needs Data"
    if best_score < 40:
        return "Avoid"
    if market_risk_level == "High" and best_score >= 60:
        return "Wait for Pullback"
    if volatility >= 35 or drawdown >= 20:
        return "Wait for Pullback" if best_score >= 50 else "Watch"
    if best_score >= 72:
        return "Buy Candidate"
    if best_score >= 55:
        return "Watch"
    return "Watch"


def route_multi_horizon_opportunity(
    symbol,
    signal_data,
    risk,
    fundamentals,
    catalysts,
    accuracy_context,
    profile,
):
    """Score short-term, long-term, and futures-proxy opportunity lanes."""
    symbol = str(symbol or "").upper()
    signal_data = signal_data or {}
    risk = risk or {}
    fundamentals = fundamentals or {}
    catalysts = catalysts or {}
    accuracy_context = accuracy_context or {}
    profile = profile or {}

    signal_score = _safe_float(signal_data.get("score"), 50.0)
    volatility = _safe_float(risk.get("volatility_pct"), 0.0)
    drawdown = abs(_safe_float(risk.get("max_drawdown_pct"), 0.0))
    return_pct = _safe_float(risk.get("return_pct"), 0.0)
    fundamental_score = _safe_float(fundamentals.get("fundamental_score"), 50.0)
    accuracy_adjustment = _safe_float(accuracy_context.get("confidence_adjustment"), 0.0)
    risk_tolerance = str(profile.get("risk_tolerance", "Moderate"))
    catalyst_count = len(catalysts.get("catalysts", []) or [])
    gate = signal_data.get("recommendation_gate", "Warning")
    market_risk_level = str(signal_data.get("market_risk_level", ""))

    short_term = signal_score + min(return_pct, 12) - (volatility * 0.7) - (drawdown * 0.2)
    swing = signal_score + (catalyst_count * 2) + min(return_pct, 10) - (volatility * 0.35) - (drawdown * 0.25)
    long_term = (signal_score * 0.45) + (fundamental_score * 0.45) - (drawdown * 0.25)
    futures_proxy = (signal_score * 0.5) + (max(0.0, 100 - volatility * 1.4) * 0.25) - (drawdown * 0.15)
    futures_proxy += 16 if symbol in FUTURES_PROXY_SYMBOLS else -20

    if risk_tolerance == "Low":
        short_term -= 10
        swing -= 4
        futures_proxy -= 4
    elif risk_tolerance == "High":
        short_term += 3
        swing += 2
        futures_proxy += 2

    short_term += accuracy_adjustment
    swing += accuracy_adjustment
    long_term += accuracy_adjustment * 0.5
    futures_proxy += accuracy_adjustment * 0.5

    blocked = []
    if volatility >= 35 or drawdown >= 20:
        blocked.append("Short-term action blocked by high volatility or drawdown.")
        short_term = min(short_term, 39)
    if gate == "Blocked":
        blocked.append("All action lanes blocked by data quality.")
        short_term = min(short_term, 35)
        swing = min(swing, 35)
        long_term = min(long_term, 35)
        futures_proxy = min(futures_proxy, 35)

    horizons = [
        {
            "horizon": "Short-term",
            "lane": "Short Term",
            "score": round(_clamp(short_term), 1),
            "expected_holding_period": "Days to 2 weeks",
            "reasoning": "Fast setup uses signal strength but penalizes volatility heavily.",
        },
        {
            "horizon": "Swing",
            "lane": "Short Term",
            "score": round(_clamp(swing), 1),
            "expected_holding_period": "2-12 weeks",
            "reasoning": "Default action horizon balances signal, catalyst context, and risk.",
        },
        {
            "horizon": "Long-term",
            "lane": "Long Term",
            "score": round(_clamp(long_term), 1),
            "expected_holding_period": "1-5 years",
            "reasoning": "Long-term setup weights fundamentals and drawdown control.",
        },
        {
            "horizon": "Futures Proxy",
            "lane": "Futures Proxy",
            "score": round(_clamp(futures_proxy), 1),
            "expected_holding_period": "Days to 3 months",
            "reasoning": "Proxy lane uses ETF/market instruments only; no direct futures, margin, or leverage.",
        },
    ]
    horizons.sort(key=lambda row: row["score"], reverse=True)
    best = horizons[0]
    if symbol in FUTURES_PROXY_SYMBOLS and gate != "Blocked":
        best = next(row for row in horizons if row["lane"] == "Futures Proxy")

    if best["score"] >= 70:
        confidence = "High"
    elif best["score"] >= 55:
        confidence = "Moderate"
    else:
        confidence = "Low"

    entry_state = _entry_state(
        best["score"],
        gate,
        volatility,
        drawdown,
        market_risk_level=market_risk_level,
    )

    return {
        "symbol": symbol,
        "best_horizon": best["horizon"],
        "best_lane": "Needs Data" if gate == "Blocked" else best["lane"],
        "best_score": best["score"],
        "short_term_score": round(_clamp(max(short_term, swing)), 1),
        "long_term_score": round(_clamp(long_term), 1),
        "futures_proxy_score": round(_clamp(futures_proxy), 1),
        "entry_state": entry_state,
        "confidence_level": confidence,
        "expected_holding_period": best["expected_holding_period"],
        "best_holding_period": best["expected_holding_period"],
        "horizon_scores": horizons,
        "blocked_reasons": blocked,
        "why": [
            best["reasoning"],
            f"Accuracy adjustment applied: {accuracy_adjustment:+.1f}.",
            f"Fundamental score: {fundamental_score:.1f}; signal score: {signal_score:.1f}.",
            "Futures remain proxy-only through ETFs or broad market instruments.",
        ],
        "summary": (
            f"{symbol} best opportunity lane is {'Needs Data' if gate == 'Blocked' else best['lane']} "
            f"({best['horizon']}) with {confidence.lower()} confidence."
        ),
    }
