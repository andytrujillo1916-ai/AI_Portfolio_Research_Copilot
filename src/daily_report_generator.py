from market_data import get_market_snapshot, get_price_history, get_risk_metrics
from news_engine import generate_news_context
from signal_engine import generate_signal
from regime_engine import detect_market_regime


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def generate_daily_report(
    watchlist,
    research_mode="Balanced",
    period="1mo",
):
    """Generate a simple research-only daily watchlist report."""
    rows = []
    notable_news = []

    for symbol in watchlist or []:
        try:
            snapshot = get_market_snapshot(symbol)
            price_data = get_price_history(symbol, period=period)
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
                    "change_pct": snapshot.get("change_pct", 0.0),
                    "return_pct": risk.get("return_pct", 0.0),
                    "volatility_pct": risk.get("volatility_pct", 0.0),
                    "max_drawdown_pct": risk.get("max_drawdown_pct", 0.0),
                    "news_sentiment": news_context.get("market_sentiment", "Neutral"),
                    "signal": signal_data.get("signal", "Unknown"),
                    "score": signal_data.get("score", 0),
                    "regime": regime,
                }
            )

            headlines = news_context.get("recent_headlines", [])
            if headlines:
                top = headlines[0]
                title = top.get("title", "No headline")
                notable_news.append(f"{symbol}: {title}")
        except Exception:
            # Continue report generation even if one asset fails.
            continue

    rows.sort(key=lambda row: _safe_float(row.get("score", 0.0)), reverse=True)
    top_opportunities = [
        {
            "symbol": row.get("symbol", "N/A"),
            "signal": row.get("signal", "N/A"),
            "score": row.get("score", 0),
            "regime": row.get("regime", "Unknown"),
        }
        for row in rows[:3]
    ]
    highest_risk_assets = sorted(
        rows,
        key=lambda row: _safe_float(row.get("volatility_pct", 0.0)),
        reverse=True,
    )[:3]

    avg_score = (
        sum(_safe_float(row.get("score", 0.0)) for row in rows) / len(rows)
        if rows
        else 0.0
    )
    avg_vol = (
        sum(_safe_float(row.get("volatility_pct", 0.0)) for row in rows) / len(rows)
        if rows
        else 0.0
    )
    market_summary = (
        f"{research_mode} mode watchlist scan across {len(rows)} assets: "
        f"average score {avg_score:.2f}/100 and average volatility {avg_vol:.2f}%."
    )

    recommended_focus = [
        "Review top opportunities alongside regime and volatility context.",
        "Double-check high-volatility names before increasing paper exposure.",
        "Use notable news as context, not as a standalone decision trigger.",
    ]
    if research_mode == "Conservative":
        recommended_focus.append("Prioritize downside risk control and smaller position assumptions.")
    elif research_mode == "Aggressive":
        recommended_focus.append("Allow more upside focus, but keep drawdown and risk limits active.")

    return {
        "report_title": "Daily Research Report",
        "market_summary": market_summary,
        "top_opportunities": top_opportunities,
        "highest_risk_assets": highest_risk_assets,
        "notable_news": notable_news[:5],
        "watchlist_table": rows,
        "recommended_focus": recommended_focus,
        "disclaimer": (
            "Research-only report for learning and paper-trading context. "
            "Not financial advice. No live execution or broker connectivity."
        ),
    }
