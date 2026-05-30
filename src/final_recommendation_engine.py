def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _vote_action(vote):
    return str(vote.get("action") or vote.get("verdict") or vote.get("research_action") or "Watch")


def _normalize_action(action):
    action = str(action or "Watch")
    if action in {"Paper Buy Candidate", "Strong Research Candidate", "Research Candidate"}:
        return "Buy Candidate"
    if action in {"Strategic Buy Candidate"}:
        return "Buy Candidate"
    if action in {"Emerging Watchlist", "Speculative Research"}:
        return "Watch"
    if action in {"Needs Data", "Agent Research"}:
        return action
    if action in {"Watch Pullback", "Hold / Research", "Strong Watch"}:
        return "Watch"
    if action in {"Reduce Exposure", "Exit"}:
        return "Trim"
    if action in {"Thesis Broken"}:
        return "Sell Candidate"
    return action if action in {"Buy Candidate", "Add", "Hold", "Watch", "Wait for Pullback", "Needs Data", "Agent Research", "Trim", "Sell Candidate", "Avoid", "Keep Cash"} else "Watch"


def _display_value(value):
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.1f}"
    return str(value)


def build_final_recommendation(
    symbol,
    engine_votes,
    portfolio_context,
    data_quality,
    suitability,
    accuracy_context,
    ipo_context=None,
    growth_discovery_context=None,
    market_timing_context=None,
):
    """Resolve competing engine outputs into one canonical non-executing verdict."""
    symbol = str(symbol or "").upper()
    engine_votes = engine_votes or []
    portfolio_context = portfolio_context or {}
    data_quality = data_quality or {}
    suitability = suitability or {}
    accuracy_context = accuracy_context or {}
    ipo_context = ipo_context or {}
    growth_discovery_context = growth_discovery_context or {}
    market_timing_context = market_timing_context or {}

    conflict_rows = []
    raw_actions = []
    for vote in engine_votes:
        action = _normalize_action(_vote_action(vote))
        raw_actions.append(action)
        conflict_rows.append(
            {
                "engine": vote.get("engine", "Unknown"),
                "engine_view": action,
                "score": _display_value(vote.get("score", vote.get("decision_score", ""))),
                "reason": vote.get("reason", vote.get("summary", "")),
            }
        )

    score = _safe_float(portfolio_context.get("score"), 50.0)
    data_gate = data_quality.get("recommendation_gate", portfolio_context.get("recommendation_gate", "Warning"))
    data_confidence = data_quality.get("data_confidence", portfolio_context.get("data_confidence", "Unknown"))
    suitability_status = suitability.get("status", "Unknown")
    volatility = _safe_float(portfolio_context.get("volatility_pct"), 0.0)
    current_exposure = _safe_float(portfolio_context.get("current_exposure_pct"), 0.0)
    max_exposure = _safe_float(portfolio_context.get("max_single_stock_exposure"), 15.0)
    accuracy_adjustment = _safe_float(accuracy_context.get("confidence_adjustment"), 0.0)
    ipo_status = ipo_context.get("ipo_status", "")
    is_ipo_research_only = bool(ipo_context.get("research_only", False))
    market_risk_level = market_timing_context.get("market_risk_level", "")
    timing_regime = market_timing_context.get("timing_regime", "")
    strategic_buy_zones = market_timing_context.get("strategic_buy_zones", [])
    growth_label = growth_discovery_context.get("research_label", "")
    growth_score = _safe_float(growth_discovery_context.get("growth_score"), 0.0)

    reasons = []
    vetoes = []
    action_type = "review"

    positive_votes = sum(1 for action in raw_actions if action in {"Buy Candidate", "Add"})
    negative_votes = sum(1 for action in raw_actions if action in {"Avoid", "Sell Candidate", "Trim", "Keep Cash"})
    research_votes = sum(1 for action in raw_actions if action in {"Needs Data", "Agent Research"})

    if is_ipo_research_only:
        final = "Watch"
        vetoes.append("IPO is research-only until public listing and enough market data are available.")
    elif data_gate == "Blocked" or data_confidence == "Low":
        final = "Needs Data"
        vetoes.append("Data gate blocks buy/sell actions until better source data is available.")
    elif suitability_status == "De-risk first":
        final = "Keep Cash"
        vetoes.append("Suitability layer says de-risk before adding exposure.")
    elif current_exposure > max_exposure:
        final = "Trim"
        vetoes.append(f"Current exposure {current_exposure:.1f}% exceeds max single-position target {max_exposure:.1f}%.")
    elif volatility >= 35 and positive_votes:
        final = "Wait for Pullback"
        vetoes.append("High volatility downgrades positive votes to Watch.")
    elif growth_label == "Wait for Pullback" and positive_votes:
        final = "Wait for Pullback"
        reasons.append("Growth discovery is positive but timing/risk says wait for a better entry.")
    elif research_votes and positive_votes == 0 and score >= 45:
        final = "Agent Research"
        reasons.append("The setup is interesting enough for agent research but not buyable yet.")
    elif score < 40 or negative_votes > positive_votes:
        final = "Avoid" if not portfolio_context.get("has_position") else "Sell Candidate"
        reasons.append("Negative or weak evidence outweighs positive evidence.")
    elif positive_votes >= 2 and score >= 70 and growth_score >= 70:
        final = "Buy Candidate"
        reasons.append("Multiple engines align positively with acceptable score.")
    elif positive_votes >= 1 and score >= 60:
        final = "Add"
        reasons.append("Positive evidence exists, but not enough for highest conviction.")
    elif portfolio_context.get("has_position"):
        final = "Hold"
        reasons.append("Existing position does not trigger buy, trim, or sell rules.")
    else:
        final = "Watch"
        reasons.append("Evidence is mixed or incomplete.")

    if accuracy_adjustment <= -8 and final in {"Buy Candidate", "Add"}:
        final = "Watch"
        vetoes.append("Weak historical recommendation accuracy downgrades buy/add action.")

    if market_risk_level == "High" and final in {"Buy Candidate", "Add"}:
        final = "Wait for Pullback"
        vetoes.append("High market crash-risk conditions downgrade new-risk actions to Wait for Pullback.")
    elif market_risk_level == "Elevated" and final == "Buy Candidate":
        final = "Add"
        vetoes.append("Elevated market risk reduces Buy Candidate to a smaller Add-style review.")

    if final in {"Buy Candidate", "Add"}:
        action_type = "paper_buy_review"
    elif final in {"Trim", "Sell Candidate"}:
        action_type = "paper_sell_review"
    elif final == "Keep Cash":
        action_type = "cash"

    if final in {"Buy Candidate", "Add"} and score >= 75 and accuracy_adjustment >= 0:
        confidence = "High"
    elif final in {"Buy Candidate", "Add", "Hold", "Trim"} and score >= 55:
        confidence = "Moderate"
    else:
        confidence = "Low"

    paper_trade_eligible = (
        final in {"Buy Candidate", "Add", "Trim", "Sell Candidate"}
        and data_gate != "Blocked"
        and data_confidence != "Low"
        and suitability_status != "De-risk first"
        and not is_ipo_research_only
    )
    alert_eligible = final in {"Buy Candidate", "Add", "Trim", "Sell Candidate", "Hold", "Watch", "Needs Data", "Agent Research", "Avoid", "Keep Cash"}

    if not reasons and not vetoes:
        reasons.append("Final verdict is based on weighted evidence and current risk gates.")

    return {
        "symbol": symbol,
        "final_verdict": final,
        "confidence": confidence,
        "action_type": action_type,
        "time_horizon": portfolio_context.get("time_horizon", "Swing"),
        "position_guidance": portfolio_context.get("target_allocation_band", "Watchlist only"),
        "risk_budget": portfolio_context.get("risk_budget", "No new risk until reviewed."),
        "market_regime": timing_regime,
        "market_risk_level": market_risk_level,
        "strategic_buy_zone": strategic_buy_zones[0] if strategic_buy_zones else "",
        "source_confidence": data_confidence,
        "growth_discovery_label": growth_label,
        "growth_discovery_score": growth_score,
        "paper_trade_eligible": paper_trade_eligible,
        "alert_eligible": alert_eligible,
        "conflict_summary": (
            f"{len(set(raw_actions))} distinct engine view(s): {', '.join(sorted(set(raw_actions)))}."
            if raw_actions
            else "No engine votes available."
        ),
        "conflict_rows": conflict_rows,
        "vetoes": vetoes,
        "why": reasons,
        "what_would_change_this": [
            "Data gate improves to Trusted/Warning with fresh non-mock prices.",
            "Suitability status allows risk deployment.",
            "Volatility and drawdown fall inside risk budget.",
            "Recommendation accuracy improves or conflicting engine votes resolve.",
            "Market timing risk improves or a strategic buy zone is reached.",
        ],
        "ipo_status": ipo_status,
        "summary": (
            f"{symbol} final verdict is {final} ({confidence}). "
            "This is the source-of-truth action; other panels are evidence only."
        ),
    }
