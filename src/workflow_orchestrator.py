from time import perf_counter

from db_service import save_research_run


def run_research_workflow(
    symbol,
    price_data,
    snapshot,
    research_mode="Balanced",
):
    """Run a central research workflow with graceful step failure handling."""
    started = perf_counter()
    steps_completed = []
    steps_failed = []
    step_timings = {}
    outputs = {
        "risk": {},
        "signal": {},
        "regime": {},
        "news": {},
        "opportunity": {},
        "conviction": {},
        "alpha": {},
        "execution": {},
        "position_size": {},
        "entry_exit": {},
        "meta_decision": {},
    }

    def run_step(step_name, fn):
        t0 = perf_counter()
        try:
            result = fn()
            outputs[step_name] = result or {}
            steps_completed.append(step_name)
        except Exception as exc:
            steps_failed.append(f"{step_name}: {exc}")
            outputs[step_name] = {}
        step_timings[step_name] = round((perf_counter() - t0) * 1000, 2)

    # 1. risk metrics
    def _risk_step():
        from market_data import get_risk_metrics

        chart_input = price_data.get("data") if isinstance(price_data, dict) else price_data
        return get_risk_metrics(chart_input)

    run_step("risk", _risk_step)

    # 2. signal engine
    def _signal_step():
        from signal_engine import generate_signal

        return generate_signal(
            symbol,
            snapshot,
            outputs["risk"],
            news_context=outputs["news"] if outputs["news"] else None,
        )

    # 4. news engine (run before signal fallback context for better coverage)
    def _news_step():
        from news_engine import generate_news_context

        return generate_news_context(symbol)

    run_step("news", _news_step)
    run_step("signal", _signal_step)

    # 3. regime engine
    def _regime_step():
        from regime_engine import detect_market_regime

        return detect_market_regime(price_data, outputs["risk"])

    run_step("regime", _regime_step)

    # 5. opportunity engine (single-asset screen row)
    def _opportunity_step():
        from opportunity_engine import rank_opportunities

        row = {
            "symbol": symbol,
            "score": outputs["signal"].get("score", 50),
            "volatility_pct": outputs["risk"].get("volatility_pct", 0.0),
            "max_drawdown_pct": outputs["risk"].get("max_drawdown_pct", 0.0),
            "news_sentiment": outputs["news"].get("market_sentiment", "Neutral"),
            "signal": outputs["signal"].get("signal", "Watch"),
            "regime": outputs["regime"].get("regime", "Unknown"),
        }
        return rank_opportunities([row], research_mode=research_mode)

    run_step("opportunity", _opportunity_step)

    # 6. conviction engine
    def _conviction_step():
        from conviction_engine import calculate_conviction_score

        return calculate_conviction_score(
            signal_data=outputs["signal"],
            opportunity_data=outputs["opportunity"],
            thesis_health={"thesis_status": "Stable"},
            regime_data=outputs["regime"],
            news_context=outputs["news"],
            factor_attribution={"dominant_factor": {"factor": ""}, "risk_driver": {"factor": ""}},
            confidence_data={"adjusted_confidence": 5.0, "trust_level": "Moderate"},
            research_mode=research_mode,
        )

    run_step("conviction", _conviction_step)

    # 7. alpha engine
    def _alpha_step():
        from alpha_engine import analyze_alpha_vs_benchmark

        return analyze_alpha_vs_benchmark(symbol, price_data, benchmark_symbol="SPY", period="1mo")

    run_step("alpha", _alpha_step)

    # 8. execution readiness
    def _execution_step():
        from execution_engine import evaluate_execution_readiness

        return evaluate_execution_readiness(
            outputs["signal"],
            outputs["conviction"],
            outputs["opportunity"],
            outputs["alpha"],
            outputs["regime"],
            outputs["news"],
            {"conviction_risk": "Moderate"},
            outputs["risk"],
            research_mode=research_mode,
            confidence_data={"trust_level": "Moderate"},
        )

    run_step("execution", _execution_step)

    # 9. position sizing
    def _position_size_step():
        from position_sizing_engine import calculate_position_size

        return calculate_position_size(
            outputs["execution"],
            {
                "conviction_score": outputs["conviction"].get("conviction_score", 50),
                "confidence_level": "Moderate",
            },
            outputs["risk"],
            portfolio_value=100000,
            research_mode=research_mode,
        )

    run_step("position_size", _position_size_step)

    # 10. entry/exit
    def _entry_exit_step():
        from entry_exit_engine import generate_entry_exit_plan

        return generate_entry_exit_plan(
            outputs["execution"],
            outputs["conviction"],
            outputs["signal"],
            outputs["alpha"],
            outputs["risk"],
            position_data=None,
            research_mode=research_mode,
        )

    run_step("entry_exit", _entry_exit_step)

    # 11. meta decision
    def _meta_step():
        from meta_decision_engine import generate_meta_decision

        return generate_meta_decision(
            symbol=symbol,
            signal_data=outputs["signal"],
            conviction_data=outputs["conviction"],
            opportunity_data=outputs["opportunity"],
            alpha_data=outputs["alpha"],
            execution_data=outputs["execution"],
            position_size_data=outputs["position_size"],
            entry_exit_data=outputs["entry_exit"],
            regime_data=outputs["regime"],
            news_context=outputs["news"],
            catalyst_data={},
            scenario_data={},
            stress_test_data={},
            exposure_limits_data={},
            correlation_data={},
            capital_hierarchy_data={},
            strategy_comparison_data={},
            research_mode=research_mode,
        )

    run_step("meta_decision", _meta_step)

    workflow_runtime_ms = round((perf_counter() - started) * 1000, 2)
    if steps_completed and not steps_failed:
        workflow_status = "Complete"
    elif steps_completed:
        workflow_status = "Partial"
    else:
        workflow_status = "Failed"

    final_verdict = outputs.get("meta_decision", {}).get("final_verdict", "Watch")
    final_summary = (
        f"Workflow {workflow_status}. Completed {len(steps_completed)} step(s), "
        f"failed {len(steps_failed)} step(s). Final verdict: {final_verdict}."
    )

    # Optional DB integration: save a compact workflow snapshot.
    try:
        save_research_run(
            symbol=symbol,
            signal_score=outputs.get("signal", {}).get("score", 0),
            decision_score=outputs.get("meta_decision", {}).get("decision_score"),
            final_verdict=final_verdict,
            summary=final_summary,
            price=snapshot.get("price") if isinstance(snapshot, dict) else None,
            return_pct=outputs.get("risk", {}).get("return_pct"),
            volatility_pct=outputs.get("risk", {}).get("volatility_pct"),
            max_drawdown_pct=outputs.get("risk", {}).get("max_drawdown_pct"),
            regime=outputs.get("regime", {}).get("regime", ""),
            signal=outputs.get("signal", {}).get("signal", ""),
            exposure_level="",
            trade_decision=outputs.get("entry_exit", {}).get("recommended_action", ""),
            research_summary=final_summary,
        )
    except Exception:
        pass

    return {
        "workflow_status": workflow_status,
        "steps_completed": steps_completed,
        "steps_failed": steps_failed,
        "outputs": outputs,
        "final_summary": final_summary,
        "human_review_required": True,
        "workflow_runtime_ms": workflow_runtime_ms,
        "step_runtime_ms": step_timings,
    }
