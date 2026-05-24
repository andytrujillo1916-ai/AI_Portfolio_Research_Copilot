from pathlib import Path


def run_health_check():
    """Run simple import and core-output health checks for research-only development."""
    checks = []
    issues = []

    module_checks = [
        ("signal_engine", "generate_signal"),
        ("conviction_engine", "calculate_conviction_score"),
        ("meta_decision_engine", "generate_meta_decision"),
        ("backtester", "run_simple_backtest"),
        ("portfolio_optimizer", "generate_portfolio_allocation"),
        ("position_sizing_engine", "calculate_position_size"),
    ]

    loaded = {}
    for module_name, fn_name in module_checks:
        try:
            module = __import__(module_name, fromlist=[fn_name])
            fn = getattr(module, fn_name)
            loaded[(module_name, fn_name)] = fn
            checks.append(f"Imported {module_name}.{fn_name}")
        except Exception as exc:
            issues.append(f"Failed import {module_name}.{fn_name}: {exc}")

    data_dir = Path(__file__).resolve().parents[1] / "data"
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        checks.append(f"Data folder available at {data_dir}")
    except Exception as exc:
        issues.append(f"Failed to ensure data folder exists: {exc}")

    try:
        signal = loaded.get(("signal_engine", "generate_signal"))(
            "AAPL",
            {"price": 100.0, "change_pct": 1.0},
            {"return_pct": 2.0, "volatility_pct": 20.0, "max_drawdown_pct": -10.0},
            news_context={"market_sentiment": "Neutral", "event_tags": [], "risk_flags": []},
        )
        required = {"symbol", "signal", "score", "reasons", "risks"}
        if required.issubset(signal.keys()):
            checks.append("signal_engine.generate_signal returned required keys")
        else:
            issues.append("signal_engine.generate_signal missing required keys")
    except Exception as exc:
        issues.append(f"signal_engine.generate_signal check failed: {exc}")

    try:
        conviction = loaded.get(("conviction_engine", "calculate_conviction_score"))(
            signal_data={"score": 70},
            opportunity_data={"best_opportunity": {"opportunity_score": 60}},
            thesis_health={"thesis_status": "Stable"},
            regime_data={"regime": "Recovery"},
            news_context={"market_sentiment": "Neutral"},
            factor_attribution={"dominant_factor": {"factor": "Signal score quality"}, "risk_driver": {"factor": ""}},
            confidence_data={"adjusted_confidence": 6.0, "trust_level": "Moderate"},
            research_mode="Balanced",
        )
        score = float(conviction.get("conviction_score", -1))
        if 0 <= score <= 100:
            checks.append("conviction_engine.calculate_conviction_score returned valid range")
        else:
            issues.append("conviction_engine.calculate_conviction_score out of range")
    except Exception as exc:
        issues.append(f"conviction_engine.calculate_conviction_score check failed: {exc}")

    try:
        meta = loaded.get(("meta_decision_engine", "generate_meta_decision"))(
            symbol="AAPL",
            signal_data={"score": 70},
            conviction_data={"conviction_score": 65},
            opportunity_data={},
            alpha_data={"alpha_pct": 1.0},
            execution_data={"execution_score": 60, "readiness_level": "Watch"},
            position_size_data={},
            entry_exit_data={},
            regime_data={"regime": "Recovery"},
            news_context={"market_sentiment": "Neutral"},
            catalyst_data={"conviction_risk": "Moderate"},
            scenario_data={"overall_scenario_summary": "Mixed."},
            stress_test_data={"summary": "Moderate risk."},
            exposure_limits_data={"exposure_status": "Moderate"},
            correlation_data={"diversification_score": 60},
            capital_hierarchy_data={"top_capital_candidate": {"symbol": "AAPL"}},
            strategy_comparison_data={"best_strategy": {"strategy_name": "Trend Following Strategy"}},
            research_mode="Balanced",
        )
        if "final_verdict" in meta and "decision_score" in meta:
            checks.append("meta_decision_engine.generate_meta_decision returned required fields")
        else:
            issues.append("meta_decision_engine.generate_meta_decision missing required fields")
    except Exception as exc:
        issues.append(f"meta_decision_engine.generate_meta_decision check failed: {exc}")

    try:
        import pandas as pd

        sample = pd.DataFrame({"Date": pd.date_range("2026-01-01", periods=25, freq="D"), "Close": [100 + i for i in range(25)]})
        backtest = loaded.get(("backtester", "run_simple_backtest"))(sample)
        if "strategy_return_pct" in backtest:
            checks.append("backtester.run_simple_backtest returned expected output")
        else:
            issues.append("backtester.run_simple_backtest missing strategy_return_pct")
    except Exception as exc:
        issues.append(f"backtester.run_simple_backtest check failed: {exc}")

    try:
        alloc = loaded.get(("portfolio_optimizer", "generate_portfolio_allocation"))(
            [
                {"symbol": "AAPL", "score": 70, "volatility_pct": 20, "max_drawdown_pct": -10, "regime": "Bull Trend", "news_sentiment": "Neutral"},
                {"symbol": "XLV", "score": 60, "volatility_pct": 15, "max_drawdown_pct": -8, "regime": "Recovery", "news_sentiment": "Neutral"},
            ],
            research_mode="Balanced",
        )
        if isinstance(alloc.get("allocations", None), list):
            checks.append("portfolio_optimizer.generate_portfolio_allocation returned allocations")
        else:
            issues.append("portfolio_optimizer.generate_portfolio_allocation did not return allocations list")
    except Exception as exc:
        issues.append(f"portfolio_optimizer.generate_portfolio_allocation check failed: {exc}")

    try:
        sizing = loaded.get(("position_sizing_engine", "calculate_position_size"))(
            {"execution_score": 65, "readiness_level": "Near Ready"},
            {"conviction_score": 68, "confidence_level": "Moderate"},
            {"volatility_pct": 22, "max_drawdown_pct": -12},
            portfolio_value=100000,
            research_mode="Balanced",
        )
        if "recommended_position_pct" in sizing:
            checks.append("position_sizing_engine.calculate_position_size returned position percentage")
        else:
            issues.append("position_sizing_engine.calculate_position_size missing recommended_position_pct")
    except Exception as exc:
        issues.append(f"position_sizing_engine.calculate_position_size check failed: {exc}")

    status = "Healthy" if not issues else "Warning"
    summary = (
        f"Health check completed with {len(checks)} checks and {len(issues)} issue(s). "
        "This is a development safety check, not a trading or performance guarantee."
    )

    return {
        "status": status,
        "checks": checks,
        "issues": issues,
        "summary": summary,
    }
