def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def generate_executive_summary(
    symbol,
    meta_decision,
    conviction_data,
    allocation_timing,
    position_size,
    entry_exit,
    exposure_limits,
    correlation_data,
    subagent_reviews,
    research_mode="Balanced",
):
    """Create a top-level research-only executive summary across major outputs."""
    meta_decision = meta_decision or {}
    conviction_data = conviction_data or {}
    allocation_timing = allocation_timing or {}
    position_size = position_size or {}
    entry_exit = entry_exit or {}
    exposure_limits = exposure_limits or {}
    correlation_data = correlation_data or {}
    subagent_reviews = subagent_reviews or {}

    headline_verdict = meta_decision.get("final_verdict", "Watch")
    recommended_next_action = meta_decision.get(
        "recommended_next_step",
        allocation_timing.get("recommended_action", "Watch and re-run research."),
    )
    suggested_paper_allocation = (
        f"{_safe_float(position_size.get('recommended_position_pct', 0.0)):.2f}% "
        f"(${_safe_float(position_size.get('recommended_position_value', 0.0)):,.2f})"
    )
    timing_view = meta_decision.get("timing_view", entry_exit.get("risk_to_reward_view", "Balanced"))

    top_reasons = list(meta_decision.get("main_reasons", []))[:3]
    if not top_reasons:
        top_reasons = [
            f"Conviction score: {_safe_float(conviction_data.get('conviction_score', 0.0)):.1f}/100.",
            f"Entry framework action: {entry_exit.get('recommended_action', 'Watch')}.",
        ]

    top_risks = list(meta_decision.get("main_risks", []))[:3]
    if not top_risks:
        top_risks = ["No major risks were surfaced in this pass, but uncertainty remains."]

    exposure_status = str(exposure_limits.get("exposure_status", "Moderate"))
    diversification_score = _safe_float(correlation_data.get("diversification_score", 50.0))
    if exposure_status in {"Elevated", "High Risk"} or diversification_score < 45:
        portfolio_warning = (
            f"Portfolio caution: exposure status {exposure_status}, "
            f"diversification score {diversification_score:.0f}/100."
        )
    else:
        portfolio_warning = (
            f"Portfolio risk posture is manageable (exposure {exposure_status}, "
            f"diversification {diversification_score:.0f}/100)."
        )

    agent_consensus = subagent_reviews.get("consensus_view", "Mixed Consensus")
    summary = (
        f"{research_mode} executive view for {symbol}: {headline_verdict}. "
        f"Agent consensus: {agent_consensus}. Human review remains required."
    )

    return {
        "headline_verdict": headline_verdict,
        "recommended_next_action": recommended_next_action,
        "suggested_paper_allocation": suggested_paper_allocation,
        "timing_view": timing_view,
        "top_reasons": top_reasons,
        "top_risks": top_risks,
        "portfolio_warning": portfolio_warning,
        "agent_consensus": agent_consensus,
        "human_review_required": True,
        "summary": summary,
    }
