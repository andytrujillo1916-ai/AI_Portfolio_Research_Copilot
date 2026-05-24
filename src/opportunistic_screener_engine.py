def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _rating(score):
    if score >= 70:
        return "Research Candidate"
    if score >= 50:
        return "Watch"
    return "Avoid"


def rank_opportunistic_stocks(screened_assets, research_mode="Balanced"):
    """Rank stocks/ETFs for balanced-growth research using momentum plus risk controls."""
    rows = []
    for asset in screened_assets or []:
        signal_score = _safe_float(asset.get("score", 0.0))
        return_pct = _safe_float(asset.get("return_pct", 0.0))
        volatility = _safe_float(asset.get("volatility_pct", 0.0))
        drawdown = abs(_safe_float(asset.get("max_drawdown_pct", 0.0)))
        sentiment = str(asset.get("news_sentiment", "Neutral"))
        regime = str(asset.get("regime", "Unknown"))
        confidence = str(asset.get("data_confidence", "Unknown"))

        score = 45.0
        score += min(max(return_pct, -15), 20) * 0.9
        score += (signal_score - 50) * 0.45

        if regime in {"Bull Trend", "Recovery"}:
            score += 8
        elif regime in {"Bear Trend", "High Volatility"}:
            score -= 8

        if sentiment == "Bullish":
            score += 4
        elif sentiment == "Bearish":
            score -= 5

        score -= max(0, volatility - 18) * 0.45
        score -= max(0, drawdown - 10) * 0.65

        if research_mode == "Conservative":
            score -= max(0, volatility - 15) * 0.25
            score -= max(0, drawdown - 8) * 0.25
        elif research_mode == "Aggressive":
            score += max(0, return_pct) * 0.15

        if confidence == "Low":
            score -= 8
        elif confidence == "Medium":
            score -= 3

        opportunity_score = round(max(0, min(100, score)), 2)
        label = _rating(opportunity_score)
        reasoning = (
            f"Momentum {return_pct:+.2f}%, signal {signal_score:.0f}, regime {regime}, "
            f"volatility {volatility:.2f}%, drawdown {drawdown:.2f}%, data confidence {confidence}."
        )

        rows.append(
            {
                "symbol": asset.get("symbol", ""),
                "opportunity_score": opportunity_score,
                "opportunity_label": label,
                "price": asset.get("price"),
                "return_pct": return_pct,
                "volatility_pct": volatility,
                "max_drawdown_pct": asset.get("max_drawdown_pct", 0.0),
                "signal": asset.get("signal", "Unknown"),
                "regime": regime,
                "news_sentiment": sentiment,
                "data_confidence": confidence,
                "data_source": asset.get("data_source", "unknown"),
                "reasoning": reasoning,
            }
        )

    rows.sort(key=lambda row: row.get("opportunity_score", 0), reverse=True)
    best = rows[0] if rows else {}
    avoid_count = sum(1 for row in rows if row.get("opportunity_label") == "Avoid")
    return {
        "ranked_opportunities": rows,
        "best_candidate": best,
        "avoid_count": avoid_count,
        "summary": (
            f"Balanced-growth opportunity scan reviewed {len(rows)} assets. "
            "Labels are research-only and are not trade instructions."
        ),
    }
