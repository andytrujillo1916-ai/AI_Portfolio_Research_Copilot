from market_data import get_price_history, get_risk_metrics
from signal_engine import generate_signal


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _extract_close_series(price_data):
    """Return close prices as a simple list of floats."""
    data = price_data.get("data") if isinstance(price_data, dict) else price_data
    if data is None:
        return []

    try:
        if hasattr(data, "__getitem__") and "Close" in data:
            closes = data["Close"]
            return [float(value) for value in closes if value is not None]
    except Exception:
        pass

    if isinstance(data, dict) and "Close" in data:
        return [_safe_float(value) for value in data.get("Close", [])]

    return []


def _window_return_pct(close_series):
    if len(close_series) < 2:
        return 0.0
    start = _safe_float(close_series[0], 0.0)
    end = _safe_float(close_series[-1], 0.0)
    if start <= 0:
        return 0.0
    return ((end - start) / start) * 100


def _slice_to_history(close_series):
    return {"Close": close_series}


def run_walk_forward_validation(
    watchlist,
    research_mode="Balanced",
    train_window_days=60,
    test_window_days=20,
    period="1y",
):
    """Run rolling train/test validation versus SPY benchmark.

    Research-only: this evaluates historical behavior and does not imply
    future performance.
    """
    watchlist = watchlist or []
    train_window_days = max(20, int(train_window_days))
    test_window_days = max(5, int(test_window_days))

    # Load benchmark first; if missing we fail gracefully with an empty report.
    spy_data = get_price_history("SPY", period=period)
    spy_close = _extract_close_series(spy_data)
    total_span = train_window_days + test_window_days
    if len(spy_close) < total_span:
        return {
            "total_windows": 0,
            "win_rate_vs_spy": 0.0,
            "average_alpha_vs_spy": 0.0,
            "best_window": {},
            "worst_window": {},
            "window_results": [],
            "summary": "Not enough SPY data for walk-forward validation.",
        }

    asset_closes = {}
    for symbol in watchlist:
        if symbol == "SPY":
            continue
        try:
            asset_data = get_price_history(symbol, period=period)
            closes = _extract_close_series(asset_data)
            if len(closes) >= total_span:
                asset_closes[symbol] = closes
        except Exception:
            # Continue gracefully if one symbol fails.
            continue

    if not asset_closes:
        return {
            "total_windows": 0,
            "win_rate_vs_spy": 0.0,
            "average_alpha_vs_spy": 0.0,
            "best_window": {},
            "worst_window": {},
            "window_results": [],
            "summary": "No assets had enough history for walk-forward validation.",
        }

    window_results = []
    step = test_window_days
    max_start = len(spy_close) - total_span

    for start in range(0, max_start + 1, step):
        train_start = start
        train_end = start + train_window_days
        test_end = train_end + test_window_days

        ranked_assets = []
        for symbol, close_series in asset_closes.items():
            if len(close_series) < test_end:
                continue

            train_close = close_series[train_start:train_end]
            test_close = close_series[train_end:test_end]
            if len(train_close) < 2 or len(test_close) < 2:
                continue

            risk = get_risk_metrics(_slice_to_history(train_close))
            previous_price = _safe_float(train_close[-2], 0.0)
            current_price = _safe_float(train_close[-1], 0.0)
            change_pct = (
                ((current_price - previous_price) / previous_price) * 100
                if previous_price > 0
                else 0.0
            )
            snapshot = {
                "symbol": symbol,
                "price": current_price,
                "change_pct": round(change_pct, 2),
                "volume": 0,
            }
            signal = generate_signal(
                symbol,
                snapshot,
                risk,
                news_context={"market_sentiment": "Neutral", "event_tags": [], "risk_flags": []},
            )
            ranked_assets.append(
                {
                    "symbol": symbol,
                    "score": _safe_float(signal.get("score", 0.0)),
                    "test_return_pct": _window_return_pct(test_close),
                }
            )

        if not ranked_assets:
            continue

        ranked_assets.sort(key=lambda row: row.get("score", 0.0), reverse=True)
        top_n = max(1, min(5, len(ranked_assets)))
        selected = ranked_assets[:top_n]
        portfolio_return = sum(row.get("test_return_pct", 0.0) for row in selected) / len(selected)

        spy_test_close = spy_close[train_end:test_end]
        spy_return = _window_return_pct(spy_test_close)
        alpha = portfolio_return - spy_return

        window_results.append(
            {
                "window_start_index": train_start,
                "window_end_index": test_end - 1,
                "selected_assets": ", ".join(row["symbol"] for row in selected),
                "portfolio_return_pct": round(portfolio_return, 2),
                "spy_return_pct": round(spy_return, 2),
                "alpha_vs_spy_pct": round(alpha, 2),
                "outperformed_spy": alpha > 0,
                "research_mode": research_mode,
            }
        )

    if not window_results:
        return {
            "total_windows": 0,
            "win_rate_vs_spy": 0.0,
            "average_alpha_vs_spy": 0.0,
            "best_window": {},
            "worst_window": {},
            "window_results": [],
            "summary": "Walk-forward validation could not produce any valid rolling windows.",
        }

    wins = sum(1 for row in window_results if row.get("outperformed_spy"))
    total_windows = len(window_results)
    avg_alpha = sum(row.get("alpha_vs_spy_pct", 0.0) for row in window_results) / total_windows
    best_window = max(window_results, key=lambda row: row.get("alpha_vs_spy_pct", -9999))
    worst_window = min(window_results, key=lambda row: row.get("alpha_vs_spy_pct", 9999))

    return {
        "total_windows": total_windows,
        "win_rate_vs_spy": round((wins / total_windows) * 100, 2),
        "average_alpha_vs_spy": round(avg_alpha, 2),
        "best_window": best_window,
        "worst_window": worst_window,
        "window_results": window_results,
        "summary": (
            f"Walk-forward validation ran {total_windows} rolling windows in {research_mode} mode. "
            "Results are research-only and not guaranteed future performance."
        ),
    }
