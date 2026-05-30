def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def run_governance_review(
    meta_decision=None,
    conviction_data=None,
    execution_data=None,
    position_size_data=None,
    prediction_accuracy=None,
    benchmark_data=None,
    research_mode="Balanced",
):
    """Run a research-only governance and safety review across decision layers."""
    meta_decision = meta_decision or {}
    conviction_data = conviction_data or {}
    execution_data = execution_data or {}
    position_size_data = position_size_data or {}
    prediction_accuracy = prediction_accuracy or {}
    benchmark_data = benchmark_data or {}

    overconfidence_flags = []
    risk_flags = []
    required_disclaimers = []
    approval_notes = []

    conviction_score = _safe_float(conviction_data.get("conviction_score", 0.0))
    execution_score = _safe_float(execution_data.get("execution_score", 0.0))
    recommended_position = _safe_float(position_size_data.get("recommended_position_pct", 0.0))
    max_loss_tolerance = _safe_float(position_size_data.get("max_loss_tolerance_pct", 0.0))
    hit_rate = _safe_float(
        prediction_accuracy.get("hit_rate", prediction_accuracy.get("win_rate", 0.0))
    )
    avg_alpha = _safe_float(
        prediction_accuracy.get("alpha_vs_benchmark", benchmark_data.get("ai_outperformance_pct", 0.0))
    )
    avg_drawdown = abs(
        _safe_float(
            prediction_accuracy.get("avg_drawdown_after_signal", position_size_data.get("drawdown_pct", 0.0))
        )
    )
    total_predictions = int(
        _safe_float(
            prediction_accuracy.get("total_predictions", prediction_accuracy.get("sample_size", 0)),
            0,
        )
    )
    total_runs = int(_safe_float(prediction_accuracy.get("total_runs", 0), 0))

    # Evidence quality from sample depth.
    if total_predictions < 10 and total_runs < 10:
        evidence_quality = "Low"
    elif total_predictions < 25 or total_runs < 25:
        evidence_quality = "Medium"
    else:
        evidence_quality = "High"

    # Overconfidence: high confidence layers with weak empirical quality.
    if conviction_score >= 75 and hit_rate > 0 and hit_rate < 50:
        overconfidence_flags.append(
            "High conviction is not supported by prediction hit rate."
        )
    if execution_score >= 70 and avg_alpha < 0:
        overconfidence_flags.append(
            "High execution readiness conflicts with negative benchmark-relative alpha."
        )

    # Risk misalignment.
    if recommended_position >= 10 and avg_drawdown >= 12:
        risk_flags.append(
            "Suggested position size appears high relative to observed drawdown profile."
        )
    if max_loss_tolerance > 3 and research_mode == "Conservative":
        risk_flags.append(
            "Conservative mode appears to allow wider loss tolerance than expected."
        )
    if avg_alpha < 0:
        risk_flags.append(
            "Benchmark comparison is weak (negative alpha); require caution."
        )

    if evidence_quality == "Low":
        risk_flags.append(
            "Evidence quality is low due to limited saved predictions/research runs."
        )

    # Always require explicit disclaimers and human review.
    required_disclaimers.extend(
        [
            "Research-only decision support; not financial advice.",
            "No live trading approval. Paper-trading and human review only.",
            "No guaranteed returns or alpha claims.",
        ]
    )
    approval_notes.append("Human review is required before any paper-trade action.")
    approval_notes.append("Governance layer does not approve broker/API execution.")

    if overconfidence_flags or len(risk_flags) >= 2:
        governance_status = "High Risk"
    elif evidence_quality == "Low" or risk_flags:
        governance_status = "Needs Review"
    else:
        governance_status = "Approved for Research"

    summary = (
        f"Governance status: {governance_status}. "
        f"Evidence quality: {evidence_quality}. "
        f"Overconfidence flags: {len(overconfidence_flags)} | Risk flags: {len(risk_flags)}."
    )

    return {
        "governance_status": governance_status,
        "evidence_quality": evidence_quality,
        "overconfidence_flags": overconfidence_flags,
        "risk_flags": risk_flags,
        "required_disclaimers": required_disclaimers,
        "approval_notes": approval_notes,
        "summary": summary,
    }
