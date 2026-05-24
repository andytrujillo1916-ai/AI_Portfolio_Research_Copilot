from market_data import get_price_history, get_risk_metrics


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _extract_risk(price_data):
    risk_input = price_data.get("data") if isinstance(price_data, dict) else price_data
    return get_risk_metrics(risk_input)


def analyze_alpha_vs_benchmark(
    asset_symbol,
    asset_price_data,
    paper_trade_results=None,
    benchmark_symbol="SPY",
    period="1mo",
):
    """Compare asset research performance vs benchmark with simple transparent metrics."""
    asset_risk = _extract_risk(asset_price_data)
    benchmark_price_data = get_price_history(benchmark_symbol, period=period)
    benchmark_risk = _extract_risk(benchmark_price_data)

    asset_return_pct = _safe_float(asset_risk.get("return_pct", 0.0))
    benchmark_return_pct = _safe_float(benchmark_risk.get("return_pct", 0.0))
    asset_volatility = _safe_float(asset_risk.get("volatility_pct", 0.0))
    benchmark_volatility = _safe_float(benchmark_risk.get("volatility_pct", 0.0))
    asset_drawdown = _safe_float(asset_risk.get("max_drawdown_pct", 0.0))
    benchmark_drawdown = _safe_float(benchmark_risk.get("max_drawdown_pct", 0.0))

    alpha_pct = round(asset_return_pct - benchmark_return_pct, 2)
    volatility_gap = round(asset_volatility - benchmark_volatility, 2)
    drawdown_gap = round(asset_drawdown - benchmark_drawdown, 2)

    if alpha_pct > 1:
        outperformance_status = "Outperforming"
    elif alpha_pct < -1:
        outperformance_status = "Underperforming"
    else:
        outperformance_status = "Neutral"

    if alpha_pct > 0 and drawdown_gap >= 0:
        relative_strength = "Strong"
    elif alpha_pct > 0 and drawdown_gap < 0:
        relative_strength = "Moderate"
    elif alpha_pct <= 0 and drawdown_gap >= 0:
        relative_strength = "Weak"
    else:
        relative_strength = "Mixed"

    summary = (
        f"{asset_symbol} vs {benchmark_symbol}: alpha {alpha_pct:+.2f}%, "
        f"volatility gap {volatility_gap:+.2f}%, drawdown gap {drawdown_gap:+.2f}%."
    )
    if paper_trade_results:
        summary += " Paper-trade context can be reviewed alongside this benchmark comparison."

    return {
        "benchmark_symbol": benchmark_symbol,
        "asset_return_pct": round(asset_return_pct, 2),
        "benchmark_return_pct": round(benchmark_return_pct, 2),
        "alpha_pct": alpha_pct,
        "volatility_gap": volatility_gap,
        "drawdown_gap": drawdown_gap,
        "relative_strength": relative_strength,
        "outperformance_status": outperformance_status,
        "summary": summary,
    }
