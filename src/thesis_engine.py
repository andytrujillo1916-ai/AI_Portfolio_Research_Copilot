from datetime import datetime

from db_service import load_theses as db_load_theses
from db_service import save_thesis as db_save_thesis


def _ensure_file():
    return None


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default=5):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def load_theses():
    """Load all tracked theses from SQLite storage."""
    rows = db_load_theses()
    normalized = []
    for row in rows:
        normalized.append(
            {
                "date": str(row.get("date", row.get("updated_at", ""))),
                "symbol": str(row.get("symbol", "")),
                "thesis": str(row.get("thesis", "")),
                "confidence": str(row.get("confidence", "")),
                "stance": str(row.get("stance", "")),
                "thesis_status": str(row.get("thesis_status", "")),
                "last_price": str(row.get("last_price", "")),
                "last_signal": str(row.get("last_signal", "")),
                "last_regime": str(row.get("last_regime", "")),
                "last_news_sentiment": str(row.get("last_news_sentiment", "")),
                "last_note": str(row.get("last_note", "")),
            }
        )
    return normalized


def save_or_update_thesis(
    symbol,
    thesis,
    confidence,
    stance,
    thesis_status,
    last_price,
    last_signal,
    last_regime,
    last_news_sentiment,
    last_note="",
):
    """Save or update one thesis entry per symbol in SQLite."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_entry = {
        "date": now,
        "symbol": symbol,
        "thesis": thesis,
        "confidence": str(confidence),
        "stance": stance,
        "thesis_status": thesis_status,
        "last_price": str(last_price),
        "last_signal": last_signal,
        "last_regime": last_regime,
        "last_news_sentiment": last_news_sentiment,
        "last_note": last_note,
    }
    db_save_thesis(
        symbol=symbol,
        thesis=thesis,
        confidence=confidence,
        thesis_status=thesis_status,
        updated_at=now,
        stance=stance,
        last_price=last_price,
        last_signal=last_signal,
        last_regime=last_regime,
        last_news_sentiment=last_news_sentiment,
        last_note=last_note,
        date=now,
    )
    return updated_entry


def evaluate_thesis_health(
    symbol,
    current_price,
    signal_data,
    regime_data,
    news_context,
):
    """Evaluate thesis health from current signal, regime, and sentiment context."""
    score = _safe_float(signal_data.get("score", 0.0))
    signal_label = str(signal_data.get("signal", "Unknown"))
    regime = str(regime_data.get("regime", "Unknown"))
    sentiment = str(news_context.get("market_sentiment", "Neutral"))
    drawdown = _safe_float(signal_data.get("max_drawdown_pct", 0.0))

    points = 0
    reasoning = [f"Evaluating thesis for {symbol} at current price {current_price}."]

    if score >= 70 or signal_label == "Strong Watch":
        points += 2
        reasoning.append("Signal quality is currently strong.")
    elif score >= 55 or signal_label == "Watch":
        points += 1
        reasoning.append("Signal quality is moderately supportive.")
    elif score <= 40 or signal_label == "Avoid":
        points -= 2
        reasoning.append("Signal quality is weak.")
    else:
        reasoning.append("Signal quality is mixed.")

    if regime in {"Bull Trend", "Recovery"}:
        points += 1
        reasoning.append(f"Regime ({regime}) supports a constructive thesis.")
    elif regime in {"Bear Trend", "High Volatility"}:
        points -= 1
        reasoning.append(f"Regime ({regime}) adds caution to the thesis.")
    else:
        reasoning.append(f"Regime ({regime}) is neutral for thesis quality.")

    if sentiment == "Bullish":
        points += 1
        reasoning.append("News sentiment is supportive.")
    elif sentiment == "Bearish":
        points -= 1
        reasoning.append("News sentiment is a headwind.")
    else:
        reasoning.append("News sentiment is neutral.")

    if drawdown <= -20:
        points -= 1
        reasoning.append("Deep drawdown context adds fragility to the thesis.")

    if points >= 3:
        status = "Strengthening"
        confidence_change = 2
        suggested_action = "Hold"
    elif points >= 1:
        status = "Stable"
        confidence_change = 0
        suggested_action = "Review"
    elif points <= -3:
        status = "Broken"
        confidence_change = -2
        suggested_action = "Rebuild Thesis"
    else:
        status = "Weakening"
        confidence_change = -1
        suggested_action = "Re-run Research"

    return {
        "thesis_status": status,
        "confidence_change": max(-2, min(2, confidence_change)),
        "reasoning": reasoning,
        "suggested_action": suggested_action,
    }
