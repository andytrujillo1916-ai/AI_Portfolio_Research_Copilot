def _safe_float(value):
    """Convert values to float when possible."""
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_close_series(price_data):
    """Extract a close-price series from a DataFrame, dict, or list-like input."""
    if price_data is None:
        return []

    data = price_data
    if isinstance(price_data, dict) and "data" in price_data:
        data = price_data["data"]

    if hasattr(data, "set_index"):
        try:
            close = data.copy()
            if "Date" in close.columns:
                close = close.sort_values("Date")
            if "Close" in close.columns:
                return [float(value) for value in close["Close"].tolist()]
            if len(close.columns) > 0:
                return [float(value) for value in close.iloc[:, 0].tolist()]
        except Exception:
            pass

    if isinstance(data, dict) and "Close" in data:
        return [float(value) for value in data["Close"]]

    if isinstance(data, list):
        return [float(value) for value in data]

    return []


def _compute_recent_trend(closes):
    """Compute recent trend percentage from the latest close points."""
    if len(closes) < 2:
        return 0.0

    recent_segment = closes[-5:] if len(closes) >= 5 else closes
    if len(recent_segment) < 2:
        return 0.0

    start = recent_segment[0]
    end = recent_segment[-1]
    if start == 0:
        return 0.0
    return ((end - start) / start) * 100


def detect_market_regime(price_data, risk):
    """Detect a simple research-only market regime from price data and risk metrics."""
    closes = _extract_close_series(price_data)
    return_pct = _safe_float(risk.get("return_pct")) if isinstance(risk, dict) else 0.0
    volatility_pct = _safe_float(risk.get("volatility_pct")) if isinstance(risk, dict) else 0.0
    max_drawdown_pct = _safe_float(risk.get("max_drawdown_pct")) if isinstance(risk, dict) else 0.0
    recent_trend = _compute_recent_trend(closes)

    reasoning = []

    if volatility_pct is None:
        volatility_pct = 0.0
    if return_pct is None:
        return_pct = 0.0
    if max_drawdown_pct is None:
        max_drawdown_pct = 0.0

    # Priority order: extreme volatility first, then recovery, then trend classes.
    if volatility_pct >= 35:
        regime = "High Volatility"
        confidence = 8
        strategy_bias = "Reduce confidence in signals"
        risk_note = "Reduce confidence in signals: high volatility can create noisy signals, so use wider caution bands and smaller confidence in the setup."
        reasoning.append(f"Volatility is {volatility_pct:.2f}% and is above the high-volatility threshold.")
        reasoning.append("Price action is likely being dominated by unstable swings rather than a clean trend.")
        return {
            "regime": regime,
            "confidence": confidence,
            "reasoning": reasoning,
            "strategy_bias": strategy_bias,
            "risk_note": risk_note,
        }

    if return_pct >= 0 and max_drawdown_pct <= -8 and recent_trend > 0:
        regime = "Recovery"
        confidence = 6
        strategy_bias = "Mean reversion may work better"
        risk_note = "Prices are improving after a drawdown, but the market is still fragile and may retrace."
        reasoning.append("Returns are positive after a meaningful drawdown, which suggests a recovery phase.")
        reasoning.append("Recent trend is improving, but the market is not yet in a fully stable trend regime.")
        return {
            "regime": regime,
            "confidence": confidence,
            "reasoning": reasoning,
            "strategy_bias": strategy_bias,
            "risk_note": risk_note,
        }

    if return_pct > 2 and volatility_pct <= 25 and recent_trend > 0:
        regime = "Bull Trend"
        confidence = 7
        strategy_bias = "Trend-following may work better"
        risk_note = "Trend conditions are favorable, but signals still need confirmation and should be treated as research guidance only."
        reasoning.append(f"Positive return of {return_pct:.2f}% is aligned with a rising price trend.")
        reasoning.append(f"Volatility at {volatility_pct:.2f}% is moderate enough to allow trend signals to be useful.")
        return {
            "regime": regime,
            "confidence": confidence,
            "reasoning": reasoning,
            "strategy_bias": strategy_bias,
            "risk_note": risk_note,
        }

    if return_pct < -3 and max_drawdown_pct <= -10:
        regime = "Bear Trend"
        confidence = 7
        strategy_bias = "Reduce confidence in signals"
        risk_note = "Downside pressure is strong and drawdowns are deep, so signal quality may degrade in a falling market."
        reasoning.append(f"Returns are negative at {return_pct:.2f}% and drawdown is {max_drawdown_pct:.2f}%.")
        reasoning.append("The current setup looks more like persistent selling pressure than a healthy rebound.")
        return {
            "regime": regime,
            "confidence": confidence,
            "reasoning": reasoning,
            "strategy_bias": strategy_bias,
            "risk_note": risk_note,
        }

    if abs(return_pct) <= 3 and volatility_pct <= 18 and abs(recent_trend) <= 2:
        regime = "Sideways / Range"
        confidence = 5
        strategy_bias = "Mean reversion may work better"
        risk_note = "Price movement is narrow and directionless, so range-based research is more appropriate than trend chasing."
        reasoning.append("Returns are near flat and volatility is contained.")
        reasoning.append("The market appears to be consolidating rather than trending strongly.")
        return {
            "regime": regime,
            "confidence": confidence,
            "reasoning": reasoning,
            "strategy_bias": strategy_bias,
            "risk_note": risk_note,
        }

    if return_pct < 0:
        regime = "Bear Trend"
        confidence = 5
        strategy_bias = "Reduce confidence in signals"
        risk_note = "The market is still weak, so keep the thesis cautious and emphasize risk management in research notes."
        reasoning.append(f"Returns are negative at {return_pct:.2f}%.")
        reasoning.append("This setup is more defensive than a clean recovery or bullish trend.")
    elif recent_trend > 0:
        regime = "Bull Trend"
        confidence = 5
        strategy_bias = "Trend-following may work better"
        risk_note = "The trend is positive, but evidence is moderate rather than strong."
        reasoning.append("Recent price movement is positive.")
    else:
        regime = "Sideways / Range"
        confidence = 4
        strategy_bias = "Mean reversion may work better"
        risk_note = "Price action looks mixed, so keep the research stance balanced and avoid overcommitting to a single direction."
        reasoning.append("The market is not showing a strong directional move.")

    return {
        "regime": regime,
        "confidence": confidence,
        "reasoning": reasoning,
        "strategy_bias": strategy_bias,
        "risk_note": risk_note,
    }
