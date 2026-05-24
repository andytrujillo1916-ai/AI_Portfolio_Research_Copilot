from market_data import get_price_history, get_risk_metrics


DEFAULT_BENCHMARK_BASKET = ["SPY", "QQQ", "VOO", "IWM", "DIA"]


def find_best_etf_benchmark(period="1mo", benchmark_symbols=None, price_history_loader=None):
    """Pick the strongest ETF benchmark over the same research period."""
    symbols = benchmark_symbols or DEFAULT_BENCHMARK_BASKET
    loader = price_history_loader or get_price_history
    rows = []

    for symbol in symbols:
        try:
            price_data = loader(symbol, period=period)
            risk_input = price_data.get("data") if isinstance(price_data, dict) else price_data
            risk = get_risk_metrics(risk_input)
            rows.append(
                {
                    "symbol": symbol,
                    "return_pct": risk.get("return_pct", 0.0),
                    "volatility_pct": risk.get("volatility_pct", 0.0),
                    "max_drawdown_pct": risk.get("max_drawdown_pct", 0.0),
                    "source": price_data.get("source", "unknown") if isinstance(price_data, dict) else "unknown",
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "symbol": symbol,
                    "return_pct": 0.0,
                    "volatility_pct": 0.0,
                    "max_drawdown_pct": 0.0,
                    "source": "error",
                    "error": str(exc),
                }
            )

    ranked = sorted(rows, key=lambda row: row.get("return_pct", 0.0), reverse=True)
    best = ranked[0] if ranked else {}
    return {
        "benchmark_basket": ranked,
        "best_benchmark": best,
        "summary": (
            f"Best ETF benchmark is {best.get('symbol', 'N/A')} "
            f"with {best.get('return_pct', 0.0):+.2f}% return over {period}."
            if best
            else "No benchmark ETF data available."
        ),
    }
