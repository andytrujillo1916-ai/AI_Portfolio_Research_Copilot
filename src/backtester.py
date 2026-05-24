"""Simple strategy helpers for backtesting and strategy comparison."""


def _load_pandas():
    try:
        import pandas as pd

        return pd
    except Exception:
        return None


def _normalize_price_data(price_data):
    """Convert supported price_data inputs into a pandas DataFrame."""
    pd = _load_pandas()
    if pd is None:
        return None

    if isinstance(price_data, dict) and "data" in price_data:
        data = price_data.get("data")
        if hasattr(data, "set_index"):
            df = data
        elif isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = None
    elif hasattr(price_data, "set_index"):
        df = price_data
    elif isinstance(price_data, dict) and "Close" in price_data:
        df = pd.DataFrame(price_data)
    else:
        df = None

    if df is None:
        return None

    if "Close" not in df.columns:
        df = df.copy()
        df.columns = ["Close"] + list(df.columns[1:])

    df = df.dropna(subset=["Close"]).copy()
    if "Date" in df.columns:
        try:
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date").reset_index(drop=True)
        except Exception:
            pass

    return df


def _rolling_mean(close, window):
    pd = _load_pandas()
    if pd is None:
        return None
    return close.rolling(window=window, min_periods=1).mean()


def _strategy_metrics(close, position, df):
    """Calculate return, drawdown, and signal changes for a position series."""
    daily_returns = close.pct_change().fillna(0)
    strat_daily = daily_returns * position.shift(1).fillna(0)
    strategy_cum = (1 + strat_daily).cumprod()

    return_pct = round((strategy_cum.iloc[-1] - 1) * 100, 2)
    peak = strategy_cum.cummax()
    max_drawdown_pct = round((strategy_cum / peak - 1).min() * 100, 2)
    signal_changes = int(position.diff().abs().fillna(0).sum())

    return {
        "return_pct": return_pct,
        "max_drawdown_pct": max_drawdown_pct,
        "signal_changes": signal_changes,
        "equity_curve": strategy_cum,
    }


def _build_equity_curve(df, close, strategy_cum, strategy_name):
    pd = _load_pandas()
    if pd is None:
        return None

    equity_df = pd.DataFrame()
    if "Date" in df.columns:
        equity_df["Date"] = pd.to_datetime(df["Date"]).reset_index(drop=True)
    else:
        equity_df["Date"] = pd.Series(range(len(close)))

    equity_df["Buy and Hold"] = (close / close.iloc[0] * 100).reset_index(drop=True)
    equity_df[strategy_name] = (strategy_cum * 100).reset_index(drop=True)
    return equity_df


def _strategy_result(strategy_name, close, position, df):
    metrics = _strategy_metrics(close, position, df)
    return {
        "strategy_name": strategy_name,
        "return_pct": metrics["return_pct"],
        "max_drawdown_pct": metrics["max_drawdown_pct"],
        "signal_changes": metrics["signal_changes"],
        "equity_curve": _build_equity_curve(df, close, metrics["equity_curve"], strategy_name),
    }


def _buy_and_hold_strategy(close, df):
    position = close.apply(lambda value: 1)
    return _strategy_result("Buy & Hold", close, position, df)


def _sma_trend_strategy(close, df, window):
    sma = _rolling_mean(close, window)
    if sma is None:
        return _strategy_result(f"SMA{window} Trend", close, close.apply(lambda value: 1), df)
    position = (close > sma).astype(int)
    return _strategy_result(f"SMA{window} Trend", close, position, df)


def _sma_crossover_strategy(close, df, fast_window, slow_window):
    fast_sma = _rolling_mean(close, fast_window)
    slow_sma = _rolling_mean(close, slow_window)
    if fast_sma is None or slow_sma is None:
        return _strategy_result(
            f"SMA{fast_window}/SMA{slow_window} Crossover",
            close,
            close.apply(lambda value: 1),
            df,
        )
    position = (fast_sma > slow_sma).astype(int)
    return _strategy_result(f"SMA{fast_window}/SMA{slow_window} Crossover", close, position, df)


def _momentum_strategy(close, df, lookback=10):
    momentum = close.pct_change(lookback).fillna(0)
    position = (momentum > 0).astype(int)
    return _strategy_result("Momentum (10-day positive return)", close, position, df)


def run_strategy_lab(price_data):
    """Run the simple strategy lab and compare the results."""
    df = _normalize_price_data(price_data)
    if df is None:
        return {
            "best_strategy": "Buy & Hold",
            "worst_strategy": "Buy & Hold",
            "strategy_results": [],
        }

    close = df["Close"].astype(float)
    n = len(close)
    if n < 2:
        return {
            "best_strategy": "Buy & Hold",
            "worst_strategy": "Buy & Hold",
            "strategy_results": [],
        }

    results = [
        _buy_and_hold_strategy(close, df),
        _sma_trend_strategy(close, df, 20),
        _sma_trend_strategy(close, df, 50),
        _sma_crossover_strategy(close, df, 20, 50),
        _momentum_strategy(close, df, 10),
    ]

    ranked = sorted(results, key=lambda item: item["return_pct"], reverse=True)
    return {
        "best_strategy": ranked[0]["strategy_name"] if ranked else "Buy & Hold",
        "worst_strategy": ranked[-1]["strategy_name"] if ranked else "Buy & Hold",
        "strategy_results": results,
    }


def run_walk_forward_test(price_data, window_size=30):
    """Run a simple sequential walk-forward test using Strategy Lab on each window."""
    df = _normalize_price_data(price_data)
    if df is None:
        return {
            "total_windows": 0,
            "strategy_win_counts": {},
            "average_return_by_strategy": {},
            "most_consistent_strategy": "N/A",
        }

    if "Close" not in df.columns:
        return {
            "total_windows": 0,
            "strategy_win_counts": {},
            "average_return_by_strategy": {},
            "most_consistent_strategy": "N/A",
        }

    window_size = max(int(window_size), 2)
    total_rows = len(df)
    if total_rows < window_size:
        return {
            "total_windows": 0,
            "strategy_win_counts": {},
            "average_return_by_strategy": {},
            "most_consistent_strategy": "N/A",
        }

    total_windows = total_rows // window_size
    win_counts = {}
    returns_by_strategy = {}

    for window_index in range(total_windows):
        start = window_index * window_size
        end = start + window_size
        window_df = df.iloc[start:end].copy()
        window_results = run_strategy_lab(window_df)
        window_strategies = window_results.get("strategy_results", [])
        if not window_strategies:
            continue

        winner = window_results.get("best_strategy", "Unknown")
        win_counts[winner] = win_counts.get(winner, 0) + 1

        for entry in window_strategies:
            name = entry.get("strategy_name", "Unknown")
            returns_by_strategy.setdefault(name, []).append(entry.get("return_pct", 0.0))

    average_return_by_strategy = {
        name: round(sum(values) / len(values), 2)
        for name, values in returns_by_strategy.items()
    }

    if win_counts:
        most_consistent_strategy = sorted(
            win_counts.items(),
            key=lambda item: (
                item[1],
                average_return_by_strategy.get(item[0], 0.0),
            ),
            reverse=True,
        )[0][0]
    else:
        most_consistent_strategy = "N/A"

    return {
        "total_windows": total_windows,
        "strategy_win_counts": win_counts,
        "average_return_by_strategy": average_return_by_strategy,
        "most_consistent_strategy": most_consistent_strategy,
    }


def run_simple_backtest(price_data):
    """Run a simple backtest using Close prices and preserve existing output."""
    df = _normalize_price_data(price_data)
    if df is None:
        return {
            "buy_and_hold_return_pct": 0.0,
            "strategy_return_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "number_of_signal_changes": 0,
        }

    close = df["Close"].astype(float)
    n = len(close)
    if n < 2:
        return {
            "buy_and_hold_return_pct": 0.0,
            "strategy_return_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "number_of_signal_changes": 0,
        }

    buy_and_hold = _buy_and_hold_strategy(close, df)
    sma20 = _sma_trend_strategy(close, df, 20)

    return {
        "buy_and_hold_return_pct": round(buy_and_hold["return_pct"], 2),
        "strategy_return_pct": round(sma20["return_pct"], 2),
        "max_drawdown_pct": round(sma20["max_drawdown_pct"], 2),
        "number_of_signal_changes": int(sma20["signal_changes"]),
        "equity_curve": _build_equity_curve(df, close, _strategy_metrics(close, (close > _rolling_mean(close, 20)).astype(int), df)["equity_curve"], "Strategy"),
    }
