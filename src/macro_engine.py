def generate_macro_context(research_mode="Balanced"):
    """Generate simple research-only macro context using placeholder rules."""
    macro_state = "Neutral"
    inflation_risk = "Moderate"
    rate_environment = "Stable to Restrictive"
    growth_outlook = "Mixed"
    market_risk_bias = "Balanced risk posture"
    macro_notes = [
        "Macro context is a top-down framing tool, not a forecast.",
        "Cross-check macro bias with asset-level signal and risk metrics.",
    ]
    portfolio_implication = (
        "Keep allocations diversified and avoid overreacting to a single macro narrative."
    )

    if research_mode == "Conservative":
        macro_state = "Risk-Off"
        inflation_risk = "Elevated"
        rate_environment = "Restrictive"
        growth_outlook = "Cautious"
        market_risk_bias = "Defensive risk posture"
        macro_notes.append(
            "Conservative mode adds caution to risk-taking and position sizing."
        )
        portfolio_implication = (
            "Favor higher-quality setups, keep cash buffers, and tighten risk assumptions."
        )
    elif research_mode == "Aggressive":
        macro_state = "Risk-On"
        inflation_risk = "Moderate"
        rate_environment = "Neutral to Easing"
        growth_outlook = "Constructive"
        market_risk_bias = "Moderately pro-risk posture"
        macro_notes.append(
            "Aggressive mode allows more upside participation, while still requiring risk controls."
        )
        portfolio_implication = (
            "Lean toward stronger momentum and signal quality, but keep drawdown checks active."
        )
    else:
        macro_notes.append(
            "Balanced mode keeps a neutral top-down lens with measured risk exposure."
        )

    return {
        "macro_state": macro_state,
        "inflation_risk": inflation_risk,
        "rate_environment": rate_environment,
        "growth_outlook": growth_outlook,
        "market_risk_bias": market_risk_bias,
        "macro_notes": macro_notes,
        "portfolio_implication": portfolio_implication,
    }
