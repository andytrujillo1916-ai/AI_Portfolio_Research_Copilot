def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _strategy_strength(score):
    if score >= 70:
        return "High"
    if score >= 50:
        return "Medium"
    return "Low"


def _mode_adjustment(research_mode):
    if research_mode == "Conservative":
        return {"momentum": -6, "trend": -2, "mean_reversion": -1, "defensive": 8, "benchmark": 3}
    if research_mode == "Aggressive":
        return {"momentum": 6, "trend": 4, "mean_reversion": 2, "defensive": -4, "benchmark": -2}
    return {"momentum": 0, "trend": 0, "mean_reversion": 0, "defensive": 0, "benchmark": 0}


def compare_strategies(
    price_data,
    risk,
    regime_data,
    signal_data,
    research_mode="Balanced",
):
    """Compare simple strategy styles for research-only decision support."""
    risk = risk or {}
    regime_data = regime_data or {}
    signal_data = signal_data or {}
    mode = _mode_adjustment(research_mode)

    ret = _safe_float(risk.get("return_pct", 0.0))
    vol = _safe_float(risk.get("volatility_pct", 0.0))
    drawdown = abs(_safe_float(risk.get("max_drawdown_pct", 0.0)))
    score = _safe_float(signal_data.get("score", 50.0))
    signal_label = str(signal_data.get("signal", "Watch"))
    regime = str(regime_data.get("regime", "Unknown"))

    trend_favorable = regime in {"Bull Trend", "Recovery"}
    caution_regime = regime == "Bear Trend"
    positive_signal = signal_label in {"Strong Watch", "Watch"}
    weak_signal = signal_label in {"Caution", "Avoid"}

    momentum_score = 50
    if ret > 0:
        momentum_score += 15
    if positive_signal:
        momentum_score += 15
    if trend_favorable:
        momentum_score += 10
    if vol > 35:
        momentum_score -= 8
    momentum_score += mode["momentum"]

    trend_score = 50
    if trend_favorable:
        trend_score += 18
    if drawdown < 15:
        trend_score += 12
    if ret > 0:
        trend_score += 8
    if caution_regime:
        trend_score -= 12
    trend_score += mode["trend"]

    mean_rev_score = 50
    if ret < 0:
        mean_rev_score += 15
    if drawdown < 25:
        mean_rev_score += 8
    if not weak_signal:
        mean_rev_score += 8
    if drawdown > 35:
        mean_rev_score -= 15
    mean_rev_score += mode["mean_reversion"]

    defensive_score = 50
    if vol < 25:
        defensive_score += 15
    if weak_signal:
        defensive_score += 12
    if caution_regime:
        defensive_score += 10
    if ret > 0 and trend_favorable:
        defensive_score -= 8
    defensive_score += mode["defensive"]

    benchmark_score = 50
    if abs(ret) < 8:
        benchmark_score += 10
    if vol < 28:
        benchmark_score += 8
    if score < 55:
        benchmark_score += 8
    if score > 70 and trend_favorable:
        benchmark_score -= 8
    benchmark_score += mode["benchmark"]

    strategy_rows = [
        {
            "strategy_name": "Momentum Strategy",
            "strategy_score": max(0, min(100, round(momentum_score, 1))),
            "best_use_case": "When returns and signals are positive with trend support.",
            "reasoning": f"Return {ret:+.2f}%, signal {signal_label}, regime {regime}.",
        },
        {
            "strategy_name": "Trend Following Strategy",
            "strategy_score": max(0, min(100, round(trend_score, 1))),
            "best_use_case": "When regime is Bull Trend/Recovery with stable drawdowns.",
            "reasoning": f"Regime {regime}, drawdown {drawdown:.2f}%, return {ret:+.2f}%.",
        },
        {
            "strategy_name": "Mean Reversion Strategy",
            "strategy_score": max(0, min(100, round(mean_rev_score, 1))),
            "best_use_case": "When recent weakness may allow rebound without deep breakdown.",
            "reasoning": f"Return {ret:+.2f}%, drawdown {drawdown:.2f}%, signal {signal_label}.",
        },
        {
            "strategy_name": "Defensive Strategy",
            "strategy_score": max(0, min(100, round(defensive_score, 1))),
            "best_use_case": "When caution is warranted and volatility control matters.",
            "reasoning": f"Volatility {vol:.2f}%, signal {signal_label}, regime {regime}.",
        },
        {
            "strategy_name": "Benchmark Hold Strategy",
            "strategy_score": max(0, min(100, round(benchmark_score, 1))),
            "best_use_case": "When active signals are mixed and passive exposure is acceptable.",
            "reasoning": f"Signal score {score:.1f}, return {ret:+.2f}%, volatility {vol:.2f}%.",
        },
    ]

    for row in strategy_rows:
        row["strength"] = _strategy_strength(row["strategy_score"])

    ranked = sorted(strategy_rows, key=lambda row: row["strategy_score"], reverse=True)
    best_strategy = ranked[0]
    worst_strategy = ranked[-1]

    if trend_favorable and vol < 30:
        market_fit = "Current environment favors directional strategies with controlled risk."
    elif caution_regime or vol >= 35:
        market_fit = "Current environment leans defensive and risk-managed styles."
    else:
        market_fit = "Current environment is mixed; balanced strategy selection is preferred."

    summary = (
        f"{research_mode} strategy comparison: best is {best_strategy['strategy_name']} "
        f"({best_strategy['strategy_score']}/100)."
    )

    return {
        "strategies": ranked,
        "best_strategy": best_strategy,
        "worst_strategy": worst_strategy,
        "market_fit": market_fit,
        "summary": summary,
    }
