def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def generate_strategy_scorecard(paper_performance, benchmark_data, paper_positions=None):
    """Compare simulated paper strategy performance against the best ETF benchmark."""
    paper_performance = paper_performance or {}
    benchmark_data = benchmark_data or {}
    paper_positions = paper_positions or {}

    strategy_return = _safe_float(paper_performance.get("total_unrealized_pnl_pct", 0.0))
    best_benchmark = benchmark_data.get("best_benchmark", {}) or {}
    benchmark_return = _safe_float(best_benchmark.get("return_pct", 0.0))
    alpha_vs_best_etf = round(strategy_return - benchmark_return, 2)
    number_of_trades = int(_safe_float(paper_performance.get("number_of_trades", 0), 0))
    win_rate = _safe_float(paper_performance.get("win_rate", 0.0))

    positions = paper_positions.get("positions", {}) if isinstance(paper_positions, dict) else {}
    avg_position_size = 0.0
    if positions:
        total_market_value = _safe_float(paper_positions.get("market_value", 0.0))
        if total_market_value > 0:
            weights = [
                (_safe_float(info.get("market_value", 0.0)) / total_market_value) * 100
                for info in positions.values()
            ]
            avg_position_size = round(sum(weights) / len(weights), 2)

    if number_of_trades < 3:
        status = "Needs More Data"
        learning_state = "More simulated trades are needed before judging the strategy."
    elif alpha_vs_best_etf > 1:
        status = "Outperforming"
        learning_state = "Paper strategy is ahead of the best ETF benchmark in this sample."
    elif alpha_vs_best_etf < -1:
        status = "Underperforming"
        learning_state = "Paper strategy trails the best ETF benchmark in this sample."
    else:
        status = "Needs More Data"
        learning_state = "Paper strategy is close to benchmark; continue evaluation."

    return {
        "strategy_total_return_pct": round(strategy_return, 2),
        "best_etf_symbol": best_benchmark.get("symbol", "N/A"),
        "best_etf_return_pct": round(benchmark_return, 2),
        "alpha_vs_best_etf_pct": alpha_vs_best_etf,
        "drawdown_pct": 0.0,
        "win_rate": round(win_rate, 2),
        "number_of_trades": number_of_trades,
        "average_position_size_pct": avg_position_size,
        "best_position": paper_performance.get("best_position", "N/A"),
        "worst_position": paper_performance.get("worst_position", "N/A"),
        "status": status,
        "learning_state": learning_state,
        "summary": (
            f"Paper strategy return {strategy_return:+.2f}% vs "
            f"{best_benchmark.get('symbol', 'best ETF')} {benchmark_return:+.2f}%."
        ),
    }
