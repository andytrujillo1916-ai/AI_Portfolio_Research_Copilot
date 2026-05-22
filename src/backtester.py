def run_simple_backtest(price_data):
    """Run a simple backtest using Close prices.

    Strategy: buy-and-hold vs SMA(20) rule:
      - in market when Close > SMA20
      - out of market when Close <= SMA20

    Accepts a pandas DataFrame-like object with a "Close" column,
    or a dict/structure returned by the existing `get_price_history`.
    Returns a dict with:
      - buy_and_hold_return_pct
      - strategy_return_pct
      - max_drawdown_pct
      - number_of_signal_changes
    """
    try:
        import pandas as pd
    except Exception:
        pd = None

    # Normalize input to a pandas Series of closes
    closes = None
    if isinstance(price_data, dict) and "data" in price_data:
        data = price_data.get("data")
        if hasattr(data, "set_index"):
            df = data
        elif isinstance(data, dict):
            df = pd.DataFrame(data) if pd else None
        else:
            df = None
    elif hasattr(price_data, "set_index"):
        df = price_data
    elif isinstance(price_data, dict) and "Close" in price_data:
        df = pd.DataFrame(price_data) if pd else None
    else:
        df = None

    if df is None:
        return {
            "buy_and_hold_return_pct": 0.0,
            "strategy_return_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "number_of_signal_changes": 0,
        }

    # Ensure Close column
    if "Close" not in df.columns:
        # Try first column
        df = df.copy()
        df.columns = ["Close"] + list(df.columns[1:])
    df = df.dropna(subset=["Close"]).copy()
    if "Date" in df.columns:
        try:
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date").reset_index(drop=True)
        except Exception:
            pass

    close = df["Close"].astype(float)
    n = len(close)
    if n < 2:
        return {
            "buy_and_hold_return_pct": 0.0,
            "strategy_return_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "number_of_signal_changes": 0,
        }

    # Buy and hold return
    buy_and_hold_return = (close.iloc[-1] / close.iloc[0] - 1) * 100

    # SMA(20)
    if pd is None:
        # Fallback: simple rolling implemented in pure Python
        sma = [sum(close[max(0, i - 19): i + 1]) / (i - max(0, i - 19) + 1) for i in range(n)]
        import math
        sma = pd.Series(sma) if pd else None
    else:
        sma = close.rolling(window=20, min_periods=1).mean()

    # Position: 1 if close > sma else 0
    position = (close > sma).astype(int)
    # Count signal changes
    number_of_signal_changes = int(position.diff().abs().fillna(0).sum())

    # Strategy returns: enter at next day's open is approximated by using today's close change
    daily_returns = close.pct_change().fillna(0)
    strat_daily = daily_returns * position.shift(1).fillna(0)
    strategy_cum = (1 + strat_daily).cumprod()
    strategy_return = (strategy_cum.iloc[-1] - 1) * 100

    # Max drawdown on strategy equity curve
    peak = strategy_cum.cummax()
    drawdown = (strategy_cum / peak - 1).min() * 100

    # Build equity curves starting at 100
    try:
        equity_df = pd.DataFrame()
        # Determine date/index for x-axis
        if "Date" in df.columns:
            equity_df["Date"] = pd.to_datetime(df["Date"]).reset_index(drop=True)
        else:
            # Use index if it's datetime-like, else a simple range index
            try:
                equity_df["Date"] = pd.to_datetime(df.index).to_series().reset_index(drop=True)
            except Exception:
                equity_df["Date"] = pd.Series(range(n))

        equity_df["Buy and Hold"] = (close / close.iloc[0] * 100).reset_index(drop=True)
        equity_df["Strategy"] = (strategy_cum * 100).reset_index(drop=True)
    except Exception:
        equity_df = None

    return {
        "buy_and_hold_return_pct": round(buy_and_hold_return, 2),
        "strategy_return_pct": round(strategy_return, 2),
        "max_drawdown_pct": round(drawdown, 2),
        "number_of_signal_changes": int(number_of_signal_changes),
        "equity_curve": equity_df,
    }
