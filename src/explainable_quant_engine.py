from market_data import get_price_history, get_risk_metrics


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, value))


def _risk_level(volatility, drawdown):
    drawdown = abs(drawdown)
    if volatility >= 35 or drawdown >= 25:
        return "High"
    if volatility >= 22 or drawdown >= 12:
        return "Medium"
    return "Low"


def _research_action(score, regime, risk_level, thesis_status):
    if thesis_status == "Broken":
        return "Thesis Broken"
    if score >= 75 and risk_level != "High":
        return "Paper Buy Candidate"
    if score >= 62:
        return "Watch Pullback"
    if score >= 48:
        return "Hold / Research"
    if regime == "Bear Trend" and score < 38:
        return "Short Research Candidate (research-only)"
    if risk_level == "High":
        return "Reduce Exposure"
    return "Avoid"


def build_ranked_decision_table(
    screened_assets,
    opportunity_data=None,
    selected_symbol=None,
    selected_conviction=None,
    selected_thesis_health=None,
):
    """Create an explainable ranked opportunity table from existing screener output."""
    opportunity_rows = {}
    for row in (opportunity_data or {}).get("ranked_opportunities", []):
        opportunity_rows[row.get("symbol")] = row

    rows = []
    for asset in screened_assets or []:
        symbol = asset.get("symbol", "")
        opportunity = opportunity_rows.get(symbol, {})
        signal_score = _safe_float(asset.get("score", 50.0))
        opportunity_score = _safe_float(opportunity.get("opportunity_score", signal_score))
        volatility = _safe_float(asset.get("volatility_pct", 0.0))
        drawdown = _safe_float(asset.get("max_drawdown_pct", 0.0))
        regime = str(asset.get("regime", "Unknown"))
        sentiment = str(asset.get("news_sentiment", "Neutral"))
        risk = _risk_level(volatility, drawdown)

        conviction = round(_clamp((signal_score * 0.55) + (opportunity_score * 0.45)), 1)
        thesis_status = "Stable"
        if symbol == selected_symbol:
            conviction = _safe_float((selected_conviction or {}).get("conviction_score", conviction))
            thesis_status = (selected_thesis_health or {}).get("thesis_status", "Stable")

        if regime in {"Bull Trend", "Recovery"} and sentiment != "Bearish":
            timing = "trend continuation"
        elif volatility >= 35:
            timing = "high-risk event"
        elif drawdown <= -15 and signal_score >= 55:
            timing = "pullback watch"
        elif regime == "Bear Trend":
            timing = "wait"
        elif thesis_status in {"Weakening", "Broken"}:
            timing = "thesis invalidation"
        else:
            timing = "hold / research"

        rows.append(
            {
                "asset": symbol,
                "conviction": round(conviction, 1),
                "research_action": _research_action(conviction, regime, risk, thesis_status),
                "timing_view": timing,
                "thesis_health": thesis_status,
                "risk_level": risk,
            }
        )

    rows.sort(key=lambda row: row.get("conviction", 0), reverse=True)
    return rows


def calculate_explainability_panel(
    signal_data,
    conviction_data,
    regime_data,
    news_context,
    opportunity_data,
    risk,
    exposure_limits_data,
    thesis_health,
    confidence_data,
):
    """Explain how major engines contribute to the final decision-support score."""
    signal_score = _safe_float((signal_data or {}).get("score", 50.0))
    conviction_score = _safe_float((conviction_data or {}).get("conviction_score", 50.0))
    best_opp = (opportunity_data or {}).get("best_opportunity", {})
    opportunity_score = _safe_float(best_opp.get("opportunity_score", 50.0))
    regime = str((regime_data or {}).get("regime", "Unknown"))
    sentiment = str((news_context or {}).get("market_sentiment", "Neutral"))
    volatility = _safe_float((risk or {}).get("volatility_pct", 0.0))
    exposure_status = str((exposure_limits_data or {}).get("exposure_status", "Moderate"))
    thesis_status = str((thesis_health or {}).get("thesis_status", "Stable"))
    trust_level = str((confidence_data or {}).get("trust_level", "Moderate"))

    regime_points = 8 if regime in {"Bull Trend", "Recovery"} else -8 if regime in {"Bear Trend", "High Volatility"} else 0
    news_points = 5 if sentiment == "Bullish" else -5 if sentiment == "Bearish" else 0
    volatility_penalty = -12 if volatility >= 35 else -6 if volatility >= 22 else 0
    exposure_penalty = -10 if exposure_status == "High Risk" else -6 if exposure_status == "Elevated" else -2 if exposure_status == "Moderate" else 0
    thesis_points = {"Strengthening": 8, "Stable": 2, "Weakening": -8, "Broken": -15}.get(thesis_status, 0)
    confidence_points = {"High": 6, "Moderate": 2, "Low": -8}.get(trust_level, 0)

    contributions = [
        {"engine": "signal", "weight": 20, "contribution": round((signal_score - 50) * 0.35, 1)},
        {"engine": "conviction", "weight": 25, "contribution": round((conviction_score - 50) * 0.45, 1)},
        {"engine": "regime", "weight": 10, "contribution": regime_points},
        {"engine": "news", "weight": 8, "contribution": news_points},
        {"engine": "opportunity", "weight": 15, "contribution": round((opportunity_score - 50) * 0.25, 1)},
        {"engine": "volatility penalty", "weight": 8, "contribution": volatility_penalty},
        {"engine": "exposure penalty", "weight": 6, "contribution": exposure_penalty},
        {"engine": "thesis health", "weight": 5, "contribution": thesis_points},
        {"engine": "confidence calibration", "weight": 3, "contribution": confidence_points},
    ]
    final_score = round(_clamp(50 + sum(row["contribution"] for row in contributions)), 1)
    return {
        "contributions": contributions,
        "final_score": final_score,
        "summary": (
            "Final score combines supportive signals with explicit risk penalties. "
            "It is research-only decision support, not a trade instruction."
        ),
    }


def generate_timing_explanation(regime_data, risk, catalyst_data, thesis_health, signal_data):
    """Translate engine state into simple timing language."""
    regime = str((regime_data or {}).get("regime", "Unknown"))
    volatility = _safe_float((risk or {}).get("volatility_pct", 0.0))
    drawdown = _safe_float((risk or {}).get("max_drawdown_pct", 0.0))
    catalyst_risk = str((catalyst_data or {}).get("conviction_risk", "")).lower()
    thesis_status = str((thesis_health or {}).get("thesis_status", "Stable"))
    signal_score = _safe_float((signal_data or {}).get("score", 50.0))

    if thesis_status == "Broken":
        label = "thesis invalidation"
        reasoning = "The thesis health check is broken, so timing should focus on review rather than entry."
    elif "high" in catalyst_risk:
        label = "high-risk event"
        reasoning = "Catalyst risk is elevated; wait for clarity before increasing paper exposure."
    elif volatility >= 35:
        label = "overextended"
        reasoning = "Volatility is high, so chasing the move adds research risk."
    elif drawdown <= -12 and signal_score >= 55:
        label = "pullback watch"
        reasoning = "The asset has pulled back while signals remain acceptable."
    elif regime in {"Bull Trend", "Recovery"} and signal_score >= 65:
        label = "trend continuation"
        reasoning = "Trend/regime and signal strength are aligned."
    else:
        label = "wait"
        reasoning = "The setup needs clearer alignment before a higher-priority paper decision."

    return {"timing_label": label, "reasoning": reasoning}


def generate_position_sizing_modes(position_size_data, risk):
    """Show conservative, balanced, and aggressive paper sizing bands."""
    base_pct = _safe_float((position_size_data or {}).get("recommended_position_pct", 0.0))
    volatility = _safe_float((risk or {}).get("volatility_pct", 0.0))
    risk_cut = 0.7 if volatility >= 35 else 0.85 if volatility >= 22 else 1.0

    return [
        {
            "mode": "Conservative",
            "suggested_position_pct": round(min(base_pct * 0.6 * risk_cut, 5.0), 2),
            "reasoning": "Lower cap with stronger volatility protection.",
        },
        {
            "mode": "Balanced",
            "suggested_position_pct": round(min(base_pct * risk_cut, 10.0), 2),
            "reasoning": "Uses the current engine sizing with moderate caps.",
        },
        {
            "mode": "Aggressive",
            "suggested_position_pct": round(min(base_pct * 1.35 * risk_cut, 15.0), 2),
            "reasoning": "Allows a larger paper size only inside strict no-leverage caps.",
        },
    ]


def compare_etf_benchmarks(period="1mo"):
    """Compare AI research context against major ETF benchmarks and a simple 60/40 proxy."""
    rows = []
    for symbol in ["SPY", "VTI", "QQQ"]:
        try:
            history = get_price_history(symbol, period=period)
            risk = get_risk_metrics(history.get("data") if isinstance(history, dict) else history)
            volatility = _safe_float(risk.get("volatility_pct", 0.0))
            sharpe = round(_safe_float(risk.get("return_pct", 0.0)) / volatility, 2) if volatility else 0.0
            rows.append(
                {
                    "benchmark": symbol,
                    "return_pct": risk.get("return_pct", 0.0),
                    "volatility_pct": volatility,
                    "max_drawdown_pct": risk.get("max_drawdown_pct", 0.0),
                    "sharpe": sharpe,
                    "diversification": "Medium" if symbol == "QQQ" else "High",
                }
            )
        except Exception:
            rows.append(
                {
                    "benchmark": symbol,
                    "return_pct": 0.0,
                    "volatility_pct": 0.0,
                    "max_drawdown_pct": 0.0,
                    "sharpe": 0.0,
                    "diversification": "Unknown",
                }
            )

    spy = next((row for row in rows if row["benchmark"] == "SPY"), {})
    try:
        bond_history = get_price_history("BND", period=period)
        bond_risk = get_risk_metrics(bond_history.get("data") if isinstance(bond_history, dict) else bond_history)
    except Exception:
        bond_risk = {"return_pct": 0.0, "volatility_pct": 0.0, "max_drawdown_pct": 0.0}

    sixty_forty_return = (_safe_float(spy.get("return_pct", 0.0)) * 0.6) + (_safe_float(bond_risk.get("return_pct", 0.0)) * 0.4)
    sixty_forty_vol = (_safe_float(spy.get("volatility_pct", 0.0)) * 0.6) + (_safe_float(bond_risk.get("volatility_pct", 0.0)) * 0.4)
    rows.append(
        {
            "benchmark": "60/40 basket",
            "return_pct": round(sixty_forty_return, 2),
            "volatility_pct": round(sixty_forty_vol, 2),
            "max_drawdown_pct": round((_safe_float(spy.get("max_drawdown_pct", 0.0)) * 0.6) + (_safe_float(bond_risk.get("max_drawdown_pct", 0.0)) * 0.4), 2),
            "sharpe": round(sixty_forty_return / sixty_forty_vol, 2) if sixty_forty_vol else 0.0,
            "diversification": "High",
        }
    )
    return {
        "benchmarks": rows,
        "summary": "Benchmarks are research comparisons only and do not imply guaranteed outperformance.",
    }
