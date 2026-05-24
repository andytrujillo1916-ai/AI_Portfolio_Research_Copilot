def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mode_settings(research_mode):
    if research_mode == "Conservative":
        return {"stop_loss_pct": 4.0, "vol_limit": 24.0}
    if research_mode == "Aggressive":
        return {"stop_loss_pct": 9.0, "vol_limit": 34.0}
    return {"stop_loss_pct": 6.0, "vol_limit": 28.0}


def generate_entry_exit_plan(
    execution_data,
    conviction_data,
    signal_data,
    alpha_data,
    risk,
    position_data=None,
    research_mode="Balanced",
):
    """Generate a research-only paper-trade entry/exit framework."""
    settings = _mode_settings(research_mode)

    execution_score = _safe_float(execution_data.get("execution_score", 0.0))
    readiness = str(execution_data.get("readiness_level", "Not Ready"))
    conviction_score = _safe_float(conviction_data.get("conviction_score", 0.0))
    signal_score = _safe_float(signal_data.get("score", 0.0))
    alpha_pct = _safe_float(alpha_data.get("alpha_pct", 0.0))
    volatility = _safe_float(risk.get("volatility_pct", 0.0))
    drawdown = _safe_float(risk.get("max_drawdown_pct", 0.0))

    has_position = False
    concentration_pct = 0.0
    if isinstance(position_data, dict):
        has_position = _safe_float(position_data.get("market_value", 0.0)) > 0
        concentration_pct = _safe_float(position_data.get("concentration_pct", 0.0))

    entry_zone = "No-Trade Zone"
    entry_readiness = "Low"
    if execution_score >= 75 and conviction_score >= 70 and alpha_pct > 0:
        entry_zone = "Favorable Entry Zone"
        entry_readiness = "High"
    elif execution_score >= 60 and conviction_score >= 55:
        entry_zone = "Conditional Entry Zone"
        entry_readiness = "Medium"
    elif execution_score >= 45:
        entry_zone = "Watch Zone"
        entry_readiness = "Low-Medium"

    trim_conditions = [
        "Conviction score drops below 50 from a previously strong level.",
        f"Volatility rises above {settings['vol_limit']:.0f}% and stays elevated.",
        "Alpha deteriorates below 0 versus benchmark.",
    ]
    if concentration_pct >= 35:
        trim_conditions.append("Position concentration is elevated and should be reduced.")

    hold_conditions = [
        "Conviction remains stable or improving.",
        "Execution readiness remains Near Ready or better.",
        "Signal quality stays above neutral (roughly 55+).",
    ]

    exit_conditions = [
        "Execution readiness falls to Not Ready with weak conviction.",
        "Alpha remains negative while regime context stays weak.",
        "Drawdown deepens beyond risk tolerance for current mode.",
        "Catalyst outcomes invalidate the working thesis.",
    ]

    if readiness == "Ready for Paper Trade" and conviction_score >= 70 and alpha_pct > 0:
        recommended_action = "Enter Paper Trade" if not has_position else "Hold"
    elif has_position and (conviction_score < 50 or alpha_pct < 0 or volatility > settings["vol_limit"]):
        recommended_action = "Trim"
    elif has_position and (execution_score < 40 or drawdown <= -20):
        recommended_action = "Exit"
    elif readiness in {"Watch", "Not Ready"}:
        recommended_action = "Watch"
    else:
        recommended_action = "Hold" if has_position else "Watch"

    if alpha_pct > 0 and volatility <= settings["vol_limit"] and drawdown > -15:
        risk_to_reward_view = "Favorable"
    elif alpha_pct > -1 and volatility <= settings["vol_limit"] + 4:
        risk_to_reward_view = "Balanced"
    else:
        risk_to_reward_view = "Unfavorable"

    summary = (
        f"{research_mode} mode framework suggests {recommended_action} with "
        f"entry readiness {entry_readiness} and risk/reward view {risk_to_reward_view}. "
        "This is paper-trading research guidance only."
    )

    return {
        "entry_zone": entry_zone,
        "entry_readiness": entry_readiness,
        "stop_loss_guidance_pct": settings["stop_loss_pct"],
        "trim_conditions": trim_conditions,
        "hold_conditions": hold_conditions,
        "exit_conditions": exit_conditions,
        "risk_to_reward_view": risk_to_reward_view,
        "recommended_action": recommended_action,
        "summary": summary,
    }
