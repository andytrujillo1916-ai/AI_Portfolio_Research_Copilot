def get_watchlist():
    return ["SPY", "VOO", "QQQ", "AAPL", "MSFT", "NVDA"]


def _mock_snapshot(symbol):
    base_prices = {
        "SPY": 450.0,
        "VOO": 420.0,
        "QQQ": 360.0,
        "AAPL": 185.0,
        "MSFT": 320.0,
        "NVDA": 540.0,
    }
    price = base_prices.get(symbol, 100.0)
    change = round((len(symbol) % 7 - 3) * 0.4, 2)
    volume = 1_000_000 + (len(symbol) * 45_000)
    return {
        "symbol": symbol,
        "price": price,
        "change_pct": change,
        "volume": volume,
    }


def _build_mock_series(symbol, days=30):
    value = _mock_snapshot(symbol)["price"]
    prices = []
    for d in range(days):
        value = max(value + ((d % 5) - 2) * 0.5, 1.0)
        prices.append(round(value + d * 0.2, 2))
    return prices


def get_price_history(symbol, period="1mo"):
    """Return price history for `symbol` over `period` as a DataFrame or fallback data."""
    try:
        import yfinance as yf
        import pandas as pd

        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        if hist is None or hist.empty:
            raise ValueError(f"Empty history from yfinance for {symbol} ({period})")
        df = hist.reset_index()[["Date", "Close"]]
        df["Date"] = pd.to_datetime(df["Date"])
        return {"source": "yfinance", "data": df}
    except ModuleNotFoundError as error:
        return {
            "source": "mock",
            "error": str(error),
            "data": _mock_price_history(symbol),
        }
    except Exception as error:
        return {
            "source": "mock",
            "error": str(error),
            "data": _mock_price_history(symbol),
        }


def _mock_price_history(symbol, days=30):
    prices = _build_mock_series(symbol, days=days)
    try:
        import pandas as pd

        dates = pd.date_range(end=pd.Timestamp.today(), periods=days)
        return pd.DataFrame({"Date": dates, "Close": prices})
    except Exception:
        dates = [f"day-{i}" for i in range(days)]
        return {"Date": dates, "Close": prices}


def get_market_snapshot(symbol):
    """Return latest market snapshot: price, daily change pct, volume, and source."""
    try:
        import yfinance as yf

        ticker = yf.Ticker(symbol)
        recent = ticker.history(period="2d")
        if recent is None or recent.empty:
            raise ValueError(f"No recent data from yfinance for {symbol}")
        latest = recent.iloc[-1]
        prev = recent.iloc[-2] if len(recent) > 1 else latest
        price = float(latest["Close"])
        prev_close = float(prev["Close"]) if "Close" in prev else price
        change_pct = round((price - prev_close) / prev_close * 100, 2) if prev_close else 0.0
        volume = int(latest.get("Volume", 0))
        return {
            "symbol": symbol,
            "price": price,
            "change_pct": change_pct,
            "volume": volume,
            "source": "yfinance",
        }
    except ModuleNotFoundError as error:
        snapshot = _mock_snapshot(symbol)
        snapshot["source"] = "mock"
        snapshot["error"] = str(error)
        return snapshot
    except Exception as error:
        snapshot = _mock_snapshot(symbol)
        snapshot["source"] = "mock"
        snapshot["error"] = str(error)
        return snapshot


def get_asset_comparison(symbols, period="1mo", normalize=True):
    """Return close price series for each symbol.

    If `normalize=True`, each series is scaled so the first value == 100
    (normalized = (price / first_price) * 100).
    Returns a dict with `source` and `data` to indicate real vs mock data.
    """
    try:
        import yfinance as yf
        import pandas as pd

        prices = []
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)[["Close"]].rename(columns={"Close": symbol})
            hist.index = pd.to_datetime(hist.index)
            prices.append(hist)
        if not prices:
            raise ValueError("No symbols provided")
        df = pd.concat(prices, axis=1).dropna()
        df.index.name = "Date"
        if normalize:
            df = df.apply(lambda col: (col / col.iloc[0]) * 100)
        return {"source": "yfinance", "data": df}
    except Exception as error:
        # Build fallback mock series
        days = 30
        prices = {}
        for symbol in symbols:
            prices[symbol] = _build_mock_series(symbol, days=days)
        try:
            import pandas as pd

            dates = pd.date_range(end=pd.Timestamp.today(), periods=days)
            df = pd.DataFrame(prices, index=dates)
            if normalize:
                df = df.apply(lambda col: (col / col.iloc[0]) * 100)
            return {"source": "mock", "data": df, "error": str(error)}
        except Exception:
            # Return plain dict of lists; normalize manually if requested
            if normalize:
                norm = {}
                for sym, series in prices.items():
                    first = series[0] if series else 1
                    norm[sym] = [round((p / first) * 100, 2) for p in series]
                dates = [f"day-{i}" for i in range(days)]
                fallback = {"Date": dates}
                fallback.update(norm)
                return {"source": "mock", "data": fallback, "error": str(error)}
            else:
                dates = [f"day-{i}" for i in range(days)]
                fallback = {"Date": dates}
                fallback.update(prices)
                return {"source": "mock", "data": fallback, "error": str(error)}


def get_risk_metrics(price_history):
    """Return return, volatility, and max drawdown for a price series."""
    try:
        import pandas as pd

        if isinstance(price_history, dict):
            price_history = pd.DataFrame(price_history)
        if hasattr(price_history, "set_index"):
            df = price_history.copy()
        else:
            df = pd.DataFrame(price_history)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date").set_index("Date")
        if "Close" not in df.columns and len(df.columns) > 0:
            df = df.iloc[:, [0]]
            df.columns = ["Close"]
        close = df["Close"].astype(float)
        returns = close.pct_change().dropna()
        total_return = (close.iloc[-1] / close.iloc[0] - 1) * 100 if len(close) > 1 else 0.0
        volatility = returns.std() * (252 ** 0.5) * 100 if not returns.empty else 0.0
        drawdown = close / close.cummax() - 1
        max_drawdown = drawdown.min() * 100 if not drawdown.empty else 0.0
        return {
            "return_pct": round(total_return, 2),
            "volatility_pct": round(volatility, 2),
            "max_drawdown_pct": round(max_drawdown, 2),
        }
    except Exception:
        closes = []
        if isinstance(price_history, dict):
            if "Close" in price_history:
                closes = [float(x) for x in price_history.get("Close", [])]
            else:
                first_key = next((k for k in price_history if k not in {"Date", "source", "error"}), None)
                if first_key:
                    closes = [float(x) for x in price_history.get(first_key, [])]
        elif isinstance(price_history, list):
            closes = [float(x) for x in price_history]
        if len(closes) < 2:
            return {"return_pct": 0.0, "volatility_pct": 0.0, "max_drawdown_pct": 0.0}
        total_return = (closes[-1] / closes[0] - 1) * 100
        returns = [(closes[i] / closes[i - 1] - 1) for i in range(1, len(closes))]
        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / max(len(returns) - 1, 1)
        volatility = (variance ** 0.5) * (252 ** 0.5) * 100
        peak = closes[0]
        drawdowns = []
        for price in closes:
            peak = max(peak, price)
            drawdowns.append((price / peak) - 1)
        max_drawdown = min(drawdowns) * 100 if drawdowns else 0.0
        return {
            "return_pct": round(total_return, 2),
            "volatility_pct": round(volatility, 2),
            "max_drawdown_pct": round(max_drawdown, 2),
        }
