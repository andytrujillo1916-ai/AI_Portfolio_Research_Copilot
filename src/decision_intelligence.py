def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, value))


def _risk_level(volatility, drawdown):
    drawdown = abs(drawdown)
    if volatility >= 35 or drawdown >= 25:
        return "High"
    if volatility >= 22 or drawdown >= 12:
        return "Medium"
    return "Low"


def _normalize_symbol(row):
    return row.get("symbol") or row.get("asset") or row.get("ticker") or ""


def _index_by_symbol(rows):
    indexed = {}
    if isinstance(rows, dict):
        for key, value in rows.items():
            if isinstance(value, dict):
                indexed[key] = value
        return indexed

    for row in rows or []:
        if isinstance(row, dict):
            symbol = _normalize_symbol(row)
            if symbol:
                indexed[symbol] = row
    return indexed


def _score_from_level(value, default=50.0):
    label = str(value or "").lower()
    if label in {"very high", "approved for research"}:
        return 90.0
    if label in {"high", "strong", "strengthening", "ready for paper trade"}:
        return 78.0
    if label in {"medium", "moderate", "stable", "needs review"}:
        return 58.0
    if label in {"low", "weak", "weakening", "not ready"}:
        return 35.0
    if label in {"broken", "high risk"}:
        return 12.0
    return default


def _extract_conviction(symbol, conviction_scores, ranked_row):
    if isinstance(conviction_scores, dict) and "conviction_score" in conviction_scores:
        return _safe_float(conviction_scores.get("conviction_score"), 50.0)

    indexed = _index_by_symbol(conviction_scores)
    row = indexed.get(symbol, {})
    return _safe_float(
        row.get(
            "conviction_score",
            ranked_row.get("conviction", ranked_row.get("opportunity_score", 50.0)),
        ),
        50.0,
    )


def _extract_thesis_strength(symbol, conviction_scores, ranked_row):
    thesis_status = ranked_row.get("thesis_health") or ranked_row.get("thesis_status")
    if isinstance(conviction_scores, dict):
        thesis_status = conviction_scores.get("thesis_status", thesis_status)
        thesis_status = conviction_scores.get("thesis_health", thesis_status)

    return _score_from_level(thesis_status, default=60.0), str(thesis_status or "Not tracked")


def _extract_benchmark_score(benchmark_truth):
    benchmark_truth = benchmark_truth or {}
    if "ai_outperformance_pct" in benchmark_truth:
        alpha = _safe_float(benchmark_truth.get("ai_outperformance_pct"), 0.0)
    elif "edge_vs_benchmark_pct" in benchmark_truth:
        alpha = _safe_float(benchmark_truth.get("edge_vs_benchmark_pct"), 0.0)
    else:
        alpha = _safe_float(benchmark_truth.get("alpha_vs_benchmark", 0.0), 0.0)

    score = _clamp(50 + (alpha * 4), 0, 100)
    if alpha > 2:
        label = "Benchmark truth is supportive."
    elif alpha < -2:
        label = "Benchmark truth is weak; confidence is reduced."
    else:
        label = "Benchmark truth is close to neutral."
    return score, label


def _extract_walk_forward_score(walk_forward_results):
    walk_forward_results = walk_forward_results or {}
    total_windows = _safe_float(walk_forward_results.get("total_windows", 0), 0)
    win_rate = _safe_float(walk_forward_results.get("win_rate_vs_spy", 0.0), 0.0)
    alpha = _safe_float(walk_forward_results.get("average_alpha_vs_spy", 0.0), 0.0)

    if total_windows <= 0:
        return 42.0, "Walk-forward stability is not available yet."

    score = _clamp((win_rate * 0.65) + ((50 + alpha * 5) * 0.35), 0, 100)
    if score >= 65:
        label = "Walk-forward stability is supportive."
    elif score <= 45:
        label = "Walk-forward stability is weak."
    else:
        label = "Walk-forward stability is mixed."
    return score, label


def _extract_governance_score(governance_review):
    governance_review = governance_review or {}
    status = governance_review.get("governance_status", "Needs Review")
    evidence = governance_review.get("evidence_quality", "Low")
    flags = len(governance_review.get("risk_flags", []) or [])
    overconfidence = len(governance_review.get("overconfidence_flags", []) or [])

    score = _score_from_level(status, default=55.0)
    score += {"High": 6, "Medium": 0, "Low": -10}.get(str(evidence), -6)
    score -= flags * 8
    score -= overconfidence * 10
    return _clamp(score, 0, 100), str(status)


def _extract_optimizer_context(symbol, portfolio_optimizer):
    portfolio_optimizer = portfolio_optimizer or {}
    allocations = (
        portfolio_optimizer.get("recommended_allocations")
        or portfolio_optimizer.get("allocations")
        or []
    )
    allocation = next((row for row in allocations if row.get("symbol") == symbol), {})
    weight = _safe_float(
        allocation.get("allocation_pct", allocation.get("weight_pct", 0.0)),
        0.0,
    )
    concentration = str(portfolio_optimizer.get("concentration_warning", ""))
    risk_level = str(portfolio_optimizer.get("portfolio_risk_level", "Unknown"))
    return weight, concentration, risk_level


def _research_action(score, governance_status, benchmark_score, volatility, thesis_status):
    thesis = str(thesis_status)
    if thesis == "Broken":
        return "Thesis Broken"
    if governance_status == "High Risk":
        return "Avoid" if score < 55 else "Hold / Research"
    if volatility >= 35 and _score_from_level(thesis, 50) < 50:
        return "Avoid"
    if score >= 76 and benchmark_score >= 50:
        return "Paper Buy Candidate"
    if score >= 64:
        return "Watch Pullback"
    if score >= 50:
        return "Hold / Research"
    if score >= 40:
        return "Reduce Exposure"
    if benchmark_score < 35:
        return "Short Research Candidate (research-only)"
    return "Avoid"


def _timing_view(score, volatility, benchmark_score, walk_score, signal_label):
    if volatility >= 35:
        return "High volatility; wait for cleaner evidence."
    if benchmark_score < 40:
        return "Benchmark truth is weak; require more proof."
    if walk_score < 45:
        return "Walk-forward results are unstable; slow down."
    if score >= 76 and str(signal_label) in {"Strong Watch", "Watch"}:
        return "Aligned research setup; monitor for paper-entry conditions."
    if score >= 60:
        return "Constructive but wait for pullback or stronger confirmation."
    return "Low urgency; keep in research queue."


def _position_size_hint(score, volatility, optimizer_weight, concentration_warning):
    if score < 50:
        return "No new paper size; review or reduce."
    if "concentrated" in str(concentration_warning).lower():
        return "Small paper size only; concentration review required."
    if volatility >= 35:
        return "Tiny paper size only due to high volatility."
    if optimizer_weight > 0:
        return f"Use optimizer as an upper research cap near {optimizer_weight:.1f}%."
    if score >= 76:
        return "Small starter paper position only after human review."
    return "Watchlist sizing only."


def build_quant_decision_intelligence(
    ranked_assets,
    conviction_scores,
    signal_outputs,
    benchmark_truth,
    portfolio_optimizer,
    governance_review,
    walk_forward_results,
    research_mode="Balanced",
):
    """Unify existing research engines into one explainable decision layer.

    This function orchestrates existing outputs only. It does not call broker APIs,
    place orders, or claim future returns.
    """
    ranked_assets = ranked_assets or []
    signal_by_symbol = _index_by_symbol(signal_outputs)
    benchmark_score, benchmark_note = _extract_benchmark_score(benchmark_truth)
    walk_score, walk_note = _extract_walk_forward_score(walk_forward_results)
    governance_score, governance_status = _extract_governance_score(governance_review)

    weights = {
        "conviction": 0.24,
        "signal_quality": 0.20,
        "walk_forward_stability": 0.14,
        "governance_safety": 0.14,
        "benchmark_truth": 0.12,
        "volatility_risk": 0.06,
        "concentration_risk": 0.05,
        "thesis_strength": 0.05,
    }

    opportunities = []
    source_rows = ranked_assets
    if isinstance(ranked_assets, dict):
        source_rows = ranked_assets.get("ranked_opportunities", [])

    for row in source_rows:
        if not isinstance(row, dict):
            continue

        symbol = _normalize_symbol(row)
        if not symbol:
            continue

        signal_row = signal_by_symbol.get(symbol, row)
        signal_score = _safe_float(
            signal_row.get("score", row.get("opportunity_score", row.get("conviction", 50))),
            50.0,
        )
        conviction = _extract_conviction(symbol, conviction_scores, row)
        volatility = _safe_float(
            signal_row.get("volatility_pct", row.get("volatility_pct", 0.0)),
            0.0,
        )
        drawdown = _safe_float(
            signal_row.get("max_drawdown_pct", row.get("max_drawdown_pct", 0.0)),
            0.0,
        )
        thesis_score, thesis_status = _extract_thesis_strength(symbol, conviction_scores, row)
        optimizer_weight, concentration_warning, portfolio_risk = _extract_optimizer_context(
            symbol,
            portfolio_optimizer,
        )

        volatility_quality = 100 - (volatility * 2.0)
        if drawdown < 0:
            volatility_quality -= abs(drawdown)
        concentration_quality = 45.0 if optimizer_weight >= 25 else 65.0
        if "concentrated" in concentration_warning.lower():
            concentration_quality -= 15

        decision_score = (
            conviction * weights["conviction"]
            + signal_score * weights["signal_quality"]
            + walk_score * weights["walk_forward_stability"]
            + governance_score * weights["governance_safety"]
            + benchmark_score * weights["benchmark_truth"]
            + _clamp(volatility_quality) * weights["volatility_risk"]
            + _clamp(concentration_quality) * weights["concentration_risk"]
            + thesis_score * weights["thesis_strength"]
        )

        if benchmark_score < 40:
            decision_score -= 8
        if governance_status == "High Risk":
            decision_score -= 12
        if volatility >= 35 and thesis_score < 50:
            decision_score -= 10

        decision_score = round(_clamp(decision_score), 1)
        signal_label = signal_row.get("signal", row.get("research_action", "Unknown"))
        action = _research_action(
            decision_score,
            governance_status,
            benchmark_score,
            volatility,
            thesis_status,
        )

        why = [
            f"Conviction contributes {weights['conviction']:.0%} of the transparent score.",
            f"Signal quality contributes {weights['signal_quality']:.0%}; current signal score is {signal_score:.1f}.",
            walk_note,
            benchmark_note,
            f"Governance status is {governance_status}.",
        ]
        risk = _risk_level(volatility, drawdown)
        if risk == "High":
            why.append("Volatility/drawdown risk is high, so confidence is capped.")
        if thesis_status != "Not tracked":
            why.append(f"Thesis health is {thesis_status}.")
        if concentration_warning:
            why.append(concentration_warning)

        opportunities.append(
            {
                "symbol": symbol,
                "priority_rank": 0,
                "decision_score": decision_score,
                "research_action": action,
                "timing_view": _timing_view(
                    decision_score,
                    volatility,
                    benchmark_score,
                    walk_score,
                    signal_label,
                ),
                "position_size_hint": _position_size_hint(
                    decision_score,
                    volatility,
                    optimizer_weight,
                    concentration_warning,
                ),
                "why": why,
            }
        )

    opportunities.sort(key=lambda item: item.get("decision_score", 0), reverse=True)
    for rank, row in enumerate(opportunities, start=1):
        row["priority_rank"] = rank

    top_score = opportunities[0]["decision_score"] if opportunities else 0
    if governance_status == "High Risk":
        portfolio_stance = "Defensive research stance"
    elif top_score >= 75 and benchmark_score >= 50:
        portfolio_stance = "Selective paper-risk-on research stance"
    elif top_score >= 58:
        portfolio_stance = "Balanced watchlist stance"
    else:
        portfolio_stance = "Capital preservation research stance"

    if top_score >= 75:
        capital_view = "Deploy only small paper allocations into highest-ranked candidates after human review."
    elif top_score >= 58:
        capital_view = "Keep most capital in reserve; build watchlist and wait for stronger alignment."
    else:
        capital_view = "Do not add new paper exposure from this layer; focus on research and validation."

    risk_summary = (
        f"Portfolio optimizer risk is {portfolio_optimizer.get('portfolio_risk_level', 'Unknown') if isinstance(portfolio_optimizer, dict) else 'Unknown'}. "
        f"Governance is {governance_status}. Human review remains required."
    )
    benchmark_summary = (
        f"{benchmark_note} Score uses benchmark truth at {weights['benchmark_truth']:.0%} weight "
        "so weak passive comparison reduces confidence."
    )
    summary = (
        f"Quant Decision Intelligence ranked {len(opportunities)} opportunity/opportunities in "
        f"{research_mode} mode using transparent weights across conviction, signals, stability, "
        "governance, benchmark truth, risk, concentration, and thesis strength. Research-only; "
        "no live trading, broker APIs, auto execution, guaranteed returns, or buy-now certainty."
    )

    return {
        "best_opportunities": opportunities,
        "portfolio_stance": portfolio_stance,
        "capital_deployment_view": capital_view,
        "risk_summary": risk_summary,
        "benchmark_truth_summary": benchmark_summary,
        "human_review_required": True,
        "summary": summary,
    }
