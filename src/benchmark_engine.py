def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def compare_to_benchmarks(portfolio_returns, benchmark_data):
    """Compare research portfolio returns to major passive benchmark baselines."""
    portfolio_returns = portfolio_returns or {}
    benchmark_data = benchmark_data or {}

    portfolio_return = _safe_float(
        portfolio_returns.get("total_unrealized_pnl_pct", portfolio_returns.get("return_pct", 0.0))
    )
    portfolio_vol = _safe_float(portfolio_returns.get("volatility_pct", 0.0))
    portfolio_drawdown = _safe_float(portfolio_returns.get("drawdown_pct", 0.0))
    portfolio_sharpe = (
        portfolio_return / portfolio_vol if portfolio_vol else _safe_float(portfolio_returns.get("sharpe", 0.0))
    )

    rows = []
    for row in benchmark_data.get("benchmarks", []):
        name = str(row.get("benchmark", ""))
        if name in {"SPY", "VTI", "QQQ", "60/40 basket"}:
            rows.append(
                {
                    "name": name,
                    "return_pct": _safe_float(row.get("return_pct", 0.0)),
                    "volatility_pct": _safe_float(row.get("volatility_pct", 0.0)),
                    "max_drawdown_pct": _safe_float(row.get("max_drawdown_pct", 0.0)),
                    "sharpe": _safe_float(row.get("sharpe", 0.0)),
                }
            )

    if rows:
        equal_weight_return = sum(row["return_pct"] for row in rows) / len(rows)
        equal_weight_vol = sum(row["volatility_pct"] for row in rows) / len(rows)
        equal_weight_dd = sum(row["max_drawdown_pct"] for row in rows) / len(rows)
        equal_weight_sharpe = equal_weight_return / equal_weight_vol if equal_weight_vol else 0.0
        rows.append(
            {
                "name": "Equal Weight Basket",
                "return_pct": round(equal_weight_return, 2),
                "volatility_pct": round(equal_weight_vol, 2),
                "max_drawdown_pct": round(equal_weight_dd, 2),
                "sharpe": round(equal_weight_sharpe, 2),
            }
        )

    if not rows:
        return {
            "best_benchmark": "N/A",
            "ai_outperformance_pct": 0.0,
            "volatility_comparison": "No benchmark volatility data.",
            "drawdown_comparison": "No benchmark drawdown data.",
            "sharpe_comparison": "No benchmark sharpe data.",
            "verdict": "Needs More Data",
            "summary": "Benchmark Truth Engine could not compare because benchmark inputs were empty.",
        }

    best = max(rows, key=lambda row: row.get("return_pct", 0.0))
    ai_outperformance = portfolio_return - _safe_float(best.get("return_pct", 0.0))

    avg_benchmark_vol = sum(row["volatility_pct"] for row in rows) / len(rows)
    avg_benchmark_dd = sum(row["max_drawdown_pct"] for row in rows) / len(rows)
    avg_benchmark_sharpe = sum(row["sharpe"] for row in rows) / len(rows)

    volatility_comparison = (
        "AI portfolio volatility is lower than benchmark set average."
        if portfolio_vol and portfolio_vol < avg_benchmark_vol
        else "AI portfolio volatility is at or above benchmark set average."
    )
    drawdown_comparison = (
        "AI drawdown profile is better (shallower) than benchmark set average."
        if portfolio_drawdown and portfolio_drawdown > avg_benchmark_dd
        else "AI drawdown profile is similar/worse versus benchmark set average."
    )
    sharpe_comparison = (
        "AI risk-adjusted return is stronger than benchmark set average."
        if portfolio_sharpe > avg_benchmark_sharpe
        else "AI risk-adjusted return trails benchmark set average."
    )

    if ai_outperformance > 1:
        verdict = "Outperforming"
    elif ai_outperformance < -1:
        verdict = "Underperforming"
    else:
        verdict = "Near Benchmark"

    return {
        "best_benchmark": best.get("name", "N/A"),
        "ai_outperformance_pct": round(ai_outperformance, 2),
        "volatility_comparison": volatility_comparison,
        "drawdown_comparison": drawdown_comparison,
        "sharpe_comparison": sharpe_comparison,
        "verdict": verdict,
        "summary": (
            f"AI portfolio return {portfolio_return:+.2f}% vs best benchmark "
            f"{best.get('name', 'N/A')} {_safe_float(best.get('return_pct', 0.0)):+.2f}%."
        ),
    }
