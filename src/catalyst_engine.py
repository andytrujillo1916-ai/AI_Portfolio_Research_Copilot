def generate_catalyst_tracker(symbol, news_context, thesis_health, conviction_data):
    """Generate simple research-only catalyst tracking from news and thesis context."""
    sentiment = str(news_context.get("market_sentiment", "Neutral"))
    tags = [str(tag).lower() for tag in (news_context.get("event_tags", []) or [])]
    risk_flags = [str(flag).lower() for flag in (news_context.get("risk_flags", []) or [])]
    thesis_status = str(thesis_health.get("thesis_status", "Stable"))
    conviction_level = str(conviction_data.get("conviction_level", "Medium"))

    catalysts = []

    if any(tag in {"earnings", "guidance"} for tag in tags):
        catalysts.append(
            {
                "catalyst": f"{symbol} earnings/guidance cycle",
                "type": "Earnings",
                "potential_impact": "Positive" if sentiment == "Bullish" else "Neutral",
                "urgency": "High" if conviction_level in {"High", "Very High"} else "Medium",
                "reasoning": "Earnings and guidance often shift near-term thesis quality and conviction.",
            }
        )

    if any(tag in {"macro", "rates", "inflation", "fed"} for tag in tags):
        catalysts.append(
            {
                "catalyst": "Macro policy shift",
                "type": "Macro",
                "potential_impact": "Negative" if thesis_status in {"Weakening", "Broken"} else "Neutral",
                "urgency": "Medium",
                "reasoning": "Macro changes can move valuation and risk appetite across sectors.",
            }
        )

    if any(tag in {"ai", "product", "launch", "partnership"} for tag in tags):
        catalysts.append(
            {
                "catalyst": "Product/innovation updates",
                "type": "Product",
                "potential_impact": "Positive",
                "urgency": "Medium" if conviction_level in {"Low", "Medium"} else "High",
                "reasoning": "Product and innovation events can improve growth narrative and sentiment.",
            }
        )

    if any(
        key in " ".join(risk_flags)
        for key in {"regulation", "lawsuit", "investigation", "legal", "antitrust"}
    ):
        catalysts.append(
            {
                "catalyst": "Regulatory/legal headline risk",
                "type": "Regulation",
                "potential_impact": "Negative",
                "urgency": "High",
                "reasoning": "Regulatory or legal pressure can reduce confidence and increase downside risk.",
            }
        )

    if any(tag in {"analyst", "downgrade", "upgrade"} for tag in tags):
        catalysts.append(
            {
                "catalyst": "Analyst rating revisions",
                "type": "Analyst",
                "potential_impact": "Neutral",
                "urgency": "Low",
                "reasoning": "Analyst revisions can influence short-term sentiment without changing fundamentals.",
            }
        )

    if any(tag in {"sector", "rotation"} for tag in tags):
        catalysts.append(
            {
                "catalyst": "Sector rotation pressure",
                "type": "Sector",
                "potential_impact": "Neutral",
                "urgency": "Medium",
                "reasoning": "Sector leadership changes can alter relative strength and opportunity quality.",
            }
        )

    if not catalysts:
        catalysts.append(
            {
                "catalyst": "No major tagged catalyst",
                "type": "Macro",
                "potential_impact": "Neutral",
                "urgency": "Low",
                "reasoning": "No strong catalyst tag was detected in current news context.",
            }
        )

    urgency_rank = {"High": 3, "Medium": 2, "Low": 1}
    highest_priority_catalyst = sorted(
        catalysts,
        key=lambda row: urgency_rank.get(row.get("urgency", "Low"), 1),
        reverse=True,
    )[0]

    negative_count = sum(1 for c in catalysts if c.get("potential_impact") == "Negative")
    positive_count = sum(1 for c in catalysts if c.get("potential_impact") == "Positive")

    if thesis_status in {"Weakening", "Broken"} and negative_count >= 1:
        conviction_risk = "High"
    elif conviction_level in {"High", "Very High"} and positive_count >= 1:
        conviction_risk = "Medium"
    else:
        conviction_risk = "Low"

    summary = (
        f"Catalyst scan for {symbol} found {len(catalysts)} items with conviction risk {conviction_risk}. "
        "Use catalyst tracking as research context, not as certainty."
    )

    return {
        "catalysts": catalysts,
        "highest_priority_catalyst": highest_priority_catalyst,
        "conviction_risk": conviction_risk,
        "summary": summary,
    }
