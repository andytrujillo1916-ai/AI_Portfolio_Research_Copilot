def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mode_profile(research_mode):
    if research_mode == "Conservative":
        return {"upside_mult": 0.9, "risk_mult": 1.2, "ready_cutoff": 68, "candidate_cutoff": 55}
    if research_mode == "Aggressive":
        return {"upside_mult": 1.1, "risk_mult": 0.9, "ready_cutoff": 60, "candidate_cutoff": 48}
    return {"upside_mult": 1.0, "risk_mult": 1.0, "ready_cutoff": 64, "candidate_cutoff": 52}


def generate_meta_decision(
    symbol,
    signal_data,
    conviction_data,
    opportunity_data,
    alpha_data,
    execution_data,
    position_size_data,
    entry_exit_data,
    regime_data,
    news_context,
    catalyst_data,
    scenario_data,
    stress_test_data,
    exposure_limits_data,
    correlation_data,
    capital_hierarchy_data,
    strategy_comparison_data,
    research_mode="Balanced",
):
    """Generate a final research-only verdict by combining major engine outputs."""
    signal_data = signal_data or {}
    conviction_data = conviction_data or {}
    opportunity_data = opportunity_data or {}
    alpha_data = alpha_data or {}
    execution_data = execution_data or {}
    position_size_data = position_size_data or {}
    entry_exit_data = entry_exit_data or {}
    regime_data = regime_data or {}
    news_context = news_context or {}
    catalyst_data = catalyst_data or {}
    scenario_data = scenario_data or {}
    stress_test_data = stress_test_data or {}
    exposure_limits_data = exposure_limits_data or {}
    correlation_data = correlation_data or {}
    capital_hierarchy_data = capital_hierarchy_data or {}
    strategy_comparison_data = strategy_comparison_data or {}

    mode = _mode_profile(research_mode)

    signal_score = _safe_float(signal_data.get("score", 50))
    conviction_score = _safe_float(conviction_data.get("conviction_score", 50))
    alpha_pct = _safe_float(alpha_data.get("alpha_pct", 0))
    execution_score = _safe_float(execution_data.get("execution_score", 50))
    diversification_score = _safe_float(correlation_data.get("diversification_score", 50))
    exposure_status = str(exposure_limits_data.get("exposure_status", "Moderate"))
    hierarchy_top = (capital_hierarchy_data.get("top_capital_candidate") or {}).get("symbol")
    best_strategy = (strategy_comparison_data.get("best_strategy") or {}).get("strategy_name", "Unknown")
    regime = str(regime_data.get("regime", "Unknown"))
    upside = (
        signal_score * 0.24
        + conviction_score * 0.23
        + execution_score * 0.22
        + max(-10, min(10, alpha_pct * 2)) * 1.5
        + diversification_score * 0.16
    ) * mode["upside_mult"]

    risk_penalty = 0.0
    main_risks = []
    if regime == "Bear Trend":
        risk_penalty += 10
        main_risks.append("Market regime is Bear Trend.")
    if alpha_pct < 0:
        risk_penalty += 8
        main_risks.append("Alpha versus benchmark is negative.")
    if execution_score < 50:
        risk_penalty += 10
        main_risks.append("Execution readiness is weak.")
    if exposure_status in {"Elevated", "High Risk"}:
        risk_penalty += 9
        main_risks.append(f"Portfolio exposure status is {exposure_status}.")
    if diversification_score < 45:
        risk_penalty += 7
        main_risks.append("Diversification score is low, indicating overlap risk.")

    catalyst_risk = str(catalyst_data.get("conviction_risk", "")).lower()
    if "high" in catalyst_risk:
        risk_penalty += 6
        main_risks.append("Catalyst risk is elevated.")

    stress_summary = str(stress_test_data.get("summary", "")).lower()
    if "risk" in stress_summary:
        risk_penalty += 4
        main_risks.append("Stress test summary indicates downside sensitivity.")

    scenario_summary = str(scenario_data.get("overall_scenario_summary", "")).lower()
    if "negative" in scenario_summary:
        risk_penalty += 4
        main_risks.append("Scenario analysis includes notable negative-case impact.")

    decision_score = max(0, min(100, round(upside - (risk_penalty * mode["risk_mult"]), 1)))

    if decision_score >= 75:
        final_verdict = "Strong Research Candidate"
    elif decision_score >= mode["ready_cutoff"]:
        final_verdict = "Research Candidate"
    elif decision_score >= mode["candidate_cutoff"]:
        final_verdict = "Watch"
    else:
        final_verdict = "Avoid"

    readiness = str(execution_data.get("readiness_level", "Watch"))
    if final_verdict in {"Strong Research Candidate", "Research Candidate"} and "Ready" in readiness:
        next_step = "Prepare a paper-trade plan and track outcome in the decision journal."
        timing_view = "Setup is actionable for paper-trading research if risk controls remain intact."
    elif final_verdict == "Watch":
        next_step = "Monitor catalysts, alpha, and execution readiness before increasing priority."
        timing_view = "Wait for stronger alignment across conviction, alpha, and execution."
    else:
        next_step = "Avoid new paper exposure for now and re-run research after conditions improve."
        timing_view = "Timing is unfavorable until key risk factors improve."

    main_reasons = [
        f"Signal score is {signal_score:.1f}/100.",
        f"Conviction score is {conviction_score:.1f}/100.",
        f"Execution readiness score is {execution_score:.1f}/100.",
        f"Best strategy fit: {best_strategy}.",
    ]
    if hierarchy_top:
        main_reasons.append(f"Capital hierarchy top candidate: {hierarchy_top}.")
    if alpha_pct >= 0:
        main_reasons.append(f"Alpha is non-negative at {alpha_pct:+.2f}%.")

    if not main_risks:
        main_risks.append("No major risk cluster triggered in this pass, but uncertainty remains.")

    conditions_to_change_view = [
        "Alpha turns negative for a sustained period.",
        "Execution readiness drops below Watch due to risk deterioration.",
        "Exposure or correlation risk moves into Elevated/High Risk territory.",
        "Regime shifts to Bear Trend with weaker signal strength.",
    ]

    capital_priority = "Top Priority" if symbol == hierarchy_top else "Secondary Priority"
    summary = (
        f"{research_mode} meta decision for {symbol}: {final_verdict} "
        f"with score {decision_score}/100. Human review remains required."
    )

    return {
        "final_verdict": final_verdict,
        "decision_score": decision_score,
        "recommended_next_step": next_step,
        "capital_priority": capital_priority,
        "timing_view": timing_view,
        "main_reasons": main_reasons,
        "main_risks": main_risks,
        "conditions_to_change_view": conditions_to_change_view,
        "human_review_required": True,
        "summary": summary,
    }
