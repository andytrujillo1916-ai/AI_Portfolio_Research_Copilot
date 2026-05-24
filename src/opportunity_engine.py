from asset_sector_map import map_asset_to_sector


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value, low, high):
    return max(low, min(high, value))


def _mode_weights(research_mode):
    if research_mode == "Conservative":
        return {
            "score_weight": 0.45,
            "drawdown_weight": 0.20,
            "vol_weight": 0.25,
            "news_weight": 0.05,
            "regime_weight": 0.05,
        }
    if research_mode == "Aggressive":
        return {
            "score_weight": 0.60,
            "drawdown_weight": 0.15,
            "vol_weight": 0.10,
            "news_weight": 0.07,
            "regime_weight": 0.08,
        }
    return {
        "score_weight": 0.52,
        "drawdown_weight": 0.18,
        "vol_weight": 0.18,
        "news_weight": 0.06,
        "regime_weight": 0.06,
    }


def _news_bonus(news_sentiment):
    if news_sentiment == "Bullish":
        return 100
    if news_sentiment == "Neutral":
        return 65
    if news_sentiment == "Bearish":
        return 35
    return 50


def _regime_bonus(regime):
    if regime == "Bull Trend":
        return 100
    if regime == "Recovery":
        return 85
    if regime == "Sideways / Range":
        return 55
    if regime in {"Bear Trend", "High Volatility"}:
        return 30
    return 50


def _priority_from_score(opportunity_score):
    if opportunity_score >= 70:
        return "High"
    if opportunity_score >= 50:
        return "Medium"
    return "Low"


def _extract_sector_extremes(sector_context):
    strongest = {}
    weakest = {}
    if isinstance(sector_context, dict):
        strongest = sector_context.get("strongest_sector", {}) or {}
        weakest = sector_context.get("weakest_sector", {}) or {}
    return strongest.get("sector", ""), weakest.get("sector", "")


def rank_opportunities(
    screened_assets,
    research_mode="Balanced",
    sector_context=None,
    asset_class=None,
):
    """Rank cross-asset opportunities with transparent research-only scoring."""
    if not screened_assets:
        return {
            "ranked_opportunities": [],
            "best_opportunity": {},
            "highest_risk_opportunity": {},
            "summary": "No screened assets were available for opportunity ranking.",
        }

    weights = _mode_weights(research_mode)
    strongest_sector, weakest_sector = _extract_sector_extremes(sector_context)
    ranked = []

    for asset in screened_assets:
        symbol = asset.get("symbol", "Unknown")
        signal_score = _safe_float(asset.get("score", 0))
        volatility = _safe_float(asset.get("volatility_pct", 0))
        drawdown_abs = abs(_safe_float(asset.get("max_drawdown_pct", 0)))
        regime = str(asset.get("regime", "Unknown"))
        news_sentiment = str(asset.get("news_sentiment", "Neutral"))
        signal = str(asset.get("signal", "Unknown"))
        mapped_sector = map_asset_to_sector(symbol)

        drawdown_quality = _clamp(100 - (drawdown_abs * 3), 0, 100)
        volatility_quality = _clamp(100 - (volatility * 2), 0, 100)
        news_quality = _news_bonus(news_sentiment)
        regime_quality = _regime_bonus(regime)

        opportunity_score = (
            signal_score * weights["score_weight"]
            + drawdown_quality * weights["drawdown_weight"]
            + volatility_quality * weights["vol_weight"]
            + news_quality * weights["news_weight"]
            + regime_quality * weights["regime_weight"]
        )

        sector_adjustment = 0.0
        if mapped_sector != "Unknown":
            if mapped_sector == strongest_sector:
                sector_adjustment = 2.0
            elif mapped_sector == weakest_sector:
                sector_adjustment = -2.0
        opportunity_score += sector_adjustment
        opportunity_score = round(_clamp(opportunity_score, 0, 100), 2)
        priority = _priority_from_score(opportunity_score)

        reasoning = (
            f"Signal {signal} ({signal_score:.0f}), volatility {volatility:.2f}%, "
            f"drawdown {drawdown_abs:.2f}%, news {news_sentiment}, regime {regime}."
        )
        if mapped_sector != "Unknown":
            reasoning += (
                f" Sector context: {mapped_sector} ({sector_adjustment:+.1f} adjustment)."
            )

        ranked.append(
            {
                "symbol": symbol,
                "opportunity_score": opportunity_score,
                "priority": priority,
                "reasoning": reasoning,
            }
        )

    ranked.sort(key=lambda row: row.get("opportunity_score", 0), reverse=True)
    best = ranked[0] if ranked else {}
    highest_risk_source = max(
        screened_assets,
        key=lambda row: _safe_float(row.get("volatility_pct", 0)),
    )
    highest_risk = {
        "symbol": highest_risk_source.get("symbol", "Unknown"),
        "volatility_pct": _safe_float(highest_risk_source.get("volatility_pct", 0)),
        "max_drawdown_pct": _safe_float(highest_risk_source.get("max_drawdown_pct", 0)),
        "signal": highest_risk_source.get("signal", "Unknown"),
        "score": _safe_float(highest_risk_source.get("score", 0)),
    }

    summary = (
        f"{research_mode} mode ranking balances signal strength with volatility/drawdown controls "
        "and simple news/regime context. This is research-only and not guaranteed."
    )
    if sector_context:
        summary += " Sector context included with small boosts/penalties."

    return {
        "ranked_opportunities": ranked,
        "best_opportunity": best,
        "highest_risk_opportunity": highest_risk,
        "summary": summary,
    }
