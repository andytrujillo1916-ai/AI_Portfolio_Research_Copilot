from datetime import datetime

import streamlit as st

from backtester import run_simple_backtest, run_strategy_lab
from market_data import get_market_snapshot, get_price_history, get_watchlist
from news_engine import generate_news_context
from paper_trader import calculate_paper_performance, calculate_paper_positions
from trade_decision_assistant import generate_trade_decision
from adaptive_learning_engine import calculate_factor_insights
from prediction_log import evaluate_all_predictions, load_predictions
from prediction_accuracy_engine import evaluate_prediction_accuracy
from regime_engine import detect_market_regime
from research_agent import generate_research_summary
from research_run_log import evaluate_research_runs, load_research_runs
from screener_engine import run_cross_asset_screen
from macro_engine import generate_macro_context
from sector_rotation_engine import analyze_sector_rotation
from signal_engine import generate_signal
from portfolio_optimizer import generate_portfolio_allocation
from opportunity_engine import rank_opportunities
from scenario_engine import run_scenarios
from stress_test_engine import run_stress_tests
from factor_engine import analyze_factor_attribution
from thesis_engine import evaluate_thesis_health
from confidence_engine import calculate_confidence_adjustment
from conviction_engine import calculate_conviction_score
from catalyst_engine import generate_catalyst_tracker
from asset_class_engine import classify_asset
from strategy_comparison_engine import compare_strategies
from allocation_timing_engine import generate_allocation_timing_recommendation
from alpha_engine import analyze_alpha_vs_benchmark
from execution_engine import evaluate_execution_readiness
from position_sizing_engine import calculate_position_size as calculate_position_size_engine
from entry_exit_engine import generate_entry_exit_plan
from exposure_limits_engine import evaluate_portfolio_exposure_limits
from correlation_engine import analyze_cross_asset_correlation
from meta_decision_engine import generate_meta_decision
from subagent_engine import run_subagent_reviews
from benchmark_basket_engine import find_best_etf_benchmark
from strategy_scorecard_engine import generate_strategy_scorecard
from experiment_tracker import load_experiments
from benchmark_engine import compare_to_benchmarks
from data_quality_engine import evaluate_data_quality
from decision_intelligence import build_quant_decision_intelligence
from explainable_quant_engine import compare_etf_benchmarks
from governance_engine import run_governance_review
from portfolio_optimizer import optimize_portfolio
from walk_forward_engine import run_walk_forward_validation
from alternative_data_engine import generate_alternative_data_context
from db_service import load_financial_profile, load_real_holdings
from growth_discovery_engine import score_growth_discovery
from market_timing_engine import build_market_timing_context
from ui_sections import (
    render_asset_comparison,
    render_cross_asset_screener_from_rows,
    render_data_source_quality_dashboard,
    render_data_source_status,
    render_financial_profile_form,
    render_final_recommendation_panel,
    render_ipo_research,
    render_broker_alert_tickets,
    render_buy_finder_terminal,
    render_opportunity_terminal,
    render_opportunistic_stock_screener,
    render_opportunity_engine,
    render_watchlist_drift_engine,
    render_cross_asset_screener,
    render_market_snapshot,
    render_asset_class_context,
    render_best_opportunities_workstation,
    render_macro_dashboard,
    render_sector_rotation,
    render_price_chart,
    render_market_regime,
    render_backtest_section,
    render_news_intelligence,
    render_prediction_log,
    render_prediction_evaluation,
    render_decision_journal,
    render_experiment_tracker,
    render_research_review_agent,
    render_governance_review,
    render_research_packet_exporter,
    render_research_quality_audit,
    render_market_stress_research,
    render_research_agent,
    render_alternative_data_context,
    render_fundamental_catalyst_quality,
    render_research_brief,
    render_daily_research_report,
    render_thesis_tracker,
    render_conviction_engine,
    render_catalyst_tracker,
    render_scenario_engine,
    render_factor_attribution,
    render_signal_engine,
    render_strategy_lab,
    render_strategy_comparison_engine,
    render_walk_forward_section,
    render_walk_forward_validation,
    render_strategy_leaderboard,
    render_portfolio_simulator,
    render_portfolio_optimizer,
    render_portfolio_optimizer_v1,
    render_benchmark_truth,
    render_rebalance_advisor,
    render_exposure_limits_engine,
    render_correlation_engine,
    render_capital_hierarchy_engine,
    render_allocation_timing_recommendation,
    render_best_etf_benchmark,
    render_strategy_scorecard,
    render_auto_paper_trading_control_panel,
    render_alpha_engine,
    render_execution_readiness,
    render_position_sizing_engine,
    render_entry_exit_framework,
    render_meta_decision_engine,
    render_paper_trading_simulator,
    render_stress_test_engine,
    render_trade_decision_assistant,
    render_confidence_engine,
    render_risk_engine,
    render_exposure_engine,
    render_save_research_run,
    render_research_run_evaluation,
    render_adaptive_learning,
    render_learning_engine,
    render_agent_task_runner,
    render_agent_research_desk,
    render_research_journal,
    render_research_notes,
    render_workflow_orchestrator,
    render_subagent_reviews,
    render_executive_dashboard,
    render_quant_decision_intelligence,
    render_ranked_quant_decision_table,
    render_real_portfolio_editor,
    render_sp500_strategy_scan,
    render_portfolio_strategy_advisor,
    render_recommendation_learning_dashboard,
    render_recommendation_logger,
    render_explainability_panel,
    render_timing_explanation,
    render_position_sizing_modes,
    render_etf_benchmark_dashboard,
    render_prediction_accuracy_dashboard,
    render_health_check,
    render_database_status,
    render_roadmap,
)

st.set_page_config(page_title="AI Portfolio Research Copilot", layout="wide")

st.title("AI Portfolio Research Copilot")
st.write(
    "Research-only AI quant workstation for market analysis, strategy testing, and paper-trade decision support."
)

watchlist = get_watchlist()
period_options = ["5d", "1mo", "3mo", "6mo", "1y"]
research_modes = ["Conservative", "Balanced", "Aggressive"]
analysis_depth_options = ["Quick", "Standard", "Deep"]

# Shared research control state
if "selected_asset" not in st.session_state:
    st.session_state.selected_asset = watchlist[0] if watchlist else ""
if "period" not in st.session_state:
    st.session_state.period = "1mo"
if "shares" not in st.session_state:
    st.session_state.shares = 0.0
if "research_mode" not in st.session_state:
    st.session_state.research_mode = "Balanced"
if "analysis_depth" not in st.session_state:
    st.session_state.analysis_depth = "Standard"
if "last_run_timestamp" not in st.session_state:
    st.session_state.last_run_timestamp = "Never"
if "run_full_research" not in st.session_state:
    st.session_state.run_full_research = False

st.sidebar.header("Research Control Panel")

selected_asset = st.sidebar.selectbox(
    "Selected Asset",
    watchlist,
    index=watchlist.index(st.session_state.selected_asset)
    if st.session_state.selected_asset in watchlist
    else 0,
)
period = st.sidebar.selectbox(
    "Period",
    period_options,
    index=period_options.index(st.session_state.period)
    if st.session_state.period in period_options
    else 1,
)
shares = st.sidebar.number_input(
    "Shares Owned",
    min_value=0.0,
    value=float(st.session_state.shares),
    step=1.0,
)
research_mode = st.sidebar.selectbox(
    "Research Mode",
    research_modes,
    index=research_modes.index(st.session_state.research_mode),
)
analysis_depth = st.sidebar.selectbox(
    "Analysis Depth",
    analysis_depth_options,
    index=analysis_depth_options.index(st.session_state.analysis_depth),
)
run_full_research_clicked = st.sidebar.button("Run Full Research")

st.session_state.selected_asset = selected_asset
st.session_state.period = period
st.session_state.shares = shares
st.session_state.research_mode = research_mode
st.session_state.analysis_depth = analysis_depth
if run_full_research_clicked:
    st.session_state.run_full_research = True
    st.session_state.last_run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

snapshot = get_market_snapshot(selected_asset)
price_data = get_price_history(selected_asset, period=period)
data_source = (
    price_data.get("source")
    if isinstance(price_data, dict) and "source" in price_data
    else snapshot.get("source", "unknown")
)

st.sidebar.header("System Status")
st.sidebar.write(f"**Data source:** {data_source}")
st.sidebar.write(f"**Current asset:** {selected_asset}")
st.sidebar.write(f"**Selected period:** {period}")
st.sidebar.markdown("### Current Research State")
st.sidebar.write(f"- Asset: {st.session_state.selected_asset}")
st.sidebar.write(f"- Mode: {st.session_state.research_mode}")
st.sidebar.write(f"- Depth: {st.session_state.analysis_depth}")
st.sidebar.write(f"- Period: {st.session_state.period}")
st.sidebar.write(f"- Last run: {st.session_state.last_run_timestamp}")

# Compute shared data once before rendering tabs.
risk = {
    "return_pct": 0.0,
    "volatility_pct": 0.0,
    "max_drawdown_pct": 0.0,
}
try:
    from market_data import get_risk_metrics

    chart_input = price_data.get("data") if isinstance(price_data, dict) else price_data
    risk = get_risk_metrics(chart_input)
except Exception:
    pass

current_prices_by_symbol = {
    asset: get_market_snapshot(asset).get("price", 0.0) for asset in watchlist
}
paper_positions = calculate_paper_positions(current_prices_by_symbol)
paper_performance = calculate_paper_performance(current_prices_by_symbol)
news_context = generate_news_context(selected_asset)
alternative_data_context = generate_alternative_data_context(selected_asset)
backtest_results = run_simple_backtest(price_data)
strategy_lab_results = run_strategy_lab(price_data)
regime_data = detect_market_regime(price_data, risk)
evaluation_summary = evaluate_all_predictions(selected_asset, snapshot.get("price"))
adaptive_learning = calculate_factor_insights(load_predictions(), load_research_runs())
screened_assets = run_cross_asset_screen(watchlist, period=period)
macro_context = generate_macro_context(research_mode=research_mode)
sector_context = analyze_sector_rotation(period=period, research_mode=research_mode)
asset_class_context = classify_asset(selected_asset)
signal_data = generate_signal(
    selected_asset,
    snapshot,
    risk,
    news_context=news_context,
    asset_class=asset_class_context,
    alternative_data_context=alternative_data_context,
)
decision = generate_trade_decision(
    selected_asset,
    snapshot,
    risk,
    signal_data,
    news_context,
    backtest_results,
    paper_positions,
)
optimizer_result = generate_portfolio_allocation(
    screened_assets,
    research_mode=research_mode,
    sector_context=sector_context,
)
recommended_allocations = optimizer_result.get("allocations", [])
opportunity_data = rank_opportunities(
    screened_assets,
    research_mode=research_mode,
    sector_context=sector_context,
)
selected_screen_row = next(
    (row for row in screened_assets if row.get("symbol") == selected_asset),
    {},
)
selected_data_confidence = selected_screen_row.get("data_confidence", "Medium")
benchmark_basket_data = find_best_etf_benchmark(period=period)
paper_scorecard = generate_strategy_scorecard(
    paper_performance,
    benchmark_basket_data,
    paper_positions=paper_positions,
)
benchmark_results = {
    "strategy_return_pct": float(backtest_results.get("strategy_return_pct", 0.0)),
    "benchmark_return_pct": float(backtest_results.get("buy_and_hold_return_pct", 0.0)),
    "edge_vs_benchmark_pct": float(backtest_results.get("strategy_return_pct", 0.0))
    - float(backtest_results.get("buy_and_hold_return_pct", 0.0)),
}
strategy_results = strategy_lab_results.get("strategy_results", [])
buy_hold_return = 0.0
for strategy in strategy_results:
    if strategy.get("strategy_name") == "Buy & Hold":
        buy_hold_return = strategy.get("return_pct", 0.0)

strategy_beats_buy_hold = any(
    strategy.get("strategy_name") != "Buy & Hold"
    and strategy.get("return_pct", 0.0) > buy_hold_return
    for strategy in strategy_results
)
if strategy_results and strategy_beats_buy_hold:
    adaptive_learning["strategy_consistency"] = "Improving"
elif strategy_results:
    adaptive_learning["strategy_consistency"] = "Weak"
else:
    adaptive_learning["strategy_consistency"] = "Unknown"

current_symbol_exposure = paper_positions.get("positions", {}).get(selected_asset, {}).get(
    "market_value", 0.0
)
if current_symbol_exposure == 0 and shares:
    current_symbol_exposure = shares * snapshot.get("price", 0.0)

portfolio_value = paper_positions.get("market_value", 0.0)
if portfolio_value <= 0:
    portfolio_value = max(1000.0, current_symbol_exposure)

exposure_pct = 0.0
if portfolio_value > 0:
    exposure_pct = (current_symbol_exposure / portfolio_value) * 100

if exposure_pct >= 30:
    exposure_level = "High"
elif exposure_pct >= 15:
    exposure_level = "Medium"
elif exposure_pct > 0:
    exposure_level = "Low"
else:
    exposure_level = "None"

exposure_data = {
    "current_symbol_exposure": current_symbol_exposure,
    "total_portfolio_value": portfolio_value,
    "exposure_pct": exposure_pct,
    "exposure_level": exposure_level,
}

notes = ""
research_memo = generate_research_summary(selected_asset, snapshot, risk, notes=notes)

# Research mode context: pass lightweight context without rewriting strategy logic.
mode_confidence_offset = 0.0
mode_position_multiplier = 1.0
mode_caution_note = "Balanced mode keeps the default research posture."
if research_mode == "Conservative":
    mode_confidence_offset = -1.0
    mode_position_multiplier = 0.8
    mode_caution_note = "Conservative mode lowers confidence and position tolerance."
elif research_mode == "Aggressive":
    mode_confidence_offset = 0.5
    mode_position_multiplier = 1.1
    mode_caution_note = "Aggressive mode slightly increases trust and risk tolerance."

mode_adjusted_confidence = max(1, min(10, decision.get("confidence", 5) + mode_confidence_offset)) if "decision" in locals() else 5
mode_adjusted_portfolio_value = portfolio_value * mode_position_multiplier

# Executive summary inputs (pre-tab, research-only, graceful fallback-friendly).
strategy_comparison_exec = compare_strategies(
    price_data,
    risk,
    regime_data,
    signal_data,
    research_mode=research_mode,
)
thesis_health_exec = evaluate_thesis_health(
    selected_asset,
    snapshot.get("price"),
    signal_data,
    regime_data,
    news_context,
)
confidence_exec = calculate_confidence_adjustment(
    signal_data,
    evaluation_summary,
    regime_data,
    adaptive_learning,
    research_mode=research_mode,
    analysis_depth=analysis_depth,
)
conviction_exec = calculate_conviction_score(
    signal_data,
    opportunity_data,
    thesis_health_exec,
    regime_data,
    news_context,
    {"dominant_factor": {"factor": ""}, "risk_driver": {"factor": ""}},
    confidence_exec,
    research_mode=research_mode,
)
catalyst_exec = generate_catalyst_tracker(
    selected_asset,
    news_context,
    thesis_health_exec,
    conviction_exec,
)
allocation_timing_exec = generate_allocation_timing_recommendation(
    selected_asset,
    conviction_exec,
    signal_data,
    opportunity_data,
    regime_data,
    news_context,
    catalyst_exec,
    backtest_results,
    strategy_lab_results,
    benchmark_results,
    risk,
    research_mode=research_mode,
)
alpha_exec = analyze_alpha_vs_benchmark(
    selected_asset,
    price_data,
    paper_trade_results=paper_positions,
    benchmark_symbol="SPY",
    period=period,
)
execution_exec = evaluate_execution_readiness(
    signal_data,
    conviction_exec,
    opportunity_data,
    alpha_exec,
    regime_data,
    news_context,
    catalyst_exec,
    risk,
    research_mode=research_mode,
    confidence_data=confidence_exec,
)
position_size_exec = calculate_position_size_engine(
    execution_exec,
    {
        "conviction_score": conviction_exec.get("conviction_score", 0),
        "confidence_level": confidence_exec.get("trust_level", "Moderate"),
    },
    risk,
    portfolio_value=portfolio_value,
    research_mode=research_mode,
)
entry_exit_exec = generate_entry_exit_plan(
    execution_exec,
    conviction_exec,
    signal_data,
    alpha_exec,
    risk,
    position_data=None,
    research_mode=research_mode,
)
exposure_limits_exec = evaluate_portfolio_exposure_limits(
    recommended_allocations,
    screened_assets,
    conviction_data=conviction_exec,
    research_mode=research_mode,
)
correlation_exec = analyze_cross_asset_correlation(
    screened_assets,
    portfolio_allocations=recommended_allocations,
    research_mode=research_mode,
)
meta_decision_exec = generate_meta_decision(
    symbol=selected_asset,
    signal_data=signal_data,
    conviction_data=conviction_exec,
    opportunity_data=opportunity_data,
    alpha_data=alpha_exec,
    execution_data=execution_exec,
    position_size_data=position_size_exec,
    entry_exit_data=entry_exit_exec,
    regime_data=regime_data,
    news_context=news_context,
    catalyst_data=catalyst_exec,
    scenario_data={},
    stress_test_data={},
    exposure_limits_data=exposure_limits_exec,
    correlation_data=correlation_exec,
    capital_hierarchy_data={},
    strategy_comparison_data=strategy_comparison_exec,
    research_mode=research_mode,
)
subagent_reviews_exec = run_subagent_reviews(
    {
        "risk": risk,
        "news": news_context,
        "strategy_comparison": strategy_comparison_exec,
        "execution": execution_exec,
        "position_size": position_size_exec,
        "entry_exit": entry_exit_exec,
        "meta_decision": meta_decision_exec,
        "conviction": conviction_exec,
        "opportunity": opportunity_data,
        "exposure_limits": exposure_limits_exec,
        "correlation": correlation_exec,
        "stress_test": {},
    },
    research_mode=research_mode,
)

stress_test_results = run_stress_tests(paper_positions)
scenario_results = run_scenarios(
    selected_asset,
    risk,
    signal_data,
    news_context,
    regime_data,
    exposure_data=exposure_data,
)
factor_attribution_exec = analyze_factor_attribution(
    screened_assets,
    portfolio_allocations=recommended_allocations,
    research_mode=research_mode,
)
decision_ranked_assets = []
opportunity_by_symbol = {
    row.get("symbol"): row for row in opportunity_data.get("ranked_opportunities", [])
}
for row in screened_assets:
    symbol = row.get("symbol", "")
    opportunity_row = opportunity_by_symbol.get(symbol, {})
    decision_ranked_assets.append(
        {
            **row,
            "opportunity_score": opportunity_row.get(
                "opportunity_score",
                row.get("score", 50),
            ),
            "priority": opportunity_row.get("priority", "Medium"),
            "reasoning": opportunity_row.get("reasoning", ""),
        }
    )
decision_ranked_assets.sort(
    key=lambda row: row.get("opportunity_score", row.get("score", 0)),
    reverse=True,
)
conviction_inputs = [{"symbol": selected_asset, **conviction_exec}]
optimizer_v1_exec = optimize_portfolio(
    decision_ranked_assets,
    research_mode=research_mode,
)
benchmark_comparison_exec = compare_etf_benchmarks(period=period)
benchmark_truth_exec = compare_to_benchmarks(
    paper_performance,
    benchmark_comparison_exec,
)
walk_forward_validation_exec = run_walk_forward_validation(
    watchlist,
    research_mode=research_mode,
    period=period,
)
prediction_summary_exec = evaluate_prediction_accuracy(
    load_predictions(),
    benchmark_returns=benchmark_basket_data,
)
prediction_summary_exec["total_predictions"] = len(load_predictions())
research_run_summary_exec = evaluate_research_runs(
    selected_asset,
    snapshot.get("price"),
)
prediction_summary_exec["total_runs"] = research_run_summary_exec.get("total_runs", 0)
governance_review_exec = run_governance_review(
    meta_decision=meta_decision_exec,
    conviction_data=conviction_exec,
    execution_data=execution_exec,
    position_size_data=position_size_exec,
    prediction_accuracy=prediction_summary_exec,
    benchmark_data=benchmark_truth_exec,
    research_mode=research_mode,
)
quant_decision_exec = build_quant_decision_intelligence(
    decision_ranked_assets,
    conviction_inputs,
    screened_assets,
    benchmark_truth_exec,
    optimizer_v1_exec,
    governance_review_exec,
    walk_forward_validation_exec,
    research_mode=research_mode,
)
snapshot_quality_exec = evaluate_data_quality(snapshot)
price_quality_exec = evaluate_data_quality(price_data)
selected_data_quality_exec = {
    "data_confidence": "Low"
    if "Low" in {snapshot_quality_exec.get("data_confidence"), price_quality_exec.get("data_confidence")}
    else "Medium"
    if "Medium" in {snapshot_quality_exec.get("data_confidence"), price_quality_exec.get("data_confidence")}
    else "High",
    "recommendation_gate": "Blocked"
    if "Blocked" in {snapshot_quality_exec.get("recommendation_gate"), price_quality_exec.get("recommendation_gate")}
    else "Warning"
    if "Warning" in {snapshot_quality_exec.get("recommendation_gate"), price_quality_exec.get("recommendation_gate")}
    else "Trusted",
    "status": price_quality_exec.get("status", snapshot_quality_exec.get("status", "Unknown")),
    "summary": " | ".join(snapshot_quality_exec.get("issues", []) + price_quality_exec.get("issues", [])),
}
stored_financial_profile_exec = load_financial_profile()
opportunity_terminal_rows_exec = st.session_state.get("opportunity_terminal_rows", [])
opportunity_scan_rows_exec = opportunity_terminal_rows_exec or screened_assets
selected_opportunity_row_exec = next(
    (row for row in opportunity_scan_rows_exec if row.get("symbol") == selected_asset),
    selected_screen_row,
)
selected_growth_discovery_exec = score_growth_discovery(
    selected_asset,
    selected_opportunity_row_exec or selected_screen_row,
    fundamentals={},
    catalysts=catalyst_exec,
    alt_data=alternative_data_context,
    source_quality=selected_data_quality_exec,
)
market_timing_exec = build_market_timing_context(
    {"rows": [row for row in opportunity_scan_rows_exec if row.get("symbol") in {"SPY", "QQQ", "IWM"}]},
    opportunity_scan_rows_exec,
    sector_context,
    macro_context,
    stored_financial_profile_exec,
)

(
    tab_buy_finder,
    tab_opportunity,
    tab_executive,
    tab_decision,
    tab_timing,
    tab_portfolio,
    tab_etf,
    tab_accuracy,
    tab_strategy,
    tab_journal,
    tab_agents,
    tab_health,
) = st.tabs(
    [
        "Buy Finder",
        "Opportunity Terminal",
        "Executive Dashboard",
        "Decision Breakdown",
        "Timing & Position Sizing",
        "Portfolio Lab",
        "ETF Benchmark",
        "Prediction Accuracy",
        "Strategy Lab",
        "Journal",
        "Agent Research Desk",
        "System Health",
    ]
)

with tab_buy_finder:
    opportunity_terminal_context = render_opportunity_terminal(
        period,
        default_rows=screened_assets,
        financial_profile=stored_financial_profile_exec,
        sector_context=sector_context,
        macro_context=macro_context,
        key_suffix="buy_finder_opportunity",
    )
    buy_finder_rows = opportunity_terminal_context.get("rows", opportunity_scan_rows_exec)
    buy_finder_timing = opportunity_terminal_context.get("market_timing", market_timing_exec)
    render_buy_finder_terminal(
        buy_finder_rows,
        buy_finder_timing,
        stored_financial_profile_exec,
        load_real_holdings(),
        accuracy_context=prediction_summary_exec,
        key_suffix="buy_finder_tab",
    )

with tab_opportunity:
    opportunity_terminal_context = render_opportunity_terminal(
        period,
        default_rows=screened_assets,
        financial_profile=stored_financial_profile_exec,
        sector_context=sector_context,
        macro_context=macro_context,
        key_suffix="opportunity_tab",
    )
    opportunity_scan_rows_exec = opportunity_terminal_context.get("rows", opportunity_scan_rows_exec)
    market_timing_exec = opportunity_terminal_context.get("market_timing", market_timing_exec)
    render_best_opportunities_workstation(
        opportunity_scan_rows_exec,
        financial_profile=stored_financial_profile_exec,
        accuracy_context=prediction_summary_exec,
        market_timing=market_timing_exec,
        selected_asset=selected_asset,
        period=period,
        key_suffix="opportunity_tab",
    )

with tab_executive:
    render_research_packet_exporter(
        selected_asset,
        snapshot,
        risk,
        news_context,
        signal_data,
        backtest_results,
        benchmark_results,
    )
    render_quant_decision_intelligence(
        decision_ranked_assets,
        conviction_inputs,
        screened_assets,
        benchmark_truth_exec,
        optimizer_v1_exec,
        governance_review_exec,
        walk_forward_validation_exec,
        research_mode=research_mode,
    )
    render_executive_dashboard(
        selected_asset,
        meta_decision_exec,
        conviction_exec,
        allocation_timing_exec,
        position_size_exec,
        entry_exit_exec,
        exposure_limits_exec,
        correlation_exec,
        subagent_reviews_exec,
        research_mode,
    )
    render_ranked_quant_decision_table(
        screened_assets,
        opportunity_data,
        selected_asset,
        conviction_exec,
        thesis_health_exec,
    )
    render_data_source_status(selected_asset, snapshot, price_data, screened_assets)
    render_market_snapshot(snapshot, shares)
    render_price_chart(price_data)

with tab_decision:
    render_explainability_panel(
        signal_data,
        conviction_exec,
        regime_data,
        news_context,
        opportunity_data,
        risk,
        exposure_limits_exec,
        thesis_health_exec,
        confidence_exec,
    )
    render_meta_decision_engine(
        selected_asset,
        signal_data,
        conviction_exec,
        opportunity_data,
        alpha_exec,
        execution_exec,
        position_size_exec,
        entry_exit_exec,
        regime_data,
        news_context,
        catalyst_exec,
        scenario_results,
        stress_test_results,
        exposure_limits_exec,
        correlation_exec,
        {},
        strategy_comparison_exec,
        research_mode,
    )
    render_cross_asset_screener_from_rows(screened_assets)
    render_opportunistic_stock_screener(screened_assets, research_mode)
    render_opportunity_engine(
        screened_assets,
        research_mode,
        sector_context=sector_context,
        asset_class=asset_class_context,
    )
    render_watchlist_drift_engine(screened_assets, research_mode)
    render_thesis_tracker(selected_asset, snapshot, signal_data, regime_data, news_context)
    render_catalyst_tracker(selected_asset, news_context, thesis_health_exec, conviction_exec)
    render_alternative_data_context(selected_asset)
    render_fundamental_catalyst_quality(selected_asset, catalyst_exec)
    render_conviction_engine(
        signal_data,
        opportunity_data,
        thesis_health_exec,
        regime_data,
        news_context,
        factor_attribution_exec,
        confidence_exec,
        research_mode,
    )
    render_scenario_engine(
        selected_asset,
        risk,
        signal_data,
        news_context,
        regime_data,
        exposure_data=exposure_data,
        asset_class=asset_class_context,
    )
    render_factor_attribution(screened_assets, recommended_allocations, research_mode)

with tab_timing:
    render_timing_explanation(regime_data, risk, catalyst_exec, thesis_health_exec, signal_data)
    decision = render_trade_decision_assistant(
        selected_asset,
        snapshot,
        risk,
        news_context,
        backtest_results,
        paper_positions,
    )
    render_allocation_timing_recommendation(
        selected_asset,
        conviction_exec,
        signal_data,
        opportunity_data,
        regime_data,
        news_context,
        catalyst_exec,
        backtest_results,
        strategy_lab_results,
        benchmark_results,
        risk,
        research_mode,
    )
    alpha_data = render_alpha_engine(
        selected_asset,
        price_data,
        paper_trade_results=paper_positions,
        period=period,
        key_suffix="timing",
    )
    execution_data = render_execution_readiness(
        signal_data,
        conviction_exec,
        opportunity_data,
        alpha_data,
        regime_data,
        news_context,
        catalyst_exec,
        risk,
        research_mode,
        confidence_data=confidence_exec,
    )
    position_size_data = render_position_sizing_engine(
        execution_data,
        conviction_exec,
        risk,
        research_mode,
        portfolio_value=portfolio_value,
    )
    render_position_sizing_modes(position_size_data, risk)
    entry_exit_data = render_entry_exit_framework(
        execution_data,
        conviction_exec,
        signal_data,
        alpha_data,
        risk,
        research_mode,
    )

with tab_portfolio:
    # V1 requested order:
    # 1) Decision intelligence 2) Ranked opportunities 3) Portfolio optimizer
    # 4) Benchmark truth 5) Strategy lab context
    financial_profile = render_financial_profile_form()
    real_holdings = render_real_portfolio_editor()
    opportunity_terminal_context = render_opportunity_terminal(
        period,
        default_rows=screened_assets,
        financial_profile=financial_profile,
        sector_context=sector_context,
        macro_context=macro_context,
        key_suffix="portfolio",
    )
    opportunity_scan_rows = opportunity_terminal_context.get("rows", screened_assets)
    market_timing_context = opportunity_terminal_context.get("market_timing", market_timing_exec)
    buy_finder_context = render_buy_finder_terminal(
        opportunity_scan_rows,
        market_timing_context,
        financial_profile,
        real_holdings,
        accuracy_context=learning_accuracy if "learning_accuracy" in locals() else prediction_summary_exec,
        key_suffix="portfolio",
    )
    selected_opportunity_row = next(
        (row for row in opportunity_scan_rows if row.get("symbol") == selected_asset),
        selected_screen_row,
    )
    selected_growth_discovery = score_growth_discovery(
        selected_asset,
        selected_opportunity_row or selected_screen_row,
        fundamentals={},
        catalysts=catalyst_exec,
        alt_data=alternative_data_context,
        source_quality=selected_data_quality_exec,
    )
    render_data_source_quality_dashboard(selected_asset, snapshot, price_data, screened_assets)
    learning_accuracy = render_recommendation_learning_dashboard(current_prices_by_symbol)
    advisor_strategy = render_portfolio_strategy_advisor(
        financial_profile,
        real_holdings,
        opportunity_scan_rows,
        benchmark_truth=benchmark_truth_exec,
        decision_intelligence={},
        accuracy_context=learning_accuracy,
    )
    ipo_research_context = render_ipo_research(selected_asset)
    selected_existing_real_holding = next(
        (row for row in real_holdings if row.get("symbol") == selected_asset),
        {},
    )
    final_recommendation = render_final_recommendation_panel(
        selected_asset,
        signal_data,
        quant_decision_exec,
        advisor_strategy,
        selected_data_quality_exec,
        advisor_strategy.get("suitability", {}),
        learning_accuracy,
        risk,
        current_holding=selected_existing_real_holding,
        ipo_context=ipo_research_context.get("selected_ipo", {}),
        growth_discovery_context=selected_growth_discovery,
        market_timing_context=market_timing_context,
    )
    render_broker_alert_tickets(final_recommendation)
    render_recommendation_logger(advisor_strategy, current_prices_by_symbol)
    render_quant_decision_intelligence(
        decision_ranked_assets,
        conviction_inputs,
        screened_assets,
        benchmark_truth_exec,
        optimizer_v1_exec,
        governance_review_exec,
        walk_forward_validation_exec,
        research_mode=research_mode,
    )
    ranked_for_portfolio = render_ranked_quant_decision_table(
        screened_assets,
        opportunity_data,
        selected_asset,
        conviction_exec,
        thesis_health_exec,
    )
    optimizer_v1 = render_portfolio_optimizer_v1(
        ranked_for_portfolio,
        research_mode=research_mode,
    )
    benchmark_view = render_etf_benchmark_dashboard(period, paper_scorecard=paper_scorecard)
    render_benchmark_truth(
        paper_performance,
        benchmark_view,
    )
    render_strategy_comparison_engine(
        price_data,
        risk,
        regime_data,
        signal_data,
        research_mode,
    )

    current_allocations = render_portfolio_simulator(watchlist)
    render_risk_engine(
        selected_asset,
        snapshot,
        risk,
        confidence=mode_adjusted_confidence,
        total_portfolio_value=mode_adjusted_portfolio_value,
        current_symbol_exposure=current_symbol_exposure,
        asset_class=asset_class_context,
    )
    render_exposure_engine(exposure_data)
    render_portfolio_optimizer(
        screened_assets,
        research_mode,
        sector_context=sector_context,
        optimizer_result=optimizer_result,
    )
    render_rebalance_advisor(
        current_allocations,
        recommended_allocations,
        research_mode,
        sector_context,
    )
    exposure_limits_data = render_exposure_limits_engine(
        recommended_allocations,
        screened_assets,
        conviction_exec,
        research_mode,
    )
    correlation_data = render_correlation_engine(
        screened_assets,
        recommended_allocations,
        research_mode,
    )
    capital_hierarchy_data = render_capital_hierarchy_engine(
        screened_assets,
        recommended_allocations,
        conviction_exec,
        execution_exec,
        alpha_exec,
        correlation_data,
        research_mode,
    )
    selected_existing_position = paper_positions.get("positions", {}).get(selected_asset, {})
    render_auto_paper_trading_control_panel(
        selected_asset,
        snapshot,
        meta_decision_exec,
        execution_exec,
        position_size_exec,
        entry_exit_exec,
        exposure_limits_data,
        correlation_data,
        benchmark_basket_data,
        selected_data_confidence,
        selected_existing_position,
        research_mode,
        final_recommendation=final_recommendation if "final_recommendation" in locals() else None,
    )
    render_stress_test_engine(paper_positions)
    render_paper_trading_simulator(watchlist)

with tab_etf:
    render_etf_benchmark_dashboard(period, paper_scorecard=paper_scorecard)
    render_best_etf_benchmark(period)
    render_alpha_engine(
        selected_asset,
        price_data,
        paper_trade_results=paper_positions,
        period=period,
        key_suffix="etf",
    )
    render_strategy_scorecard(paper_performance, benchmark_basket_data, paper_positions)

with tab_accuracy:
    render_prediction_accuracy_dashboard(
        load_predictions(),
        benchmark_returns=benchmark_basket_data,
    )
    render_prediction_evaluation(selected_asset, snapshot.get("price"))

with tab_strategy:
    render_backtest_section(price_data)
    render_strategy_lab(price_data)
    render_walk_forward_section(price_data)
    walk_forward_validation = render_walk_forward_validation(
        watchlist,
        research_mode,
    )
    prediction_eval_summary = evaluate_all_predictions(selected_asset, snapshot.get("price"))
    research_run_eval_summary = evaluate_research_runs(selected_asset, snapshot.get("price"))
    render_strategy_leaderboard(
        walk_forward_validation,
        prediction_evaluations=prediction_eval_summary,
        research_run_evaluations=research_run_eval_summary,
    )
    strategy_comparison_data = render_strategy_comparison_engine(
        price_data,
        risk,
        regime_data,
        signal_data,
        research_mode,
    )

with tab_journal:
    notes = st.text_area(f"Notes for {selected_asset}", height=180)
    research_memo = generate_research_summary(selected_asset, snapshot, risk, notes=notes)
    render_research_notes(selected_asset, notes)
    render_research_brief(
        selected_asset,
        snapshot,
        risk,
        macro_context,
        sector_context,
        news_context,
        regime_data,
        signal_data,
        opportunity_data,
        exposure_data,
        decision,
        research_memo,
        scenario_results,
        stress_test_results,
        factor_attribution_exec,
    )
    render_daily_research_report(watchlist, research_mode, period)
    render_prediction_log(selected_asset, snapshot.get("price"))
    render_prediction_evaluation(selected_asset, snapshot.get("price"))
    render_decision_journal(selected_asset, decision, snapshot)
    render_save_research_run(
        selected_asset,
        snapshot,
        risk,
        price_data,
        news_context,
        notes,
        current_symbol_exposure,
        portfolio_value,
        decision,
    )
    render_research_run_evaluation(selected_asset, snapshot.get("price"))
    render_adaptive_learning()
    render_learning_engine(selected_asset, snapshot.get("price"))
    render_research_journal(watchlist, selected_asset)

with tab_agents:
    render_agent_research_desk(
        selected_asset,
        screened_assets,
        financial_profile=stored_financial_profile_exec,
        current_prices=current_prices_by_symbol,
        key_suffix="agents_tab",
    )
    render_research_agent(selected_asset, snapshot, risk, notes)
    orchestrator_report = render_workflow_orchestrator(
        selected_asset,
        price_data,
        snapshot,
        research_mode,
    )
    render_subagent_reviews(orchestrator_report.get("outputs", {}), research_mode)
    render_agent_task_runner(
        selected_asset,
        snapshot,
        price_data,
        risk,
        news_context,
        signal_data,
        regime_data,
        exposure_data,
        backtest_results,
        strategy_lab_results,
        decision,
        research_memo,
        research_mode=research_mode,
        analysis_depth=analysis_depth,
    )

with tab_health:
    health_prediction_summary = evaluate_prediction_accuracy(
        load_predictions(),
        benchmark_returns=benchmark_basket_data,
    )
    stress_research = render_market_stress_research(period=period)
    render_research_quality_audit(
        selected_asset,
        snapshot,
        price_data,
        prediction_summary=health_prediction_summary,
        stress_context=stress_research,
    )
    render_macro_dashboard(research_mode)
    render_asset_class_context(selected_asset, asset_class_context)
    render_sector_rotation(research_mode, period, sector_context=sector_context)
    render_market_regime(price_data, risk)
    render_news_intelligence(selected_asset)
    render_alternative_data_context(selected_asset)
    compare_assets = st.multiselect(
        "Compare with assets",
        [asset for asset in watchlist if asset != selected_asset],
        default=[asset for asset in watchlist if asset != selected_asset][:2],
    )
    normalize = st.checkbox("Normalize performance (start all at 100)", value=True)
    render_asset_comparison(selected_asset, watchlist, compare_assets, period, normalize)
    render_confidence_engine(
        signal_data,
        evaluation_summary,
        regime_data,
        adaptive_learning,
        research_mode=research_mode,
        analysis_depth=analysis_depth,
    )
    render_signal_engine(selected_asset, snapshot, risk, price_data)
    render_experiment_tracker()
    experiment_rows = load_experiments()
    status_counts = {}
    for row in experiment_rows:
        status = row.get("status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    experiment_summary = {
        "total_experiments": len(experiment_rows),
        "status_counts": status_counts,
    }
    prediction_summary = health_prediction_summary
    research_run_summary = evaluate_research_runs(selected_asset, snapshot.get("price"))
    render_research_review_agent(
        prediction_summary=prediction_summary,
        research_run_summary=research_run_summary,
        experiment_summary=experiment_summary,
        leaderboard_summary={},
        portfolio_performance=paper_performance,
    )
    prediction_summary["total_predictions"] = len(load_predictions())
    prediction_summary["total_runs"] = research_run_summary.get("total_runs", 0)
    render_governance_review(
        meta_decision=meta_decision_exec,
        conviction_data=conviction_exec,
        execution_data=execution_exec,
        position_size_data=position_size_exec,
        prediction_accuracy=prediction_summary,
        benchmark_data=benchmark_basket_data,
        research_mode=research_mode,
    )
    render_health_check()
    render_database_status()
    render_roadmap()
