def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def generate_fundamental_catalyst_context(symbol, sec_facts=None, catalyst_data=None):
    """Build a lightweight fundamental/catalyst quality context.

    V2 keeps SEC data as optional input so the app remains free-source friendly.
    Future EDGAR integration can pass companyfacts/submissions into this function.
    """
    symbol = str(symbol or "").upper()
    sec_facts = sec_facts or {}
    catalyst_data = catalyst_data or {}
    catalysts = catalyst_data.get("catalysts", []) or []

    score = 50.0
    positive = []
    risks = []
    limitations = [
        "SEC EDGAR company facts are planned as a free official data source.",
        "Earnings dates and catalyst calendars are placeholders until a verified free source is wired in.",
        "Fundamentals support long-term context; they do not guarantee future returns.",
    ]

    revenue_growth = _safe_float(sec_facts.get("revenue_growth_pct"), None)
    profitability_trend = sec_facts.get("profitability_trend", "")
    debt_trend = sec_facts.get("debt_trend", "")
    dilution_risk = sec_facts.get("dilution_risk", "")

    if revenue_growth is not None:
        if revenue_growth > 5:
            score += 8
            positive.append(f"Revenue trend appears positive at {revenue_growth:+.1f}%.")
        elif revenue_growth < 0:
            score -= 8
            risks.append(f"Revenue trend appears negative at {revenue_growth:+.1f}%.")

    if profitability_trend == "Improving":
        score += 6
        positive.append("Profitability trend is improving.")
    elif profitability_trend == "Deteriorating":
        score -= 6
        risks.append("Profitability trend is deteriorating.")

    if debt_trend == "Rising":
        score -= 5
        risks.append("Debt trend is rising.")
    elif debt_trend == "Falling":
        score += 4
        positive.append("Debt trend is falling.")

    if dilution_risk == "High":
        score -= 6
        risks.append("Share dilution risk is high.")

    high_catalysts = [row for row in catalysts if row.get("urgency") == "High"]
    if high_catalysts:
        score += 4
        positive.append("High-priority catalyst exists; useful for swing-timing review.")

    if not positive and not risks:
        risks.append("No verified fundamental or catalyst edge is available yet.")

    score = max(0, min(100, round(score, 1)))
    if score >= 65:
        quality = "Supportive"
    elif score <= 40:
        quality = "Weak"
    else:
        quality = "Neutral"

    return {
        "symbol": symbol,
        "fundamental_quality": quality,
        "fundamental_score": score,
        "earnings_date": catalyst_data.get("earnings_date", "Unknown"),
        "recent_filing_status": sec_facts.get("recent_filing_status", "Not connected"),
        "positive_factors": positive,
        "risk_flags": risks,
        "data_limitations": limitations,
        "summary": (
            f"{symbol} fundamental/catalyst quality is {quality}. "
            "V2 treats this as supporting evidence, with SEC EDGAR integration planned."
        ),
    }
