from market_data import get_price_history, get_risk_metrics


DEFAULT_STRESS_PROXIES = {
    "SPY": "Broad market",
    "QQQ": "Growth/technology",
    "IWM": "Small caps",
    "VTI": "Total US market",
    "SCHD": "Dividend/value",
    "TLT": "Long-duration Treasuries",
    "HYG": "High-yield credit",
    "GLD": "Gold",
    "^VIX": "Volatility index",
}

RESEARCH_ONLY_DISCLAIMER = (
    "Crash Watch is hypothesis testing only. It does not predict a crash, guarantee outcomes, "
    "place trades, connect to brokers, or replace human research."
)


def _safe_float(value, default=0.0):
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _extract_close_values(price_data):
    data = price_data.get("data") if isinstance(price_data, dict) else price_data
    if hasattr(data, "columns"):
        if "Close" in data.columns:
            return [_safe_float(value) for value in data["Close"].tolist()]
        if len(data.columns) > 0:
            return [_safe_float(value) for value in data.iloc[:, -1].tolist()]
    if isinstance(data, dict):
        close = data.get("Close")
        if close is None:
            close_key = next((key for key in data if key != "Date"), None)
            close = data.get(close_key, [])
        return [_safe_float(value) for value in close]
    if isinstance(data, list):
        return [_safe_float(value) for value in data]
    return []


def _trend_status(close_values):
    if len(close_values) < 5:
        return "Needs More Data"
    last = close_values[-1]
    short_window = close_values[-10:] if len(close_values) >= 10 else close_values
    long_window = close_values[-30:] if len(close_values) >= 30 else close_values
    short_avg = sum(short_window) / len(short_window)
    long_avg = sum(long_window) / len(long_window)
    if last < short_avg < long_avg:
        return "Deteriorating"
    if last >= short_avg >= long_avg:
        return "Constructive"
    return "Mixed"


def _row_stress_points(row):
    points = 0
    drawdown = _safe_float(row.get("max_drawdown_pct"))
    volatility = _safe_float(row.get("volatility_pct"))
    return_pct = _safe_float(row.get("return_pct"))
    if drawdown <= -20:
        points += 18
    elif drawdown <= -10:
        points += 10
    if volatility >= 35:
        points += 14
    elif volatility >= 25:
        points += 8
    if return_pct <= -8:
        points += 10
    elif return_pct < 0:
        points += 5
    if row.get("trend_status") == "Deteriorating":
        points += 8
    return points


def _risk_posture(score, rows):
    valid_rows = [row for row in rows if row.get("source") != "error"]
    if len(valid_rows) < 3:
        return "Needs More Data"
    if score >= 55:
        return "Stress"
    if score >= 25:
        return "Elevated"
    return "Normal"


def analyze_market_stress(period="3mo", proxy_symbols=None, price_history_loader=None):
    """Analyze broad market stress with ETFs/proxies only.

    This is research-only crash-risk context. It is intentionally simple and
    uses proxies before any direct futures or leveraged instrument logic.
    """
    proxies = proxy_symbols or DEFAULT_STRESS_PROXIES
    loader = price_history_loader or get_price_history
    rows = []

    for symbol, role in proxies.items():
        try:
            history = loader(symbol, period=period)
            risk = get_risk_metrics(history.get("data") if isinstance(history, dict) else history)
            close_values = _extract_close_values(history)
            source = history.get("source", "unknown") if isinstance(history, dict) else "unknown"
            is_fallback = bool(history.get("is_fallback") or source == "mock") if isinstance(history, dict) else False
            rows.append(
                {
                    "symbol": symbol,
                    "role": role,
                    "return_pct": risk.get("return_pct", 0.0),
                    "volatility_pct": risk.get("volatility_pct", 0.0),
                    "max_drawdown_pct": risk.get("max_drawdown_pct", 0.0),
                    "trend_status": _trend_status(close_values),
                    "source": source,
                    "is_fallback": is_fallback,
                    "error": history.get("error", "") if isinstance(history, dict) else "",
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "symbol": symbol,
                    "role": role,
                    "return_pct": 0.0,
                    "volatility_pct": 0.0,
                    "max_drawdown_pct": 0.0,
                    "trend_status": "Needs More Data",
                    "source": "error",
                    "is_fallback": False,
                    "error": str(exc),
                }
            )

    risk_on_symbols = {"SPY", "QQQ", "IWM", "VTI", "SCHD"}
    risk_on_rows = [row for row in rows if row.get("symbol") in risk_on_symbols]
    constructive = [
        row
        for row in risk_on_rows
        if _safe_float(row.get("return_pct")) > 0 and row.get("trend_status") != "Deteriorating"
    ]
    breadth_pct = round((len(constructive) / len(risk_on_rows)) * 100, 2) if risk_on_rows else 0.0

    spy = next((row for row in rows if row.get("symbol") == "SPY"), {})
    defensive_rows = [row for row in rows if row.get("symbol") in {"TLT", "GLD"}]
    defensive_return = (
        sum(_safe_float(row.get("return_pct")) for row in defensive_rows) / len(defensive_rows)
        if defensive_rows
        else 0.0
    )
    defensive_rotation = defensive_return > _safe_float(spy.get("return_pct")) + 2

    hyg = next((row for row in rows if row.get("symbol") == "HYG"), {})
    vix = next((row for row in rows if row.get("symbol") == "^VIX"), {})
    deteriorating_count = sum(1 for row in risk_on_rows if row.get("trend_status") == "Deteriorating")
    fallback_count = sum(1 for row in rows if row.get("is_fallback") or row.get("source") in {"mock", "error"})

    stress_score = sum(_row_stress_points(row) for row in risk_on_rows)
    if breadth_pct < 40:
        stress_score += 15
    elif breadth_pct < 60:
        stress_score += 8
    if defensive_rotation:
        stress_score += 8
    if _safe_float(hyg.get("return_pct")) < -3 or _safe_float(hyg.get("max_drawdown_pct")) <= -6:
        stress_score += 10
    if _safe_float(vix.get("return_pct")) > 15:
        stress_score += 10
    stress_score = min(100, round(stress_score, 2))
    posture = _risk_posture(stress_score, rows)

    if posture == "Stress":
        interpretation = "Multiple proxy indicators show stress. Treat crash talk as a hypothesis that needs evidence and risk review."
    elif posture == "Elevated":
        interpretation = "Some proxy indicators are weakening. Research should emphasize drawdown, breadth, and benchmark checks."
    elif posture == "Normal":
        interpretation = "Broad proxy evidence does not show major stress in this sample, though conditions can change quickly."
    else:
        interpretation = "There is not enough reliable proxy data to evaluate broad market stress."

    return {
        "risk_posture": posture,
        "stress_score": stress_score,
        "breadth_pct": breadth_pct,
        "deteriorating_count": deteriorating_count,
        "defensive_rotation": defensive_rotation,
        "credit_risk_proxy": "Weakening" if _safe_float(hyg.get("return_pct")) < 0 else "Stable",
        "volatility_proxy": "Rising" if _safe_float(vix.get("return_pct")) > 0 else "Stable/Unavailable",
        "fallback_count": fallback_count,
        "rows": rows,
        "interpretation": interpretation,
        "disclaimer": RESEARCH_ONLY_DISCLAIMER,
    }
