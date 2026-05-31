from market_data import get_market_snapshot, get_price_history, get_risk_metrics
from news_engine import generate_news_context
from regime_engine import detect_market_regime
from signal_engine import generate_signal
from data_quality_engine import evaluate_data_quality


def run_cross_asset_screen(watchlist, period="1mo"):
    """Run a research-only screener across all watchlist assets."""
    rows = []

    for symbol in watchlist:
        try:
            snapshot = get_market_snapshot(symbol)
            price_data = get_price_history(symbol, period=period)
            snapshot_quality = evaluate_data_quality(snapshot)
            price_quality = evaluate_data_quality(price_data)
            risk_input = price_data.get("data") if isinstance(price_data, dict) else price_data
            risk = get_risk_metrics(risk_input)
            news_context = generate_news_context(symbol)
            signal_data = generate_signal(symbol, snapshot, risk, news_context=news_context)

            regime = "Unknown"
            try:
                regime_data = detect_market_regime(price_data, risk)
                regime = regime_data.get("regime", "Unknown")
            except Exception:
                regime = "Unknown"

            rows.append(
                {
                    "symbol": symbol,
                    "price": snapshot.get("price"),
                    "return_pct": risk.get("return_pct", 0.0),
                    "volatility_pct": risk.get("volatility_pct", 0.0),
                    "max_drawdown_pct": risk.get("max_drawdown_pct", 0.0),
                    "news_sentiment": news_context.get("market_sentiment", "Neutral"),
                    "signal": signal_data.get("signal", "Unknown"),
                    "score": signal_data.get("score", 0),
                    "regime": regime,
                    "data_source": price_quality.get("source", snapshot_quality.get("source", "unknown")),
                    "data_provider": price_quality.get("provider", snapshot_quality.get("provider", "unknown")),
                    "source_trust": price_quality.get("source_trust", snapshot_quality.get("source_trust", "Warning")),
                    "data_confidence": "Low"
                    if "Low" in {snapshot_quality.get("data_confidence"), price_quality.get("data_confidence")}
                    else "Medium"
                    if "Medium" in {snapshot_quality.get("data_confidence"), price_quality.get("data_confidence")}
                    else "High",
                    "freshness_confidence": "Low"
                    if "Low" in {snapshot_quality.get("freshness_confidence"), price_quality.get("freshness_confidence")}
                    else "Medium"
                    if "Medium" in {snapshot_quality.get("freshness_confidence"), price_quality.get("freshness_confidence")}
                    else "High",
                    "data_quality_status": price_quality.get("status", "Unknown"),
                    "recommendation_gate": "Blocked"
                    if "Blocked" in {snapshot_quality.get("recommendation_gate"), price_quality.get("recommendation_gate")}
                    else "Warning"
                    if "Warning" in {snapshot_quality.get("recommendation_gate"), price_quality.get("recommendation_gate")}
                    else "Trusted",
                    "allowed_use": "display_only"
                    if "Blocked" in {snapshot_quality.get("recommendation_gate"), price_quality.get("recommendation_gate")}
                    else "research_and_recommendation"
                    if "Trusted" == price_quality.get("recommendation_gate") == snapshot_quality.get("recommendation_gate")
                    else "research_only",
                    "last_timestamp": price_quality.get("last_timestamp") or snapshot_quality.get("last_timestamp"),
                    "data_issues": " | ".join(snapshot_quality.get("issues", []) + price_quality.get("issues", [])),
                }
            )
        except Exception:
            # Continue scanning remaining assets if one asset fails.
            continue

    rows.sort(key=lambda row: row.get("score", 0), reverse=True)
    return rows
