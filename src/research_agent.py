def generate_research_summary(symbol, snapshot, risk, notes=""):
    """Generate a simple rule-based research summary."""
    price = snapshot.get("price")
    change_pct = snapshot.get("change_pct", 0.0)
    return_pct = risk.get("return_pct", 0.0)
    volatility_pct = risk.get("volatility_pct", 0.0)
    max_drawdown_pct = risk.get("max_drawdown_pct", 0.0)

    bull_reasons = []
    bear_reasons = []

    if isinstance(price, (int, float)) and price > 0:
        bull_reasons.append(f"Current price is ${price:.2f}.")
    else:
        bear_reasons.append("Price data is not available or invalid.")

    if change_pct >= 0:
        bull_reasons.append(f"Recent price change is positive at {change_pct:+.2f}%.")
    else:
        bear_reasons.append(f"Recent price change is negative at {change_pct:+.2f}%.")

    if return_pct >= 0:
        bull_reasons.append(f"Trend return is positive at {return_pct:+.2f}%.")
    else:
        bear_reasons.append(f"Trend return is negative at {return_pct:+.2f}%.")

    if volatility_pct < 20:
        bull_reasons.append("Volatility is relatively low.")
    else:
        bear_reasons.append("Volatility is elevated.")

    if max_drawdown_pct > -20:
        bull_reasons.append("Drawdown has been modest.")
    else:
        bear_reasons.append(f"Max drawdown is deep at {max_drawdown_pct:.2f}%.")

    if notes:
        notes_line = notes.strip().replace("\n", " ")
        bull_reasons.append("User notes are available for review.")
    else:
        bear_reasons.append("No user notes have been added yet.")

    if len(bull_reasons) >= len(bear_reasons):
        stance = "Cautiously Bullish"
    else:
        stance = "Cautious / Watch"

    if volatility_pct >= 40 or max_drawdown_pct <= -30:
        stance = "Risk-Aware"
    if change_pct < 0 and return_pct < 0:
        stance = "Bearish"

    questions = [
        f"What would make {symbol} a stronger buy signal?",
        "How could volatility affect this thesis?",
        "What key event would change the outlook?",
    ]
    if notes:
        questions.insert(0, "What should I learn from my current notes?")

    return {
        "bull_case": " ".join(bull_reasons) if bull_reasons else "No clear bull case yet.",
        "bear_case": " ".join(bear_reasons) if bear_reasons else "No clear bear case yet.",
        "risk_summary": (
            f"Volatility is {volatility_pct:.2f}%, "
            f"max drawdown is {max_drawdown_pct:.2f}%.")
        ,
        "learning_questions": questions,
        "overall_stance": stance,
    }
