def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _impact_from_score(score):
    if score >= 65:
        return "Positive"
    if score >= 45:
        return "Neutral"
    return "Negative"


def _risk_from_volatility(volatility):
    if volatility >= 30:
        return "High"
    if volatility >= 18:
        return "Medium"
    return "Low"


def _caution_tail(exposure_level):
    if exposure_level == "High":
        return " Keep exposure tighter because current exposure is already high."
    if exposure_level == "Medium":
        return " Keep position sizing disciplined due to moderate existing exposure."
    return ""


def run_scenarios(
    symbol,
    risk,
    signal_data,
    news_context,
    regime_data,
    exposure_data=None,
    asset_class=None,
):
    """Run simple research-only what-if scenarios for the selected asset."""
    volatility = _safe_float(risk.get("volatility_pct", 0))
    signal_score = _safe_float(signal_data.get("score", 0))
    news_sentiment = str(news_context.get("market_sentiment", "Neutral"))
    regime = str(regime_data.get("regime", "Unknown"))
    exposure_level = "None"
    if isinstance(exposure_data, dict):
        exposure_level = str(exposure_data.get("exposure_level", "None"))

    scenarios = []

    bull_score = signal_score + (8 if regime == "Bull Trend" else 0) + (4 if news_sentiment == "Bullish" else 0)
    scenarios.append(
        {
            "scenario_name": "Bull market continuation",
            "expected_impact": _impact_from_score(bull_score),
            "risk_level": _risk_from_volatility(volatility),
            "reasoning": f"{symbol} has signal score {signal_score:.0f}, regime {regime}, and news sentiment {news_sentiment}.",
            "suggested_response": "Stay selective and confirm trend strength with ongoing risk checks." + _caution_tail(exposure_level),
        }
    )

    correction_score = 50 - (8 if regime == "Bear Trend" else 0) - (6 if volatility >= 25 else 0)
    scenarios.append(
        {
            "scenario_name": "Market correction",
            "expected_impact": _impact_from_score(correction_score),
            "risk_level": "High" if volatility >= 25 or regime == "Bear Trend" else "Medium",
            "reasoning": f"Correction risk increases when regime is {regime} and volatility is {volatility:.2f}%.",
            "suggested_response": "Reduce conviction and prioritize downside protection in research plans." + _caution_tail(exposure_level),
        }
    )

    volatility_shock_score = 45 - (10 if volatility >= 30 else 0)
    scenarios.append(
        {
            "scenario_name": "High volatility shock",
            "expected_impact": _impact_from_score(volatility_shock_score),
            "risk_level": "High" if volatility >= 20 else "Medium",
            "reasoning": f"Current volatility is {volatility:.2f}%, which influences shock sensitivity.",
            "suggested_response": "Use smaller paper position assumptions and wait for stabilization signals." + _caution_tail(exposure_level),
        }
    )

    negative_news_score = 48 - (10 if news_sentiment == "Bearish" else 0) - (5 if regime == "Bear Trend" else 0)
    scenarios.append(
        {
            "scenario_name": "Negative news event",
            "expected_impact": _impact_from_score(negative_news_score),
            "risk_level": "High" if news_sentiment == "Bearish" else "Medium",
            "reasoning": f"News sentiment is {news_sentiment}, so downside news pressure may be stronger.",
            "suggested_response": "Treat new bearish headlines as a risk review trigger before updating thesis." + _caution_tail(exposure_level),
        }
    )

    positive_catalyst_score = signal_score + (8 if signal_score >= 65 else 0) + (5 if regime in {"Bull Trend", "Recovery"} else 0)
    scenarios.append(
        {
            "scenario_name": "Positive earnings / catalyst",
            "expected_impact": _impact_from_score(positive_catalyst_score),
            "risk_level": "Medium" if volatility >= 20 else "Low",
            "reasoning": f"Signal score {signal_score:.0f} and regime {regime} shape catalyst upside quality.",
            "suggested_response": "Track catalyst follow-through and separate one-day reaction from durable trend changes." + _caution_tail(exposure_level),
        }
    )

    macro_shock_score = 47 - (8 if volatility >= 25 else 0) - (6 if regime == "Bear Trend" else 0)
    scenarios.append(
        {
            "scenario_name": "Interest rate / macro shock",
            "expected_impact": _impact_from_score(macro_shock_score),
            "risk_level": "High" if volatility >= 25 else "Medium",
            "reasoning": f"Macro sensitivity is higher when volatility is {volatility:.2f}% and regime is {regime}.",
            "suggested_response": "Stress-test thesis assumptions and keep flexibility in position sizing." + _caution_tail(exposure_level),
        }
    )

    positive_count = sum(1 for item in scenarios if item["expected_impact"] == "Positive")
    negative_count = sum(1 for item in scenarios if item["expected_impact"] == "Negative")
    high_risk_count = sum(1 for item in scenarios if item["risk_level"] == "High")

    if negative_count >= 3 or high_risk_count >= 3:
        summary = "Scenario balance is cautious: multiple downside or high-risk cases need tighter research discipline."
    elif positive_count >= 3 and high_risk_count <= 1:
        summary = "Scenario balance is constructive, but outcomes remain uncertain and require ongoing review."
    else:
        summary = "Scenario balance is mixed: keep a neutral stance and update assumptions as new data arrives."

    return {
        "scenarios": scenarios,
        "overall_scenario_summary": summary,
    }
