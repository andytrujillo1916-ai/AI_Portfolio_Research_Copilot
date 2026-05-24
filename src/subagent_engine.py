def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _status_from_score(score):
    if score >= 2:
        return "Supportive"
    if score == 1:
        return "Cautious"
    if score <= -1:
        return "Against"
    return "Needs Review"


def run_subagent_reviews(workflow_outputs, research_mode="Balanced"):
    """Run lightweight role-based reviews from orchestrated workflow outputs."""
    outputs = workflow_outputs or {}
    risk = outputs.get("risk", {}) or {}
    news = outputs.get("news", {}) or {}
    strategy = outputs.get("strategy_comparison", {}) or {}
    execution = outputs.get("execution", {}) or {}
    position_size = outputs.get("position_size", {}) or {}
    entry_exit = outputs.get("entry_exit", {}) or {}
    meta = outputs.get("meta_decision", {}) or {}
    conviction = outputs.get("conviction", {}) or {}
    opportunity = outputs.get("opportunity", {}) or {}
    exposure = outputs.get("exposure_limits", {}) or {}
    correlation = outputs.get("correlation", {}) or {}
    stress = outputs.get("stress_test", {}) or {}

    reviews = []

    # Market Data Agent
    vol = _safe_float(risk.get("volatility_pct", 0.0))
    dd = _safe_float(risk.get("max_drawdown_pct", 0.0))
    ret = _safe_float(risk.get("return_pct", 0.0))
    market_score = 0
    points = [f"Return context: {ret:+.2f}%.", f"Volatility: {vol:.2f}%.", f"Max drawdown: {dd:.2f}%."]
    concerns = []
    if ret > 0:
        market_score += 1
    else:
        concerns.append("Return trend is not currently positive.")
    if vol >= 30:
        market_score -= 1
        concerns.append("Volatility is elevated.")
    if dd <= -20:
        market_score -= 1
        concerns.append("Drawdown is deep.")
    reviews.append(
        {
            "agent_name": "Market Data Agent",
            "status": _status_from_score(market_score),
            "key_points": points,
            "concerns": concerns,
            "recommendation": "Use caution sizing if volatility/drawdown stay elevated.",
        }
    )

    # News Agent
    sentiment = str(news.get("market_sentiment", "Neutral"))
    risk_flags = news.get("risk_flags", []) or []
    event_tags = news.get("event_tags", []) or []
    news_score = 1 if sentiment == "Bullish" else -1 if sentiment == "Bearish" else 0
    if len(risk_flags) >= 2:
        news_score -= 1
    reviews.append(
        {
            "agent_name": "News Agent",
            "status": _status_from_score(news_score),
            "key_points": [
                f"Sentiment: {sentiment}.",
                f"Event tags: {', '.join(event_tags) if event_tags else 'None'}.",
            ],
            "concerns": [f"Risk flag: {flag}" for flag in risk_flags] if risk_flags else [],
            "recommendation": "Track catalysts and re-check if sentiment shifts.",
        }
    )

    # Strategy Agent
    best_strategy = (strategy.get("best_strategy") or {}).get("strategy_name", "Unknown")
    market_fit = strategy.get("market_fit", "Unknown")
    strat_score = 1 if best_strategy != "Unknown" else 0
    reviews.append(
        {
            "agent_name": "Strategy Agent",
            "status": _status_from_score(strat_score),
            "key_points": [f"Best strategy fit: {best_strategy}.", f"Market fit: {market_fit}"],
            "concerns": [] if best_strategy != "Unknown" else ["Strategy comparison context is limited."],
            "recommendation": "Prefer the highest-fit style while keeping research controls active.",
        }
    )

    # Risk Agent
    exposure_status = str(exposure.get("exposure_status", "Moderate"))
    div_score = _safe_float(correlation.get("diversification_score", 50.0))
    stress_summary = str(stress.get("summary", "No stress summary available."))
    risk_score = 0
    risk_concerns = []
    if exposure_status in {"Elevated", "High Risk"}:
        risk_score -= 1
        risk_concerns.append(f"Exposure status is {exposure_status}.")
    if div_score < 45:
        risk_score -= 1
        risk_concerns.append("Diversification is weak.")
    if vol >= 30:
        risk_score -= 1
        risk_concerns.append("Volatility remains high.")
    reviews.append(
        {
            "agent_name": "Risk Agent",
            "status": _status_from_score(risk_score),
            "key_points": [f"Exposure: {exposure_status}.", f"Diversification score: {div_score:.0f}/100.", stress_summary],
            "concerns": risk_concerns,
            "recommendation": "Reduce concentration and keep paper risk limits active.",
        }
    )

    # Portfolio Manager Agent
    conviction_score = _safe_float(conviction.get("conviction_score", 50))
    execution_score = _safe_float(execution.get("execution_score", 50))
    pos_pct = _safe_float(position_size.get("recommended_position_pct", 0))
    pm_score = 0
    pm_concerns = []
    if conviction_score >= 65:
        pm_score += 1
    else:
        pm_concerns.append("Conviction is not strong.")
    if execution_score >= 60:
        pm_score += 1
    else:
        pm_concerns.append("Execution readiness is not strong.")
    if pos_pct <= 0:
        pm_concerns.append("Position sizing suggests no exposure.")
        pm_score -= 1
    reviews.append(
        {
            "agent_name": "Portfolio Manager Agent",
            "status": _status_from_score(pm_score),
            "key_points": [
                f"Conviction score: {conviction_score:.1f}.",
                f"Execution score: {execution_score:.1f}.",
                f"Suggested size: {pos_pct:.2f}%.",
                f"Opportunity summary: {opportunity.get('summary', 'N/A')}",
            ],
            "concerns": pm_concerns,
            "recommendation": "Align sizing with readiness and keep diversification discipline.",
        }
    )

    # Safety Agent
    verdict = str(meta.get("final_verdict", "Watch"))
    summary_text = str(meta.get("summary", ""))
    lower_text = f"{verdict} {summary_text}".lower()
    safety_concerns = []
    if any(token in lower_text for token in ["guaranteed", "certain profit", "risk-free"]):
        safety_concerns.append("Language suggests certainty/guaranteed outcomes and must be revised.")
    if "buy now" in lower_text and "paper" not in lower_text:
        safety_concerns.append("Recommendation phrasing may imply live execution rather than research-only use.")
    if not safety_concerns:
        safety_status = "Supportive"
    else:
        safety_status = "Cautious"
    reviews.append(
        {
            "agent_name": "Safety Agent",
            "status": safety_status,
            "key_points": [
                "Research-only boundary checked.",
                "No broker API or auto-execution path should be used.",
            ],
            "concerns": safety_concerns,
            "recommendation": "Keep wording probabilistic and paper-trading only.",
        }
    )

    supportive = sum(1 for review in reviews if review["status"] == "Supportive")
    against = sum(1 for review in reviews if review["status"] == "Against")
    cautious = sum(1 for review in reviews if review["status"] == "Cautious")

    if against >= 2:
        consensus = "Cautious Consensus"
    elif supportive >= 4 and against == 0:
        consensus = "Supportive Consensus"
    else:
        consensus = "Mixed Consensus"

    disagreements = [r["agent_name"] for r in reviews if r["status"] in {"Against", "Needs Review"}]
    summary = (
        f"{consensus} under {research_mode} mode: "
        f"{supportive} supportive, {cautious} cautious, {against} against."
    )

    return {
        "agent_reviews": reviews,
        "consensus_view": consensus,
        "major_disagreements": disagreements,
        "human_review_required": True,
        "summary": summary,
    }
