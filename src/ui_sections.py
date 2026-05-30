import json

import streamlit as st

from market_data import get_asset_comparison, get_market_snapshot, get_risk_metrics
from journal import add_journal_entry, load_journal
from prediction_log import add_prediction, evaluate_all_predictions, load_predictions
from research_agent import generate_research_summary
from signal_engine import generate_signal
from backtester import run_simple_backtest, run_strategy_lab, run_walk_forward_test
from news_engine import generate_news_context, get_recent_news
from portfolio_simulator import simulate_portfolio
from paper_trader import (
    add_paper_trade,
    calculate_paper_performance,
    calculate_paper_positions,
    load_paper_trades,
)
from trade_decision_assistant import generate_trade_decision
from evaluation_engine import evaluate_prediction
from learning_engine import analyze_signal_effectiveness
from regime_engine import detect_market_regime
from risk_engine import calculate_position_size
from adaptive_learning_engine import calculate_factor_insights
from research_run_log import evaluate_research_runs, load_research_runs, save_research_run
from agent_task_runner import run_research_workflow
from confidence_engine import calculate_confidence_adjustment
from screener_engine import run_cross_asset_screen
from portfolio_optimizer import generate_portfolio_allocation
from opportunity_engine import rank_opportunities
from scenario_engine import run_scenarios
from stress_test_engine import run_stress_tests
from macro_engine import generate_macro_context
from sector_rotation_engine import analyze_sector_rotation
from rebalance_engine import generate_rebalance_plan
from factor_engine import analyze_factor_attribution
from drift_engine import (
    detect_watchlist_drift,
    load_previous_watchlist_snapshot,
    save_watchlist_snapshot,
)
from decision_journal import (
    evaluate_decisions_for_symbol,
    load_decisions,
    save_decision,
)
from research_brief_generator import generate_research_brief
from daily_report_generator import generate_daily_report
from catalyst_engine import generate_catalyst_tracker
from thesis_engine import (
    evaluate_thesis_health,
    load_theses,
    save_or_update_thesis,
)
from conviction_engine import calculate_conviction_score
from allocation_timing_engine import generate_allocation_timing_recommendation
from alpha_engine import analyze_alpha_vs_benchmark
from execution_engine import evaluate_execution_readiness
from position_sizing_engine import calculate_position_size as calculate_position_size_v1
from entry_exit_engine import generate_entry_exit_plan
from asset_class_engine import classify_asset
from asset_sector_map import map_asset_to_sector
from exposure_limits_engine import evaluate_portfolio_exposure_limits
from correlation_engine import analyze_cross_asset_correlation
from capital_hierarchy_engine import build_capital_allocation_hierarchy
from strategy_comparison_engine import compare_strategies
from meta_decision_engine import generate_meta_decision
from health_check import run_health_check
from database import get_database_status
from workflow_orchestrator import run_research_workflow as run_orchestrated_workflow
from subagent_engine import run_subagent_reviews
from executive_dashboard_engine import generate_executive_summary
from data_quality_engine import evaluate_data_quality, summarize_data_sources
from data_source_registry import list_data_sources
from opportunistic_screener_engine import rank_opportunistic_stocks
from benchmark_basket_engine import find_best_etf_benchmark
from strategy_scorecard_engine import generate_strategy_scorecard
from auto_paper_trader import build_auto_paper_trade_ticket, save_auto_paper_trade
from prediction_accuracy_engine import evaluate_prediction_accuracy
from benchmark_engine import compare_to_benchmarks
from walk_forward_engine import run_walk_forward_validation
from leaderboard_engine import build_strategy_leaderboard
from experiment_tracker import (
    compare_experiment_results,
    load_experiments,
    save_experiment,
    update_experiment_result,
)
from research_review_agent import generate_research_review
from governance_engine import run_governance_review
from explainable_quant_engine import (
    build_ranked_decision_table,
    calculate_explainability_panel,
    compare_etf_benchmarks,
    generate_position_sizing_modes,
    generate_timing_explanation,
)
from decision_intelligence import build_quant_decision_intelligence
from alternative_data_engine import generate_alternative_data_context
from db_service import (
    delete_real_holding,
    load_agent_evidence,
    load_agent_runs,
    load_agent_research_tasks,
    load_broker_alerts,
    load_financial_profile,
    load_recommendation_log,
    load_real_holdings,
    load_ticker_memory,
    save_agent_run,
    save_agent_evidence,
    save_agent_research_task,
    save_broker_alert,
    save_financial_profile,
    save_real_holding,
    save_recommendation_log,
    save_ticker_memory,
    update_agent_research_task,
    update_broker_alert_status,
    update_recommendation_outcome,
)
from final_recommendation_engine import build_final_recommendation
from ipo_research_engine import generate_ipo_research_context
from portfolio_strategy_engine import build_portfolio_strategy
from fundamental_catalyst_engine import generate_fundamental_catalyst_context
from recommendation_accuracy_engine import (
    build_learning_dashboard_context,
    build_research_process_audit,
    evaluate_recommendation_accuracy,
)
from sp500_universe import get_sp500_style_symbols, get_sp500_style_universe
from opportunity_universe import build_opportunity_universe, get_opportunity_symbols
from growth_discovery_engine import score_growth_discovery
from market_timing_engine import build_market_timing_context
from buy_finder_engine import build_buy_finder, build_portfolio_action_plan
from agent_research_engine import generate_agent_research_tasks
from agent_research_desk import (
    evaluate_agent_research_memory,
    generate_daily_agent_queue,
    run_agent_research_desk,
)
from best_opportunities_engine import rank_best_opportunities, run_any_ticker_research
from research_packet_exporter import build_research_packet_markdown
from market_stress_engine import analyze_market_stress


def render_market_snapshot(snapshot, shares):
    """Render the market snapshot section."""
    st.header("Market Snapshot")
    col1, col2, col3 = st.columns(3)

    price_display = (
        f"${snapshot['price']:.2f}"
        if isinstance(snapshot.get("price"), (int, float))
        else snapshot.get("price")
    )
    col1.metric("Price", price_display, delta=f"{snapshot.get('change_pct', 0):+.2f}%")
    col2.metric("Daily change", f"{snapshot.get('change_pct', 0):+.2f}%")
    col3.metric("Volume", f"{snapshot.get('volume', 0):,}")

    if snapshot.get("source") == "mock":
        st.warning(
            f"Using fallback market snapshot data. Reason: {snapshot.get('error', 'unknown')}"
        )

    position_value = (
        shares * snapshot.get("price", 0)
        if isinstance(snapshot.get("price"), (int, float))
        else 0
    )
    st.metric("Position value", f"${position_value:,.2f}")
    return position_value


def render_research_packet_exporter(
    symbol,
    snapshot,
    risk,
    news_context,
    signal_data,
    backtest_results,
    portfolio_comparison,
):
    """Render a Markdown research-packet download button."""
    st.header("Research Packet Exporter")
    packet = build_research_packet_markdown(
        symbol,
        snapshot,
        risk,
        news_context,
        signal_data,
        backtest_results,
        portfolio_comparison,
    )
    st.download_button(
        "Download Markdown Research Packet",
        data=packet,
        file_name=f"{str(symbol or 'asset').upper()}_research_packet.md",
        mime="text/markdown",
    )
    st.caption(
        "Research-only export. No financial advice, no broker APIs, no live trading, and no guaranteed returns."
    )
    return packet


def render_macro_dashboard(research_mode):
    """Render simple research-only macro context."""
    macro = generate_macro_context(research_mode=research_mode)

    st.header("Macro Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Macro state", macro.get("macro_state", "Neutral"))
    col2.metric("Inflation risk", macro.get("inflation_risk", "Moderate"))
    col3.metric("Rate environment", macro.get("rate_environment", "Stable"))

    col4, col5 = st.columns(2)
    col4.metric("Growth outlook", macro.get("growth_outlook", "Mixed"))
    col5.metric("Market risk bias", macro.get("market_risk_bias", "Balanced"))

    st.markdown("**Macro notes**")
    for note in macro.get("macro_notes", []):
        st.info(f"- {note}")

    st.markdown("**Portfolio implication**")
    st.write(macro.get("portfolio_implication", "No implication available."))
    st.caption(
        "Research-only macro layer. This is not live forecasting and does not execute trades."
    )


def render_research_quality_audit(
    selected_asset,
    snapshot,
    price_data,
    prediction_summary=None,
    stress_context=None,
):
    """Render a plain-English research quality checklist."""
    st.header("Research Quality Audit")
    st.caption(
        "Checks whether the workflow is evidence-aware, research-only, and honest about data quality."
    )

    prediction_summary = prediction_summary or {}
    stress_context = stress_context or {}
    snapshot_source = snapshot.get("source", "unknown") if isinstance(snapshot, dict) else "unknown"
    price_source = price_data.get("source", "unknown") if isinstance(price_data, dict) else "unknown"
    fallback_used = bool(
        (isinstance(snapshot, dict) and (snapshot.get("is_fallback") or snapshot_source == "mock"))
        or (isinstance(price_data, dict) and (price_data.get("is_fallback") or price_source == "mock"))
    )
    sample_confidence = prediction_summary.get("sample_confidence", "No evidence yet")
    stress_posture = stress_context.get("risk_posture", "Needs More Data")

    checklist = [
        {
            "check": "Research-only guardrails",
            "status": "Pass",
            "detail": "No broker APIs, live trading, order placement, or guaranteed-return claims are needed for this workflow.",
        },
        {
            "check": "Data source visibility",
            "status": "Review" if fallback_used else "Pass",
            "detail": (
                f"{selected_asset} snapshot source: {snapshot_source}; price source: {price_source}. "
                "Fallback/mock data is being used."
                if fallback_used
                else f"{selected_asset} snapshot source: {snapshot_source}; price source: {price_source}."
            ),
        },
        {
            "check": "Prediction evidence",
            "status": "Review" if sample_confidence in {"No evidence yet", "Not enough evidence"} else "Pass",
            "detail": f"Prediction sample confidence: {sample_confidence}.",
        },
        {
            "check": "Crash hypothesis discipline",
            "status": "Review" if stress_posture in {"Stress", "Needs More Data"} else "Pass",
            "detail": f"Crash Watch posture: {stress_posture}. Treat crash calls as hypotheses, not certainty.",
        },
        {
            "check": "Futures scope",
            "status": "Pass",
            "detail": "Futures stay proxy-only in this version; no futures contracts, margin, leverage, or execution logic.",
        },
    ]

    st.dataframe(checklist, width="stretch")
    if fallback_used:
        st.warning("Fallback/mock data is present. Use this output for learning only until data quality improves.")
    st.info(
        "Best practice: compare every thesis to ETF baselines, test out-of-sample when possible, save predictions, then review what actually happened."
    )
    return {"checks": checklist, "fallback_used": fallback_used, "sample_confidence": sample_confidence}


def render_market_stress_research(period="3mo"):
    """Render broad-market crash-risk hypothesis testing with proxies only."""
    st.header("Crash Watch Research Panel")
    st.caption(
        "Proxy-only market stress research. This is not a crash prediction, financial advice, or trade instruction."
    )

    stress = analyze_market_stress(period=period)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Risk posture", stress.get("risk_posture", "Needs More Data"))
    col2.metric("Stress score", f"{stress.get('stress_score', 0.0):.1f}/100")
    col3.metric("Risk-on breadth", f"{stress.get('breadth_pct', 0.0):.1f}%")
    col4.metric("Fallback rows", stress.get("fallback_count", 0))

    col5, col6, col7 = st.columns(3)
    col5.metric("Deteriorating proxies", stress.get("deteriorating_count", 0))
    col6.metric("Credit proxy", stress.get("credit_risk_proxy", "Unknown"))
    col7.metric("Volatility proxy", stress.get("volatility_proxy", "Unknown"))

    if stress.get("fallback_count", 0):
        st.warning("Some Crash Watch inputs use fallback/mock/error data. Treat the posture as low-confidence.")
    if stress.get("defensive_rotation"):
        st.info("Defensive proxies are outperforming SPY in this sample, which can indicate caution.")

    rows = stress.get("rows", [])
    if rows:
        st.dataframe(rows, width="stretch")
    else:
        st.write("No market stress proxy rows available.")

    st.write(stress.get("interpretation", "No stress interpretation available."))
    st.caption(stress.get("disclaimer", "Research-only market stress context."))
    return stress


def render_asset_class_context(symbol, asset_class_context=None):
    """Render asset-class metadata context for the selected symbol."""
    context = asset_class_context or classify_asset(symbol)
    st.header("Asset Class Context")
    col1, col2, col3 = st.columns(3)
    col1.metric("Asset class", context.get("asset_class", "Unknown"))
    col2.metric("Market type", context.get("market_type", "Unknown"))
    col3.metric("Risk profile", context.get("risk_level", "Unknown"))

    st.write(f"Trading profile: {context.get('trading_profile', 'Unknown')}")
    for note in context.get("notes", []):
        st.info(f"- {note}")
    st.caption("Research-only context label. No execution behavior is attached.")


def render_sector_rotation(research_mode, period, sector_context=None):
    """Render sector rotation analysis from sector ETF proxies."""
    st.header("Sector Rotation Engine")
    rotation = (
        sector_context
        if isinstance(sector_context, dict) and sector_context.get("ranked_sectors")
        else analyze_sector_rotation(period=period, research_mode=research_mode)
    )
    sectors = rotation.get("ranked_sectors", [])

    if not sectors:
        st.write("No sector results available right now.")
        st.caption("Research-only sector analysis. No live trading, no broker APIs.")
        return

    strongest = rotation.get("strongest_sector", {})
    weakest = rotation.get("weakest_sector", {})

    col1, col2 = st.columns(2)
    col1.metric(
        "Strongest sector",
        f"{strongest.get('sector', 'N/A')} ({strongest.get('ticker', 'N/A')})",
    )
    col2.metric(
        "Weakest sector",
        f"{weakest.get('sector', 'N/A')} ({weakest.get('ticker', 'N/A')})",
    )

    st.dataframe(sectors, width="stretch")
    st.write(rotation.get("rotation_summary", "No summary available."))
    st.caption(
        "Research-only sector rotation context. No auto execution, no guaranteed performance."
    )


def render_price_chart(price_data):
    """Render the price chart and risk metrics section."""
    st.header("Price Chart")

    price_source = None
    chart_data = price_data
    if isinstance(price_data, dict) and "source" in price_data:
        price_source = price_data.get("source")
        chart_data = price_data.get("data")
        if price_source == "mock":
            st.warning(
                f"Using fallback price history data. Reason: {price_data.get('error', 'unknown')}"
            )
        elif price_source == "yfinance":
            st.caption("Real yfinance market data in use.")

    if hasattr(chart_data, "set_index"):
        chart_df = chart_data.set_index("Date")["Close"]
        st.line_chart(chart_df)
    elif isinstance(chart_data, dict) and "Close" in chart_data:
        st.line_chart(chart_data["Close"])
    else:
        st.line_chart(chart_data)

    risk = get_risk_metrics(chart_data)
    col1, col2, col3 = st.columns(3)
    col1.metric("Return", f"{risk['return_pct']:+.2f}%")
    col2.metric("Volatility (ann.)", f"{risk['volatility_pct']:.2f}%")
    col3.metric("Max drawdown", f"{risk['max_drawdown_pct']:.2f}%")
    return risk


def render_market_regime(price_data, risk):
    """Render a simple research-only market regime summary."""
    regime = detect_market_regime(price_data, risk)

    st.header("Market Regime")
    st.caption("Research-only environment summary. This does not execute or recommend trades.")

    col1, col2 = st.columns(2)
    col1.metric("Regime", regime["regime"])
    col2.metric("Confidence", f"{regime['confidence']}/10")

    st.markdown("**Reasoning**")
    for point in regime["reasoning"]:
        st.info(f"- {point}")

    st.markdown("**Suggested strategy bias**")
    st.write(regime["strategy_bias"])

    st.markdown("**Risk note**")
    st.warning(regime["risk_note"])


def render_backtest_section(price_data):
    """Run a simple backtest and display results."""
    results = run_simple_backtest(price_data)
    st.header("Backtesting")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Buy & Hold", f"{results.get('buy_and_hold_return_pct', 0.0):+.2f}%")
    col2.metric("Strategy", f"{results.get('strategy_return_pct', 0.0):+.2f}%")
    col3.metric("Max drawdown", f"{results.get('max_drawdown_pct', 0.0):.2f}%")
    col4.metric("Signal changes", f"{results.get('number_of_signal_changes', 0)}")

    # Plot equity curves if available
    equity = results.get("equity_curve")
    if equity is not None:
        try:
            eq_df = equity.copy()
            if "Date" in eq_df.columns:
                eq_df = eq_df.set_index("Date")
            st.markdown("**Equity curve (base 100)**")
            st.line_chart(eq_df)
        except Exception:
            st.write("Unable to render equity curve.")

    # Simple verdict comparing strategy vs buy-and-hold
    buy_ret = results.get("buy_and_hold_return_pct", 0.0)
    strat_ret = results.get("strategy_return_pct", 0.0)
    if strat_ret > buy_ret:
        st.success("Strategy outperformed buy and hold")
    else:
        st.info("Strategy underperformed buy and hold")


def render_strategy_lab(price_data):
    """Render a simple comparison of multiple research strategies."""
    results = run_strategy_lab(price_data)
    strategy_results = results.get("strategy_results", [])
    backtest = run_simple_backtest(price_data)
    buy_and_hold_return = backtest.get("buy_and_hold_return_pct", 0.0)

    st.header("Strategy Lab")
    if not strategy_results:
        st.write("Not enough data to compare strategies.")
        return

    ranked_results = sorted(
        strategy_results,
        key=lambda entry: entry.get("return_pct", 0.0),
        reverse=True,
    )
    best = ranked_results[0].get("strategy_name", "Unknown")
    worst = ranked_results[-1].get("strategy_name", "Unknown")
    any_beats_buy_hold = any(
        entry.get("return_pct", 0.0) > buy_and_hold_return
        for entry in ranked_results
    )

    st.subheader("Strategy Lab Summary")
    summary_cols = st.columns(2)
    summary_cols[0].metric("Best performer", best)
    summary_cols[1].metric("Worst performer", worst)

    if any_beats_buy_hold:
        st.success("At least one strategy beat buy-and-hold on this sample.")
    else:
        st.info("No strategy beat buy-and-hold on this sample.")

    st.caption("Research-only reminder: past performance does not guarantee future results.")

    table_rows = []
    for rank, entry in enumerate(ranked_results, start=1):
        table_rows.append(
            {
                "Rank": rank,
                "Strategy": entry.get("strategy_name", "Unknown"),
                "Return %": f"{entry.get('return_pct', 0.0):+.2f}%",
                "Max Drawdown %": f"{entry.get('max_drawdown_pct', 0.0):.2f}%",
                "Signal Changes": entry.get("signal_changes", 0),
            }
        )

    st.dataframe(table_rows, width="stretch")

    st.markdown("**How to read this:**")
    st.write(
        "- High return + low drawdown = stronger historical candidate."
    )
    st.write(
        "- High signal changes = more active behavior and possibly more transaction costs."
    )
    st.write(
        "- Underperforming buy-and-hold means the strategy needs improvement."
    )


def render_walk_forward_section(price_data):
    """Render a simple walk-forward testing summary."""
    walk_forward = run_walk_forward_test(price_data)

    st.header("Walk-Forward Testing")
    if walk_forward.get("total_windows", 0) == 0:
        st.write("Not enough data for walk-forward testing.")
        return

    col1, col2 = st.columns(2)
    col1.metric("Total windows", walk_forward.get("total_windows", 0))
    col2.metric("Most consistent strategy", walk_forward.get("most_consistent_strategy", "N/A"))

    st.caption(
        "Walk-forward testing helps reduce overfitting, but it still does not guarantee future performance."
    )

    win_counts = walk_forward.get("strategy_win_counts", {})
    avg_returns = walk_forward.get("average_return_by_strategy", {})

    table_rows = []
    for strategy_name in sorted(win_counts.keys() | avg_returns.keys()):
        table_rows.append(
            {
                "Strategy": strategy_name,
                "Win Count": win_counts.get(strategy_name, 0),
                "Average Return %": f"{avg_returns.get(strategy_name, 0.0):+.2f}%",
            }
        )

    st.dataframe(table_rows, width="stretch")


def render_walk_forward_validation(
    watchlist,
    research_mode,
    train_window_days=60,
    test_window_days=20,
    period="1y",
):
    """Render rolling walk-forward validation versus SPY benchmark."""
    validation = run_walk_forward_validation(
        watchlist,
        research_mode=research_mode,
        train_window_days=train_window_days,
        test_window_days=test_window_days,
        period=period,
    )

    st.header("Walk-Forward Validation")
    total_windows = validation.get("total_windows", 0)
    if total_windows == 0:
        st.write("Not enough data to run walk-forward validation.")
        st.write(validation.get("summary", "No validation summary available."))
        st.caption(
            "Research-only validation. Historical rolling results do not guarantee future performance."
        )
        return validation

    col1, col2, col3 = st.columns(3)
    col1.metric("Total windows", total_windows)
    col2.metric("Win rate vs SPY", f"{validation.get('win_rate_vs_spy', 0.0):.2f}%")
    col3.metric("Average alpha vs SPY", f"{validation.get('average_alpha_vs_spy', 0.0):+.2f}%")

    best = validation.get("best_window", {})
    worst = validation.get("worst_window", {})
    col4, col5 = st.columns(2)
    col4.metric(
        "Best window alpha",
        f"{best.get('alpha_vs_spy_pct', 0.0):+.2f}%",
    )
    col5.metric(
        "Worst window alpha",
        f"{worst.get('alpha_vs_spy_pct', 0.0):+.2f}%",
    )

    window_rows = validation.get("window_results", [])
    if window_rows:
        st.dataframe(window_rows[-10:], width="stretch")
    else:
        st.write("No window-level results were produced.")

    st.write(validation.get("summary", "No validation summary available."))
    st.caption(
        "Research-only validation and not guaranteed future performance. No broker APIs, no live trading, and no auto execution."
    )
    return validation


def render_strategy_leaderboard(
    walk_forward_results,
    prediction_evaluations=None,
    research_run_evaluations=None,
):
    """Render a cross-layer leaderboard for strategy/signal/research-mode performance."""
    board = build_strategy_leaderboard(
        walk_forward_results,
        prediction_evaluations=prediction_evaluations,
        research_run_evaluations=research_run_evaluations,
    )

    st.header("Model / Strategy Leaderboard")
    rows = board.get("leaderboard", [])
    if rows:
        st.dataframe(rows, width="stretch")
    else:
        st.write("No leaderboard rows are available yet.")
        st.write(board.get("learning_summary", "No learning summary available."))
        st.caption(
            "Historical research-only results; not a guarantee of future performance."
        )
        return board

    top = board.get("top_performer", {})
    worst = board.get("worst_performer", {})
    col1, col2 = st.columns(2)
    col1.metric(
        "Top performer",
        f"{top.get('name', 'N/A')} ({top.get('consistency_score', 0):.1f})",
    )
    col2.metric(
        "Worst performer",
        f"{worst.get('name', 'N/A')} ({worst.get('consistency_score', 0):.1f})",
    )

    st.write(board.get("learning_summary", "No learning summary available."))
    st.caption(
        "Historical research-only leaderboard. No broker APIs, no live trading, no auto execution, and no guaranteed alpha."
    )
    return board


def render_strategy_comparison_engine(
    price_data,
    risk,
    regime_data,
    signal_data,
    research_mode,
):
    """Render comparison across simple strategy styles."""
    comparison = compare_strategies(
        price_data,
        risk,
        regime_data,
        signal_data,
        research_mode=research_mode,
    )

    st.header("Multi-Strategy Comparison Engine")
    strategies = comparison.get("strategies", [])
    if strategies:
        st.dataframe(strategies, width="stretch")
    else:
        st.write("No strategy comparison results available.")

    best = comparison.get("best_strategy", {})
    worst = comparison.get("worst_strategy", {})
    col1, col2 = st.columns(2)
    col1.metric(
        "Best strategy",
        f"{best.get('strategy_name', 'N/A')} ({best.get('strategy_score', 0)}/100)",
    )
    col2.metric(
        "Worst strategy",
        f"{worst.get('strategy_name', 'N/A')} ({worst.get('strategy_score', 0)}/100)",
    )

    st.markdown("**Market fit**")
    st.write(comparison.get("market_fit", "No market fit view available."))
    st.write(comparison.get("summary", "No summary available."))
    st.caption(
        "Research-only strategy comparison. Paper-trading context only with no live execution."
    )
    return comparison


def render_asset_comparison(selected_asset, watchlist, compare_assets, period, normalize):
    """Render the comparison chart section."""
    st.header("Asset Comparison")
    compare_options = [asset for asset in watchlist if asset != selected_asset]
    compare_assets = compare_assets or []

    if compare_assets:
        compare_symbols = [selected_asset] + compare_assets
        comparison = get_asset_comparison(compare_symbols, period=period, normalize=normalize)
        comp_source = None
        comp_data = comparison
        if isinstance(comparison, dict) and "source" in comparison:
            comp_source = comparison.get("source")
            comp_data = comparison.get("data")
            if comp_source == "mock":
                st.warning(
                    f"Using fallback comparison data. Reason: {comparison.get('error', 'unknown')}"
                )
            elif comp_source == "yfinance":
                st.caption("Real yfinance data used for comparison.")

        if hasattr(comp_data, "set_index"):
            st.line_chart(comp_data)
        elif isinstance(comp_data, dict):
            st.line_chart(comp_data)
        else:
            st.line_chart(comp_data)
    elif not compare_assets and not compare_options:
        st.write("No other assets available to compare.")
    else:
        st.write("Select one or more assets to compare.")


def render_cross_asset_screener_from_rows(rows):
    """Render precomputed cross-asset screener rows."""
    st.header("Cross-Asset Screener")

    if not rows:
        st.write("No screener results available right now.")
        st.caption("Research-only screener. This does not execute trades.")
        return

    st.dataframe(rows, width="stretch")

    best_candidate = rows[0]
    highest_risk = max(rows, key=lambda item: item.get("volatility_pct", 0.0))

    col1, col2 = st.columns(2)
    col1.metric(
        "Best candidate",
        f"{best_candidate.get('symbol', 'N/A')} ({best_candidate.get('score', 0)}/100)",
    )
    col2.metric(
        "Highest risk asset",
        f"{highest_risk.get('symbol', 'N/A')} ({highest_risk.get('volatility_pct', 0.0):.2f}% vol)",
    )

    st.caption(
        "Research-only screener: rankings are for study and paper-trading workflows only. No broker APIs, no live execution, no guaranteed outcomes."
    )

    if any(row.get("data_confidence") == "Low" for row in rows):
        st.warning("Some screener rows are based on fallback/mock or low-confidence data.")


def render_data_source_status(selected_asset, snapshot, price_data, screened_assets):
    """Render data-source confidence and freshness status."""
    status = summarize_data_sources(
        screened_assets=screened_assets,
        selected_snapshot=snapshot,
        selected_price_data=price_data,
    )

    st.header("Data Source Status")
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall confidence", status.get("overall_confidence", "Unknown"))
    col2.metric("Fallback/mock results", status.get("fallback_count", 0))
    col3.metric("Warnings", status.get("warning_count", 0))

    rows = status.get("rows", [])
    if rows:
        st.dataframe(rows, width="stretch")
    else:
        st.write("No data-source rows available.")

    if status.get("fallback_count", 0) > 0:
        st.warning("Fallback/mock data is present. Treat affected rankings as lower-confidence research.")
    if status.get("blocked_count", 0) > 0:
        st.error("Some rows are blocked from advisor-style buy/sell recommendations.")
    st.write(status.get("summary", "No data-source summary available."))
    return status


def render_data_source_quality_dashboard(selected_asset, snapshot, price_data, screened_assets):
    """Render stronger source registry and recommendation-gate context."""
    st.header("Data Source Quality")
    status = render_data_source_status(selected_asset, snapshot, price_data, screened_assets)

    with st.expander("Source registry", expanded=False):
        st.dataframe(list_data_sources(), width="stretch")

    blocked = [
        row for row in status.get("rows", [])
        if row.get("recommendation_gate") == "Blocked"
    ]
    if blocked:
        st.markdown("**Blocked recommendation rows**")
        st.dataframe(blocked, width="stretch")
    else:
        st.success("No blocked recommendation gates in the current data set.")

    st.caption(
        "Market data uses free sources where available. Mock, stale, or missing-price data can display research but blocks buy/sell recommendations."
    )
    return status


def render_financial_profile_form():
    """Render and persist advisor-style financial profile inputs."""
    profile = load_financial_profile()
    st.header("Financial Profile")
    st.caption("Stored locally in SQLite. Used for suitability checks before advisor-style outputs.")

    with st.form("financial_profile_form"):
        col1, col2, col3 = st.columns(3)
        cash = col1.number_input("Cash available", min_value=0.0, value=float(profile.get("cash", 0.0)), step=100.0)
        monthly_income = col2.number_input("Monthly income", min_value=0.0, value=float(profile.get("monthly_income", 0.0)), step=100.0)
        monthly_expenses = col3.number_input("Monthly expenses", min_value=0.0, value=float(profile.get("monthly_expenses", 0.0)), step=100.0)

        col4, col5, col6 = st.columns(3)
        emergency_fund = col4.number_input("Emergency fund", min_value=0.0, value=float(profile.get("emergency_fund", 0.0)), step=100.0)
        debt = col5.number_input("Total non-mortgage debt", min_value=0.0, value=float(profile.get("debt", 0.0)), step=100.0)
        tax_account_type = col6.selectbox(
            "Primary account type",
            ["Taxable", "Traditional IRA", "Roth IRA", "401(k)", "Other"],
            index=["Taxable", "Traditional IRA", "Roth IRA", "401(k)", "Other"].index(profile.get("tax_account_type", "Taxable"))
            if profile.get("tax_account_type", "Taxable") in ["Taxable", "Traditional IRA", "Roth IRA", "401(k)", "Other"]
            else 0,
        )

        col7, col8, col9 = st.columns(3)
        investment_horizon = col7.selectbox(
            "Investment horizon",
            ["0-1 years", "1-3 years", "3-5 years", "5-10 years", "10+ years"],
            index=["0-1 years", "1-3 years", "3-5 years", "5-10 years", "10+ years"].index(profile.get("investment_horizon", "3-5 years"))
            if profile.get("investment_horizon", "3-5 years") in ["0-1 years", "1-3 years", "3-5 years", "5-10 years", "10+ years"]
            else 2,
        )
        risk_tolerance = col8.selectbox(
            "Risk tolerance",
            ["Low", "Moderate", "High"],
            index=["Low", "Moderate", "High"].index(profile.get("risk_tolerance", "Moderate"))
            if profile.get("risk_tolerance", "Moderate") in ["Low", "Moderate", "High"]
            else 1,
        )
        liquidity_needs = col9.selectbox(
            "Liquidity needs",
            ["Low", "Medium", "High"],
            index=["Low", "Medium", "High"].index(profile.get("liquidity_needs", "Medium"))
            if profile.get("liquidity_needs", "Medium") in ["Low", "Medium", "High"]
            else 1,
        )

        col10, col11 = st.columns(2)
        max_single = col10.number_input(
            "Max single-stock exposure %",
            min_value=1.0,
            max_value=100.0,
            value=float(profile.get("max_single_stock_exposure", 15.0)),
            step=1.0,
        )
        max_sector = col11.number_input(
            "Max sector exposure %",
            min_value=1.0,
            max_value=100.0,
            value=float(profile.get("max_sector_exposure", 35.0)),
            step=1.0,
        )
        goals = st.text_area("Goals", value=profile.get("goals", ""), height=80)
        saved = st.form_submit_button("Save financial profile")

    if saved:
        profile = save_financial_profile(
            cash=cash,
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            emergency_fund=emergency_fund,
            debt=debt,
            investment_horizon=investment_horizon,
            risk_tolerance=risk_tolerance,
            liquidity_needs=liquidity_needs,
            goals=goals,
            tax_account_type=tax_account_type,
            max_single_stock_exposure=max_single,
            max_sector_exposure=max_sector,
        )
        st.success("Financial profile saved.")

    return profile


def render_real_portfolio_editor():
    """Render and persist current real holdings for strategy context."""
    st.header("Real Portfolio")
    st.caption("Manual holdings only. No broker connection, no live trading, no auto execution.")

    holdings = load_real_holdings()
    if holdings:
        st.dataframe(holdings, width="stretch")
    else:
        st.info("No real holdings saved yet.")

    with st.form("real_holding_form"):
        col1, col2, col3 = st.columns(3)
        symbol = col1.text_input("Symbol", value="").upper()
        shares = col2.number_input("Shares", min_value=0.0, value=0.0, step=1.0)
        cost_basis = col3.number_input("Cost basis per share", min_value=0.0, value=0.0, step=1.0)
        col4, col5 = st.columns(2)
        account_type = col4.selectbox("Account type", ["Taxable", "Traditional IRA", "Roth IRA", "401(k)", "Other"])
        current_value = col5.number_input("Current value", min_value=0.0, value=0.0, step=100.0)
        target_notes = st.text_input("Target notes", value="")
        save_clicked = st.form_submit_button("Save holding")

    if save_clicked:
        if symbol.strip():
            save_real_holding(
                symbol=symbol,
                shares=shares,
                cost_basis=cost_basis,
                account_type=account_type,
                current_value=current_value,
                target_notes=target_notes,
            )
            st.success(f"Saved holding for {symbol}.")
            holdings = load_real_holdings()
        else:
            st.warning("Symbol is required.")

    delete_symbol = st.text_input("Delete holding symbol", value="", key="delete_real_holding_symbol").upper()
    if st.button("Delete holding"):
        if delete_real_holding(delete_symbol):
            st.success(f"Deleted {delete_symbol}.")
            holdings = load_real_holdings()
        else:
            st.warning("No matching holding found.")

    return holdings


def render_sp500_strategy_scan(period, default_rows=None):
    """Render a local S&P 500-style scan control and return scan rows."""
    st.header("S&P 500-Style Scan")
    universe = get_sp500_style_universe()
    col1, col2 = st.columns(2)
    scan_limit = col1.slider("Symbols to scan", min_value=10, max_value=len(universe), value=min(25, len(universe)), step=5)
    col2.metric("Local universe size", len(universe))

    with st.expander("Universe preview", expanded=False):
        st.dataframe(universe[:scan_limit], width="stretch")

    if "sp500_strategy_scan_rows" not in st.session_state:
        st.session_state.sp500_strategy_scan_rows = default_rows or []

    if st.button("Run S&P 500-style scan"):
        symbols = get_sp500_style_symbols(limit=scan_limit)
        st.session_state.sp500_strategy_scan_rows = run_cross_asset_screen(symbols, period=period)

    rows = st.session_state.sp500_strategy_scan_rows or default_rows or []
    if rows:
        st.dataframe(rows[:25], width="stretch")
    else:
        st.info("Run the scan to rank the local S&P 500-style universe. Current watchlist results are used until then.")
    return rows


def _metadata_by_symbol(rows):
    return {str(row.get("symbol", "")).upper(): row for row in rows}


def _enrich_scan_rows_with_growth(scan_rows, universe_rows):
    metadata = _metadata_by_symbol(universe_rows)
    enriched = []
    for row in scan_rows or []:
        symbol = str(row.get("symbol", "")).upper()
        meta = metadata.get(symbol, {})
        combined = {**meta, **row, "symbol": symbol}
        growth = score_growth_discovery(
            symbol,
            combined,
            fundamentals={},
            catalysts={},
            alt_data={},
            source_quality={
                "data_confidence": combined.get("data_confidence", "Unknown"),
                "recommendation_gate": combined.get("recommendation_gate", "Warning"),
            },
        )
        combined.update(
            {
                "growth_score": growth.get("growth_score", 0),
                "growth_label": growth.get("research_label", "Speculative Research"),
                "growth_summary": growth.get("summary", ""),
                "growth_positive_factors": " | ".join(growth.get("positive_factors", [])[:3]),
                "growth_risk_flags": " | ".join(growth.get("risk_flags", [])[:3]),
            }
        )
        enriched.append(combined)
    enriched.sort(key=lambda item: item.get("growth_score", item.get("score", 0)), reverse=True)
    return enriched


def _display_best_opportunity_rows(rows):
    table = []
    for row in rows or []:
        table.append(
            {
                "symbol": row.get("symbol"),
                "company": row.get("company", ""),
                "best_lane": row.get("best_lane"),
                "entry_state": row.get("entry_state"),
                "lane_score": row.get("lane_score"),
                "short_term": row.get("short_term_score"),
                "long_term": row.get("long_term_score"),
                "futures_proxy": row.get("futures_proxy_score"),
                "holding_period": row.get("best_holding_period"),
                "gate": row.get("recommendation_gate"),
                "confidence": row.get("data_confidence"),
                "reason": row.get("lane_reason", ""),
            }
        )
    return table


def render_best_opportunities_workstation(
    scan_rows,
    financial_profile=None,
    accuracy_context=None,
    market_timing=None,
    selected_asset="",
    period="1mo",
    key_suffix="best_opportunities",
):
    """Render best opportunities by lane and any-ticker research."""
    st.header("Best Opportunities Workstation")
    st.caption(
        "Ranks long-term, short-term, and futures-proxy ideas with data gates. "
        "Futures remain ETF/proxy-only; no direct contracts, margin, leverage, or execution."
    )
    result = rank_best_opportunities(
        scan_rows,
        profile=financial_profile or {},
        accuracy_context=accuracy_context or {},
        market_timing=market_timing or {},
        limit=40,
    )
    st.write(result.get("summary", "No best-opportunities summary available."))

    lane_tabs = st.tabs(["All", "Long Term", "Short Term", "Futures Proxy", "Needs Data"])
    with lane_tabs[0]:
        st.dataframe(_display_best_opportunity_rows(result.get("ranked", [])[:30]), width="stretch")
    for tab, lane in zip(lane_tabs[1:], ["Long Term", "Short Term", "Futures Proxy", "Needs Data"]):
        with tab:
            rows = result.get("by_lane", {}).get(lane, [])
            if rows:
                st.dataframe(_display_best_opportunity_rows(rows[:20]), width="stretch")
            else:
                st.write(f"No {lane} rows ranked yet.")

    st.subheader("Any Ticker Research")
    c1, c2 = st.columns([2, 1])
    ticker = c1.text_input(
        "Research any ticker",
        value=selected_asset or "",
        key=f"any_ticker_{key_suffix}",
    ).upper().strip()
    if c2.button("Run Any Ticker Research", key=f"run_any_ticker_{key_suffix}"):
        st.session_state[f"{key_suffix}_any_ticker_packet"] = run_any_ticker_research(
            ticker,
            profile=financial_profile or {},
            accuracy_context=accuracy_context or {},
            market_timing=market_timing or {},
            period=period,
        )

    packet = st.session_state.get(f"{key_suffix}_any_ticker_packet")
    if packet:
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Verdict", packet.get("final_verdict", "Needs Data"))
        p2.metric("Best lane", packet.get("best_lane", "Needs Data"))
        p3.metric("Entry state", packet.get("entry_state", "Needs Data"))
        p4.metric("Data", packet.get("data_quality", {}).get("data_confidence", "Unknown"))
        st.write(packet.get("summary", "No packet summary available."))
        st.markdown("**Lane scores**")
        st.dataframe(
            [{"lane": lane, "score": score} for lane, score in packet.get("lane_scores", {}).items()],
            width="stretch",
        )
        col_e, col_r = st.columns(2)
        with col_e:
            st.markdown("**Evidence**")
            for item in packet.get("evidence", [])[:8]:
                st.success(f"- {item}")
        with col_r:
            st.markdown("**Risks / limits**")
            for item in packet.get("risks", [])[:8] or ["No major risk flags returned."]:
                st.warning(f"- {item}")
        st.markdown("**What would change this**")
        for item in packet.get("what_would_change_this", [])[:6]:
            st.info(f"- {item}")
        st.write(f"Watchlist view: {packet.get('watchlist_view', 'N/A')}")

        if st.button("Save Any Ticker Verdict To Learning Log", key=f"save_any_ticker_{key_suffix}"):
            saved = save_recommendation_log(
                symbol=packet.get("symbol"),
                action=packet.get("final_verdict"),
                horizon=packet.get("best_lane"),
                score=packet.get("score"),
                price=(packet.get("snapshot") or {}).get("price"),
                engine_inputs={
                    "source": "Best Opportunities Any Ticker",
                    "lane": packet.get("best_lane"),
                    "entry_state": packet.get("entry_state"),
                    "lane_scores": packet.get("lane_scores", {}),
                    "data_confidence": packet.get("data_quality", {}).get("data_confidence", "Unknown"),
                    "news_sentiment": (packet.get("news_context") or {}).get("market_sentiment", "Unknown"),
                    "fundamental_quality": (packet.get("fundamentals") or {}).get("fundamental_quality", "Unknown"),
                    "market_regime": packet.get("regime", "Unknown"),
                    "thesis_notes": packet.get("summary", ""),
                },
                data_gate=packet.get("data_quality", {}).get("recommendation_gate", ""),
                suitability_status="Human review required",
                sector=packet.get("sector", map_asset_to_sector(packet.get("symbol"))),
                market_regime=packet.get("regime", ""),
                benchmark_symbol="SPY",
            )
            st.success("Any-ticker verdict logged for future outcome evaluation.")
            st.write(saved)

    return result


def render_opportunity_terminal(period, default_rows=None, financial_profile=None, sector_context=None, macro_context=None, key_suffix="main"):
    """Render the broader opportunity terminal and return scan/timing context."""
    st.header("Opportunity Terminal")
    st.caption(
        "US stocks, global ADRs, ETFs, IPO/recent listings, and up-and-coming themes. "
        "Research-only: no guaranteed growth, no broker execution."
    )

    universe = build_opportunity_universe(scope="US_ADR", include_etfs=True, include_ipos=True)
    col1, col2, col3 = st.columns(3)
    max_rows = max(10, len(universe))
    scan_limit = col1.slider(
        "Opportunity symbols to scan",
        min_value=10,
        max_value=max_rows,
        value=min(40, max_rows),
        step=5,
        key=f"opportunity_terminal_scan_limit_{key_suffix}",
    )
    col2.metric("Universe size", len(universe))
    col3.metric("Scope", "US + ADRs")

    with st.expander("Universe preview", expanded=False):
        st.dataframe(universe[:scan_limit], width="stretch")

    if "opportunity_terminal_rows" not in st.session_state:
        fallback = _enrich_scan_rows_with_growth(default_rows or [], universe)
        st.session_state.opportunity_terminal_rows = fallback

    if st.button("Run Opportunity Terminal scan", key=f"run_opportunity_terminal_scan_{key_suffix}"):
        symbols = get_opportunity_symbols(limit=scan_limit, scope="US_ADR", include_etfs=True, include_ipos=True)
        scanned = run_cross_asset_screen(symbols, period=period)
        st.session_state.opportunity_terminal_rows = _enrich_scan_rows_with_growth(scanned, universe)

    rows = st.session_state.opportunity_terminal_rows or _enrich_scan_rows_with_growth(default_rows or [], universe)
    index_rows = []
    for index_symbol in ["SPY", "QQQ", "IWM"]:
        try:
            snapshot = get_market_snapshot(index_symbol)
            quality = evaluate_data_quality(snapshot)
            existing = next((row for row in rows if row.get("symbol") == index_symbol), {})
            index_rows.append(
                {
                    "symbol": index_symbol,
                    "return_pct": existing.get("return_pct", snapshot.get("change_pct", 0.0)),
                    "volatility_pct": existing.get("volatility_pct", 0.0),
                    "max_drawdown_pct": existing.get("max_drawdown_pct", 0.0),
                    "recommendation_gate": quality.get("recommendation_gate", "Warning"),
                }
            )
        except Exception:
            pass

    timing = build_market_timing_context(
        {"rows": index_rows},
        rows,
        sector_context or {},
        macro_context or {},
        financial_profile or {},
    )

    st.subheader("Market Timing & Crash Risk")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Market risk", timing.get("market_risk_level", "Unknown"))
    c2.metric("Regime", timing.get("timing_regime", "Unknown"))
    c3.metric("Breadth", f"{timing.get('breadth_pct', 0.0):.1f}%")
    c4.metric("Worst index drawdown", f"{timing.get('worst_index_drawdown_pct', 0.0):.1f}%")
    st.write(timing.get("cash_deployment_plan", "No cash deployment view available."))
    for item in timing.get("crash_warning_flags", [])[:4]:
        st.warning(f"- {item}")

    st.subheader("Top Opportunities")
    if rows:
        top_table = []
        for row in rows[:25]:
            top_table.append(
                {
                    "symbol": row.get("symbol"),
                    "company": row.get("company", ""),
                    "theme": row.get("theme", ""),
                    "region": row.get("region", ""),
                    "listing": row.get("listing_type", ""),
                    "growth_label": row.get("growth_label"),
                    "growth_score": row.get("growth_score"),
                    "signal_score": row.get("score"),
                    "return_%": row.get("return_pct"),
                    "volatility_%": row.get("volatility_pct"),
                    "gate": row.get("recommendation_gate"),
                    "confidence": row.get("data_confidence"),
                }
            )
        st.dataframe(top_table, width="stretch")
    else:
        st.info("Run the scan to rank the broader opportunity universe.")

    st.subheader("Up-And-Coming Stocks")
    emerging = [row for row in rows if row.get("growth_label") in {"Strategic Buy Candidate", "Emerging Watchlist", "Wait for Pullback"}]
    st.dataframe(emerging[:15], width="stretch") if emerging else st.write("No up-and-coming candidates ranked yet.")

    st.subheader("Global ADR Watchlist")
    adrs = [row for row in rows if "ADR" in str(row.get("listing_type", "")) or row.get("region") not in {"", "United States"}]
    st.dataframe(adrs[:15], width="stretch") if adrs else st.write("No ADR rows ranked yet.")

    st.subheader("Strategic Buy Zones")
    for item in timing.get("strategic_buy_zones", []):
        st.info(f"- {item}")

    st.subheader("Data Trust Panel")
    blocked = [row for row in rows if row.get("recommendation_gate") == "Blocked"]
    warning = [row for row in rows if row.get("recommendation_gate") == "Warning"]
    d1, d2, d3 = st.columns(3)
    d1.metric("Trusted/usable rows", len(rows) - len(blocked) - len(warning))
    d2.metric("Warning rows", len(warning))
    d3.metric("Blocked rows", len(blocked))
    if blocked:
        st.warning("Blocked symbols can show research but cannot receive buy/sell or auto paper-trade eligibility.")
        st.dataframe(
            [{"symbol": row.get("symbol"), "source": row.get("data_source"), "issues": row.get("data_issues", "")} for row in blocked[:15]],
            width="stretch",
        )

    st.caption(
        "Opportunity rankings are research evidence only. Final Verdict remains the source of truth for actions."
    )
    return {"rows": rows, "market_timing": timing, "universe": universe}


def _display_buy_rows(rows):
    table = []
    for row in rows or []:
        table.append(
            {
                "rank": row.get("buy_finder_rank"),
                "symbol": row.get("symbol"),
                "company": row.get("company", ""),
                "action": row.get("action"),
                "score": row.get("score"),
                "growth_score": row.get("growth_score"),
                "return_%": row.get("return_pct"),
                "volatility_%": row.get("volatility_pct"),
                "gate": row.get("recommendation_gate"),
                "paper_eligible": row.get("paper_trade_eligible"),
                "why": " | ".join(row.get("reasons", [])[:2]),
            }
        )
    return table


def render_buy_finder_terminal(scan_rows, market_timing, financial_profile, real_holdings, accuracy_context=None, key_suffix="main"):
    """Render buy candidates, data-research candidates, and agent task workflow."""
    st.header("Buy Finder")
    st.caption("Finds buy/add ideas while separating weak data from true Avoid evidence. Research-only; no real orders.")
    buy_finder = build_buy_finder(
        scan_rows,
        final_verdicts={},
        market_timing=market_timing,
        profile=financial_profile,
        holdings=real_holdings,
        accuracy_context=accuracy_context or {},
    )
    all_rows = buy_finder.get("all_rows", [])
    action_plan = build_portfolio_action_plan(all_rows, real_holdings, financial_profile, market_timing)
    agent_context = generate_agent_research_tasks(all_rows, scan_rows, action_plan)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Buy candidates", len(buy_finder.get("best_buy_candidates", [])))
    c2.metric("Add candidates", len(buy_finder.get("add_candidates", [])))
    c3.metric("Needs data/research", len(buy_finder.get("needs_data", [])))
    c4.metric("Avoid with evidence", len(buy_finder.get("avoid_with_evidence", [])))
    st.write(buy_finder.get("summary", "No Buy Finder summary available."))

    sections = [
        ("Best Buy Candidates", buy_finder.get("best_buy_candidates", [])),
        ("Add Candidates", buy_finder.get("add_candidates", [])),
        ("Wait for Pullback", buy_finder.get("wait_for_pullback", [])),
        ("Needs Data / Agent Research", buy_finder.get("needs_data", [])),
        ("Avoid With Evidence", buy_finder.get("avoid_with_evidence", [])),
    ]
    for title, rows in sections:
        st.subheader(title)
        table = _display_buy_rows(rows[:15])
        if table:
            st.dataframe(table, width="stretch")
        else:
            st.write("None.")

    st.subheader("Portfolio Optimizer Action Plan")
    actions = action_plan.get("actions", [])
    if actions:
        st.dataframe(actions[:25], width="stretch")
    else:
        st.write("No portfolio action rows yet.")

    st.subheader("Agent Task Queue")
    task_rows = agent_context.get("tasks", [])
    if task_rows:
        st.dataframe(task_rows[:25], width="stretch")
        if st.button("Save generated agent tasks", key=f"save_agent_tasks_{key_suffix}"):
            saved = 0
            for task in task_rows:
                save_agent_research_task(**task)
                saved += 1
            st.success(f"Saved {saved} agent task(s).")
    else:
        st.write("No agent tasks generated yet.")

    saved_tasks = load_agent_research_tasks()
    if saved_tasks:
        with st.expander("Saved agent research queue", expanded=False):
            st.dataframe(saved_tasks[:50], width="stretch")
            options = [f"{row.get('id')} | {row.get('symbol')} | {row.get('task_type')} | {row.get('status')}" for row in saved_tasks]
            choice = st.selectbox("Update task", options, key=f"agent_task_choice_{key_suffix}")
            task_id = int(choice.split(" | ")[0])
            status = st.selectbox("Task status", ["Open", "In Progress", "Done", "Blocked"], key=f"agent_task_status_{key_suffix}")
            findings = st.text_input("Findings update", value="", key=f"agent_task_findings_{key_suffix}")
            if st.button("Update agent task", key=f"update_agent_task_{key_suffix}"):
                update_agent_research_task(task_id, status, findings=findings)
                st.success("Agent task updated.")

    st.subheader("Personal Portfolio Assistant")
    best = buy_finder.get("best_buy_candidates", [])[:3]
    adds = buy_finder.get("add_candidates", [])[:3]
    needs = buy_finder.get("needs_data", [])[:3]
    if best:
        st.success("Best buy candidates to review: " + ", ".join(row.get("symbol", "") for row in best))
    elif adds:
        st.info("No top buy candidates yet. Add candidates to review: " + ", ".join(row.get("symbol", "") for row in adds))
    elif needs:
        st.info("Most useful next work is data/research: " + ", ".join(row.get("symbol", "") for row in needs))
    else:
        st.write("No urgent assistant action from current scan.")
    st.write(action_plan.get("summary", "No portfolio action summary available."))
    st.caption("AIOS-ready task format. Agents assist research and paper testing only; they do not place real trades.")
    return {
        "buy_finder": buy_finder,
        "portfolio_action_plan": action_plan,
        "agent_tasks": agent_context,
    }


def render_portfolio_strategy_advisor(
    financial_profile,
    real_holdings,
    scan_results,
    benchmark_truth=None,
    decision_intelligence=None,
    accuracy_context=None,
):
    """Render advisor-style non-executing portfolio strategy."""
    strategy = build_portfolio_strategy(
        financial_profile,
        real_holdings,
        scan_results,
        benchmark_truth=benchmark_truth,
        decision_intelligence=decision_intelligence,
        accuracy_context=accuracy_context,
    )

    st.header("Portfolio Strategy Evidence")
    suitability = strategy.get("suitability", {})
    col1, col2, col3 = st.columns(3)
    col1.metric("Suitability status", suitability.get("status", "Unknown"))
    col2.metric("Monthly surplus", f"${suitability.get('monthly_surplus', 0.0):,.2f}")
    col3.metric("Emergency fund", f"{suitability.get('emergency_months', 0.0):.1f} months")

    st.markdown("**Cash strategy**")
    cash = strategy.get("cash_strategy", {})
    st.write(f"{cash.get('action', 'N/A')}: {cash.get('reason', 'No cash strategy available.')}")

    for title, key in [
        ("Buy / Add Engine Views", "buy_candidates"),
        ("Trim Engine Views", "trim_candidates"),
        ("Sell Engine Views", "sell_candidates"),
        ("Hold Engine Views", "hold_candidates"),
    ]:
        rows = strategy.get(key, [])
        st.markdown(f"**{title}**")
        if rows:
            table = []
            for row in rows[:10]:
                table.append(
                    {
                        "symbol": row.get("symbol"),
                        "engine_view": row.get("action"),
                        "score": row.get("score"),
                        "confidence": row.get("confidence_level"),
                        "horizon": row.get("time_horizon"),
                        "target": row.get("target_allocation_band"),
                        "risk_budget": row.get("risk_budget"),
                        "data_confidence": row.get("data_confidence"),
                        "gate": row.get("recommendation_gate"),
                        "reason": " | ".join(row.get("reasons", [])[:2]),
                        "risk": " | ".join(row.get("risks", [])[:2]),
                    }
                )
            st.dataframe(table, width="stretch")
        else:
            st.write("None.")

    st.markdown("**Risk actions**")
    if strategy.get("risk_actions"):
        for item in strategy.get("risk_actions", []):
            st.warning(f"- {item}")
    else:
        st.success("No major suitability risk actions triggered.")

    st.markdown("**Accuracy context**")
    accuracy = strategy.get("accuracy_context", {})
    st.write(accuracy.get("summary", "No accuracy context available."))

    st.write(strategy.get("portfolio_summary", "No strategy summary available."))
    st.caption("Evidence only. The Final Verdict panel is the source-of-truth action.")
    return strategy


def _find_strategy_row(strategy, symbol):
    symbol = str(symbol or "").upper()
    for key in ["buy_candidates", "trim_candidates", "sell_candidates", "hold_candidates"]:
        for row in (strategy or {}).get(key, []):
            if str(row.get("symbol", "")).upper() == symbol:
                return row
    return {}


def render_final_recommendation_panel(
    symbol,
    signal_data,
    decision_intelligence,
    advisor_strategy,
    data_quality,
    suitability,
    accuracy_context,
    risk,
    current_holding=None,
    ipo_context=None,
    growth_discovery_context=None,
    market_timing_context=None,
):
    """Render one source-of-truth final verdict and conflict explanation."""
    selected_decision = {}
    for row in (decision_intelligence or {}).get("best_opportunities", []):
        if str(row.get("symbol", "")).upper() == str(symbol).upper():
            selected_decision = row
            break

    strategy_row = _find_strategy_row(advisor_strategy, symbol)
    current_holding = current_holding or {}
    portfolio_context = {
        **(strategy_row or {}),
        "score": strategy_row.get("score", signal_data.get("score", 50)) if strategy_row else signal_data.get("score", 50),
        "volatility_pct": risk.get("volatility_pct", 0.0),
        "max_drawdown_pct": risk.get("max_drawdown_pct", 0.0),
        "has_position": bool(current_holding),
        "current_exposure_pct": strategy_row.get("current_exposure_pct", 0.0) if strategy_row else 0.0,
        "max_single_stock_exposure": 15.0,
        "recommendation_gate": data_quality.get("recommendation_gate", "Warning"),
        "data_confidence": data_quality.get("data_confidence", "Unknown"),
    }
    engine_votes = [
        {
            "engine": "Signal Engine",
            "action": signal_data.get("signal", "Watch"),
            "score": signal_data.get("score", 0),
            "reason": "Raw signal engine view.",
        },
        {
            "engine": "Quant Decision Intelligence",
            "action": selected_decision.get("research_action", "Watch"),
            "score": selected_decision.get("decision_score", 0),
            "reason": selected_decision.get("timing_view", ""),
        },
        {
            "engine": "Portfolio Strategy Advisor",
            "action": strategy_row.get("action", "Watch"),
            "score": strategy_row.get("score", 0),
            "reason": "Portfolio/suitability action view.",
        },
        {
            "engine": "Data Quality Gate",
            "action": "Needs Data" if data_quality.get("recommendation_gate") == "Blocked" else "Watch",
            "score": data_quality.get("data_confidence", ""),
            "reason": data_quality.get("summary", data_quality.get("status", "")),
        },
    ]
    if growth_discovery_context:
        engine_votes.append(
            {
                "engine": "Growth Discovery",
                "action": growth_discovery_context.get("research_label", "Watch"),
                "score": growth_discovery_context.get("growth_score", 0),
                "reason": growth_discovery_context.get("summary", ""),
            }
        )
    if market_timing_context:
        engine_votes.append(
            {
                "engine": "Market Timing",
                "action": "Wait for Pullback"
                if market_timing_context.get("market_risk_level") in {"High", "Elevated"}
                else "Watch",
                "score": market_timing_context.get("market_risk_level", ""),
                "reason": market_timing_context.get("summary", ""),
            }
        )
    final = build_final_recommendation(
        symbol,
        engine_votes,
        portfolio_context,
        data_quality,
        suitability,
        accuracy_context,
        ipo_context=ipo_context,
        growth_discovery_context=growth_discovery_context,
        market_timing_context=market_timing_context,
    )

    st.header("Final Verdict")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Verdict", final.get("final_verdict", "Watch"))
    col2.metric("Confidence", final.get("confidence", "Low"))
    col3.metric("Time horizon", final.get("time_horizon", "Swing"))
    col4.metric("Paper eligible", "Yes" if final.get("paper_trade_eligible") else "No")

    st.write(f"Position guidance: {final.get('position_guidance', 'N/A')}")
    st.write(f"Risk budget: {final.get('risk_budget', 'N/A')}")
    if final.get("market_regime") or final.get("market_risk_level"):
        st.write(
            f"Market timing: {final.get('market_regime', 'Unknown')} / "
            f"{final.get('market_risk_level', 'Unknown')} risk."
        )
    if final.get("strategic_buy_zone"):
        st.write(f"Strategic buy-zone condition: {final.get('strategic_buy_zone')}")
    if final.get("growth_discovery_label"):
        st.write(
            f"Growth discovery: {final.get('growth_discovery_label')} "
            f"({final.get('growth_discovery_score', 0):.0f}/100)."
        )
    st.write(final.get("summary", "No final verdict summary available."))

    if final.get("vetoes"):
        st.markdown("**Vetoes / downgrades**")
        for item in final.get("vetoes", []):
            st.warning(f"- {item}")

    st.markdown("**Why this final verdict won**")
    for item in final.get("why", []):
        st.success(f"- {item}")

    st.markdown("**Conflict explanation**")
    st.write(final.get("conflict_summary", "No conflicts available."))
    st.dataframe(final.get("conflict_rows", []), width="stretch")

    st.markdown("**What would change this decision**")
    for item in final.get("what_would_change_this", []):
        st.info(f"- {item}")

    st.caption("This final verdict is the source-of-truth action. Other sections are evidence only; no broker execution.")
    return final


def render_ipo_research(symbol=None):
    """Render IPO and recent-listing research context."""
    context = generate_ipo_research_context(symbol)
    st.header("IPO Research")
    st.caption("IPO rows are research-only until listed and enough market data exists.")
    rows = context.get("ipo_candidates", [])
    if rows:
        st.dataframe(rows, width="stretch")
    else:
        st.info(context.get("summary", "No IPO candidates available."))
    selected = context.get("selected_ipo", {})
    if selected:
        st.write(selected.get("summary", "No selected IPO summary."))
        for item in selected.get("risk_flags", []):
            st.warning(f"- {item}")
    return context


def render_broker_alert_tickets(final_recommendation):
    """Render non-executing broker alert ticket workflow."""
    st.header("Broker Alert Tickets")
    st.caption("Alerts are manual review tickets only. No broker API, no live order, no execution.")
    final_recommendation = final_recommendation or {}

    if final_recommendation.get("alert_eligible"):
        if st.button("Save broker alert ticket"):
            saved = save_broker_alert(
                symbol=final_recommendation.get("symbol"),
                action=final_recommendation.get("final_verdict"),
                confidence=final_recommendation.get("confidence"),
                ticket_details={
                    "time_horizon": final_recommendation.get("time_horizon"),
                    "position_guidance": final_recommendation.get("position_guidance"),
                    "risk_budget": final_recommendation.get("risk_budget"),
                    "conflict_summary": final_recommendation.get("conflict_summary"),
                    "manual_checklist": final_recommendation.get("what_would_change_this", []),
                },
            )
            st.success("Broker alert ticket saved for manual review.")
            st.write(saved)
    else:
        st.info("Final verdict is not eligible for an alert ticket.")

    alerts = load_broker_alerts()
    if alerts:
        st.dataframe(alerts[:10], width="stretch")
    else:
        st.write("No broker alert tickets saved yet.")

    with st.expander("Resolve alert", expanded=False):
        if alerts:
            options = [f"{row.get('id')} | {row.get('symbol')} | {row.get('action')} | {row.get('status')}" for row in alerts]
            choice = st.selectbox("Alert", options)
            alert_id = int(choice.split(" | ")[0])
            status = st.selectbox("Status", ["Pending", "Resolved", "Dismissed"])
            notes = st.text_input("Outcome notes", value="")
            if st.button("Update alert status"):
                update_broker_alert_status(alert_id, status, outcome_notes=notes)
                st.success("Alert updated.")
        else:
            st.write("No alerts to resolve.")
    return alerts


def render_recommendation_logger(strategy, current_prices=None):
    """Allow saving strategy recommendations into the learning log."""
    st.header("Recommendation Logger")
    st.caption("Logs recommendations for later outcome learning. No broker APIs or execution.")
    current_prices = current_prices or {}
    strategy = strategy or {}

    rows = []
    for key in ["buy_candidates", "trim_candidates", "sell_candidates", "hold_candidates"]:
        rows.extend(strategy.get(key, []))

    actionable = [row for row in rows if row.get("action") in {"Buy Candidate", "Add", "Trim", "Sell Candidate", "Hold"}]
    if not actionable:
        st.info("No recommendation rows available to log yet.")
        return None

    labels = [
        f"{row.get('symbol')} | {row.get('action')} | {row.get('time_horizon', 'Swing')} | score {row.get('score', 0)}"
        for row in actionable
    ]
    selected = st.selectbox("Recommendation to log", labels)
    selected_row = actionable[labels.index(selected)]

    if st.button("Save recommendation to learning log"):
        saved = save_recommendation_log(
            symbol=selected_row.get("symbol"),
            action=selected_row.get("action"),
            horizon=selected_row.get("time_horizon", "Swing"),
            score=selected_row.get("score", 0),
            price=current_prices.get(selected_row.get("symbol")),
            engine_inputs={
                "reasons": selected_row.get("reasons", []),
                "risks": selected_row.get("risks", []),
                "lane": selected_row.get("best_lane", selected_row.get("time_horizon", "Swing")),
                "entry_state": selected_row.get("entry_state", selected_row.get("action")),
                "lane_scores": {
                    "short_term_score": selected_row.get("short_term_score"),
                    "long_term_score": selected_row.get("long_term_score"),
                    "futures_proxy_score": selected_row.get("futures_proxy_score"),
                },
                "data_confidence": selected_row.get("data_confidence", "Unknown"),
                "news_sentiment": selected_row.get("news_sentiment", "Unknown"),
                "fundamental_quality": selected_row.get("fundamental_quality", "Unknown"),
                "market_regime": selected_row.get("regime", ""),
                "thesis_notes": " | ".join(selected_row.get("reasons", [])[:3]),
                "target_allocation_band": selected_row.get("target_allocation_band", ""),
                "risk_budget": selected_row.get("risk_budget", ""),
                "invalidation_triggers": selected_row.get("invalidation_triggers", []),
            },
            data_gate=selected_row.get("recommendation_gate", ""),
            suitability_status=(strategy.get("suitability") or {}).get("status", ""),
            sector=map_asset_to_sector(selected_row.get("symbol", "")),
            market_regime=selected_row.get("regime", ""),
        )
        st.success("Recommendation logged.")
        st.write(saved)

    return selected_row


def render_recommendation_learning_dashboard(current_prices=None):
    """Render recommendation accuracy, outcome updates, and experiment guidance."""
    logs = load_recommendation_log()
    accuracy = evaluate_recommendation_accuracy(logs, current_prices=current_prices or {})
    learning = build_learning_dashboard_context(accuracy)

    st.header("Recommendation Learning Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Logged", accuracy.get("total_recommendations", 0))
    col2.metric("Evaluated", accuracy.get("evaluated_count", 0))
    col3.metric("Hit rate", f"{accuracy.get('hit_rate', 0.0):.2f}%")
    col4.metric("Avg return", f"{accuracy.get('average_return_pct', 0.0):+.2f}%")

    col5, col6, col7 = st.columns(3)
    col5.metric("Avg alpha", f"{accuracy.get('average_alpha_pct', 0.0):+.2f}%")
    col6.metric("False positives", accuracy.get("false_positive_count", 0))
    col7.metric("Confidence adj.", f"{accuracy.get('confidence_adjustment', 0.0):+.1f}")

    st.markdown("**What is working**")
    for item in learning.get("working", []):
        st.success(f"- {item}")

    st.markdown("**What is not working**")
    for item in learning.get("not_working", []):
        st.warning(f"- {item}")

    st.markdown("**Next best experiments**")
    for item in learning.get("next_experiments", []):
        st.info(f"- {item}")

    if accuracy.get("horizon_stats"):
        st.markdown("**Timeframe stats**")
        st.dataframe(accuracy.get("horizon_stats", []), width="stretch")
    if accuracy.get("lane_stats"):
        st.markdown("**Lane stats**")
        st.dataframe(accuracy.get("lane_stats", []), width="stretch")
    if accuracy.get("sector_stats"):
        st.markdown("**Sector stats**")
        st.dataframe(accuracy.get("sector_stats", []), width="stretch")
    if accuracy.get("data_confidence_stats"):
        st.markdown("**Data confidence stats**")
        st.dataframe(accuracy.get("data_confidence_stats", []), width="stretch")
    if accuracy.get("factor_stats"):
        with st.expander("Factor stats", expanded=False):
            st.markdown("**News sentiment**")
            st.dataframe(accuracy.get("factor_stats", {}).get("news_sentiment", []), width="stretch")
            st.markdown("**Fundamental quality**")
            st.dataframe(accuracy.get("factor_stats", {}).get("fundamental_quality", []), width="stretch")

    audit = build_research_process_audit(accuracy)
    st.subheader("Research Process Audit")
    a1, a2 = st.columns(2)
    with a1:
        st.markdown("**Overconfidence warnings**")
        for item in audit.get("overconfidence_warnings", []):
            st.warning(f"- {item}")
        st.markdown("**Repeated mistake patterns**")
        for item in audit.get("repeated_mistake_patterns", []):
            st.warning(f"- {item}")
    with a2:
        st.markdown("**Missed risk flags**")
        for item in audit.get("missed_risk_flags", []):
            st.info(f"- {item}")
        st.markdown("**Benchmark notes**")
        for item in audit.get("benchmark_notes", []):
            st.info(f"- {item}")

    with st.expander("Update recommendation outcome", expanded=False):
        if logs:
            options = [
                f"{row.get('id')} | {row.get('symbol')} | {row.get('action')} | {row.get('horizon')}"
                for row in logs
            ]
            choice = st.selectbox("Logged recommendation", options)
            selected_id = int(choice.split(" | ")[0])
            outcome_price = st.number_input("Outcome price", min_value=0.0, value=0.0, step=1.0)
            realized_return = st.number_input("Realized return %", value=0.0, step=0.5)
            drawdown = st.number_input("Max drawdown after signal %", value=0.0, step=0.5)
            alpha = st.number_input("Alpha vs benchmark %", value=0.0, step=0.5)
            label = st.selectbox("Outcome label", ["Pending", "Win", "Loss", "Mixed"])
            lesson = st.text_input("Lesson", value="")
            if st.button("Update recommendation outcome"):
                update_recommendation_outcome(
                    selected_id,
                    outcome_price=outcome_price,
                    realized_return_pct=realized_return,
                    max_drawdown_after_signal=drawdown,
                    alpha_vs_benchmark_pct=alpha,
                    outcome_label=label,
                    lesson=lesson,
                )
                st.success("Outcome updated.")
        else:
            st.write("No recommendation logs yet.")

    st.write(learning.get("summary", "No learning summary available."))
    st.caption("Learning dashboard is descriptive research support only. No auto execution or guaranteed returns.")
    return accuracy


def render_opportunistic_stock_screener(screened_assets, research_mode):
    """Render balanced-growth opportunity ranking for stocks/ETFs."""
    result = rank_opportunistic_stocks(screened_assets, research_mode=research_mode)
    rows = result.get("ranked_opportunities", [])

    st.header("Opportunistic Stock Screener")
    if rows:
        st.dataframe(rows, width="stretch")
    else:
        st.write("No opportunity rows available.")

    best = result.get("best_candidate", {})
    if best:
        st.metric(
            "Top research candidate",
            f"{best.get('symbol', 'N/A')} ({best.get('opportunity_score', 0)}/100)",
        )

    st.write(result.get("summary", "No opportunity summary available."))
    st.caption(
        "Research-only opportunity labels. No live trading, broker APIs, exchange APIs, or guaranteed outcomes."
    )


def render_cross_asset_screener(watchlist, period):
    """Render a cross-asset screener using the same research-only logic."""
    rows = run_cross_asset_screen(watchlist, period=period)
    render_cross_asset_screener_from_rows(rows)


def render_opportunity_engine(
    screened_assets,
    research_mode,
    sector_context=None,
    asset_class=None,
):
    """Render ranked research opportunities from screened assets."""
    st.header("Opportunity Ranking Engine")
    ranking = rank_opportunities(
        screened_assets,
        research_mode=research_mode,
        sector_context=sector_context,
        asset_class=asset_class,
    )
    opportunities = ranking.get("ranked_opportunities", [])

    if opportunities:
        st.dataframe(opportunities, width="stretch")
    else:
        st.write("No opportunities could be ranked from the current screener output.")

    best = ranking.get("best_opportunity", {})
    highest_risk = ranking.get("highest_risk_opportunity", {})

    col1, col2 = st.columns(2)
    col1.metric(
        "Best opportunity",
        f"{best.get('symbol', 'N/A')} ({best.get('opportunity_score', 0)}/100)",
    )
    col2.metric(
        "Highest risk opportunity",
        f"{highest_risk.get('symbol', 'N/A')} ({highest_risk.get('volatility_pct', 0.0):.2f}% vol)",
    )

    st.write(ranking.get("summary", "No summary available."))
    if sector_context:
        st.caption("Sector context included.")
    st.caption(
        "Research-only ranking: no broker APIs, no live trading, no auto execution, and no guaranteed profit."
    )


def render_watchlist_drift_engine(screened_assets, research_mode):
    """Render watchlist drift alerts based on prior screener snapshot."""
    st.header("Watchlist Drift / Alert Engine")
    previous_snapshot = load_previous_watchlist_snapshot()
    drift = detect_watchlist_drift(
        screened_assets,
        prior_screened_assets=previous_snapshot,
        research_mode=research_mode,
    )

    alerts = drift.get("alerts", [])
    if alerts:
        st.dataframe(alerts, width="stretch")
    else:
        st.write("No active drift alerts.")

    top_alert = drift.get("highest_priority_alert", {})
    if top_alert:
        st.write(
            f"**Highest priority alert:** {top_alert.get('symbol', 'N/A')} | "
            f"{top_alert.get('drift_type', 'N/A')} | {top_alert.get('severity', 'N/A')}"
        )

    stable_assets = drift.get("stable_assets", [])
    if stable_assets:
        st.write(f"**Stable assets:** {', '.join(stable_assets)}")
    else:
        st.write("**Stable assets:** None identified in this pass.")

    st.write(drift.get("summary", "No drift summary available."))
    st.caption("Research-only drift monitoring. No broker APIs, no live trading, no auto execution.")

    # Save the latest snapshot for future drift comparisons.
    save_watchlist_snapshot(screened_assets)


def render_portfolio_optimizer(
    screened_assets,
    research_mode,
    sector_context=None,
    optimizer_result=None,
):
    """Render a simple research-only portfolio allocation optimizer."""
    st.header("Portfolio Allocation Optimizer")
    optimizer = optimizer_result
    if optimizer is None:
        optimizer = generate_portfolio_allocation(
            screened_assets,
            research_mode=research_mode,
            sector_context=sector_context,
        )

    allocations = optimizer.get("allocations", [])
    if allocations:
        st.dataframe(allocations, width="stretch")
    else:
        st.write("No allocation candidates were produced from the current screener output.")

    col1, col2 = st.columns(2)
    col1.metric("Cash buffer", f"{optimizer.get('cash_buffer_pct', 0):.0f}%")
    col2.metric("Portfolio risk level", optimizer.get("portfolio_risk_level", "Unknown"))

    st.write(optimizer.get("summary", "No summary available."))
    if sector_context:
        st.caption("Sector context included.")
    st.caption(
        "Research-only allocation idea: no leverage, no shorting, no live execution, and no broker APIs."
    )
    return optimizer


def render_portfolio_optimizer_v1(ranked_assets, research_mode="Balanced"):
    """Render V1 optimizer view for ranked assets with explicit concentration messaging."""
    st.header("Portfolio Optimizer")
    from portfolio_optimizer import optimize_portfolio

    optimized = optimize_portfolio(
        ranked_assets,
        research_mode=research_mode,
    )
    rows = optimized.get("recommended_allocations", [])
    if rows:
        st.dataframe(rows, width="stretch")
    else:
        st.write("No recommended allocations were produced.")

    col1, col2 = st.columns(2)
    col1.metric("Cash allocation", f"{optimized.get('cash_allocation_pct', 0.0):.2f}%")
    col2.metric("Portfolio risk level", optimized.get("portfolio_risk_level", "Unknown"))
    st.warning(optimized.get("concentration_warning", "No concentration warning."))
    st.write(optimized.get("summary", "No optimizer summary available."))
    st.caption("Research-only optimizer output. No broker APIs, no live trading, no auto execution.")
    return optimized


def render_benchmark_truth(portfolio_returns, benchmark_data):
    """Render benchmark truth comparison against passive ETF baselines."""
    st.header("Benchmark Truth Engine")
    truth = compare_to_benchmarks(
        portfolio_returns,
        benchmark_data,
    )
    col1, col2 = st.columns(2)
    col1.metric("Best benchmark", truth.get("best_benchmark", "N/A"))
    col2.metric("AI vs benchmark", f"{truth.get('ai_outperformance_pct', 0.0):+.2f}%")

    st.write(f"Volatility: {truth.get('volatility_comparison', 'N/A')}")
    st.write(f"Drawdown: {truth.get('drawdown_comparison', 'N/A')}")
    st.write(f"Sharpe: {truth.get('sharpe_comparison', 'N/A')}")
    st.write(f"Verdict: {truth.get('verdict', 'Needs More Data')}")
    st.write(truth.get("summary", "No benchmark truth summary available."))
    st.caption(
        "Research-only benchmark truth. No broker APIs, no live trading, no auto execution, and no guaranteed outperformance."
    )
    return truth


def render_rebalance_advisor(
    current_allocations,
    recommended_allocations,
    research_mode,
    sector_context,
):
    """Render a simple research-only portfolio rebalance advisor."""
    st.header("Portfolio Rebalance Advisor")
    rebalance = generate_rebalance_plan(
        current_allocations,
        recommended_allocations,
        research_mode=research_mode,
        sector_context=sector_context,
    )

    actions = rebalance.get("rebalance_actions", [])
    if actions:
        st.dataframe(actions, width="stretch")
    else:
        st.write("No rebalance actions available.")

    largest_shift = rebalance.get("largest_shift", {})
    col1, col2 = st.columns(2)
    col1.metric(
        "Largest shift",
        f"{largest_shift.get('symbol', 'N/A')} ({largest_shift.get('change_pct', 0):+.2f}%)",
    )
    col2.metric("Portfolio turnover", f"{rebalance.get('portfolio_turnover_pct', 0.0):.2f}%")

    st.warning(rebalance.get("risk_note", "No risk note available."))
    st.write(rebalance.get("summary", "No summary available."))
    st.caption(
        "Research-only rebalance guidance: no forced rebalancing, no broker APIs, and no live execution."
    )


def render_exposure_limits_engine(
    portfolio_allocations,
    screened_assets,
    conviction_data,
    research_mode,
):
    """Render portfolio concentration and exposure limit checks."""
    exposure = evaluate_portfolio_exposure_limits(
        portfolio_allocations,
        screened_assets,
        conviction_data=conviction_data,
        research_mode=research_mode,
    )

    st.header("Portfolio Exposure Limits Engine")

    sector_rows = exposure.get("sector_exposure", [])
    if sector_rows:
        st.markdown("**Sector exposure**")
        st.dataframe(sector_rows, width="stretch")
    else:
        st.write("No sector exposure data available.")

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "High-vol exposure",
        f"{exposure.get('high_vol_exposure_pct', 0.0):.2f}%",
    )
    col2.metric(
        "Top position concentration",
        f"{exposure.get('top_position_concentration_pct', 0.0):.2f}%",
    )
    col3.metric(
        "Top 3 concentration",
        f"{exposure.get('top_3_concentration_pct', 0.0):.2f}%",
    )

    st.markdown("**Exposure status**")
    st.write(exposure.get("exposure_status", "Unknown"))

    st.markdown("**Risk flags**")
    flags = exposure.get("risk_flags", [])
    if flags:
        for flag in flags:
            st.warning(f"- {flag}")
    else:
        st.success("No concentration risk flags were triggered.")

    st.markdown("**Suggested reductions**")
    reductions = exposure.get("suggested_reductions", [])
    if reductions:
        for item in reductions:
            st.info(f"- {item}")
    else:
        st.write("No immediate reductions suggested.")

    st.write(exposure.get("summary", "No summary available."))
    st.caption("Research-only concentration checks for paper-trading workflows.")
    return exposure


def render_correlation_engine(
    screened_assets,
    portfolio_allocations,
    research_mode,
):
    """Render simple cross-asset overlap and correlation clusters."""
    correlation = analyze_cross_asset_correlation(
        screened_assets,
        portfolio_allocations=portfolio_allocations,
        research_mode=research_mode,
    )

    st.header("Cross-Asset Correlation Engine")

    groups = correlation.get("correlation_groups", [])
    if groups:
        st.dataframe(groups, width="stretch")
    else:
        st.write("No correlation groups available.")

    cluster = correlation.get("most_correlated_cluster", {})
    st.markdown("**Most correlated cluster**")
    if cluster:
        st.write(
            f"{cluster.get('group_name', 'N/A')} | "
            f"Risk: {cluster.get('risk_level', 'N/A')} | "
            f"Assets: {', '.join(cluster.get('assets', []))}"
        )
    else:
        st.write("No dominant cluster identified.")

    st.markdown("**Hidden concentration risk**")
    st.warning(correlation.get("hidden_concentration_risk", "No risk statement available."))

    st.metric("Diversification score", f"{correlation.get('diversification_score', 0)}/100")
    st.write(correlation.get("summary", "No summary available."))
    st.caption(
        "Research-only correlation context for paper-trading workflows. No broker APIs, no live execution."
    )
    return correlation


def render_capital_hierarchy_engine(
    screened_assets,
    portfolio_allocations,
    conviction_data,
    execution_data,
    alpha_data,
    correlation_data,
    research_mode,
):
    """Render ranked capital priority tiers across screened assets."""
    hierarchy = build_capital_allocation_hierarchy(
        screened_assets,
        portfolio_allocations=portfolio_allocations,
        conviction_data=conviction_data,
        execution_data=execution_data,
        alpha_data=alpha_data,
        correlation_data=correlation_data,
        research_mode=research_mode,
    )

    st.header("Capital Allocation Hierarchy Engine")

    rows = hierarchy.get("capital_hierarchy", [])
    if rows:
        st.dataframe(rows, width="stretch")
    else:
        st.write("No hierarchy rows available yet.")

    top = hierarchy.get("top_capital_candidate", {})
    low = hierarchy.get("lowest_priority_asset", {})
    col1, col2 = st.columns(2)
    col1.metric(
        "Top capital candidate",
        f"{top.get('symbol', 'N/A')} ({top.get('tier', 'N/A')})",
    )
    col2.metric(
        "Lowest priority asset",
        f"{low.get('symbol', 'N/A')} ({low.get('tier', 'N/A')})",
    )

    st.markdown("**Portfolio efficiency view**")
    st.write(hierarchy.get("portfolio_efficiency_view", "No efficiency view available."))
    st.write(hierarchy.get("summary", "No summary available."))
    st.caption("Research-only hierarchy guidance for paper trading. No leverage, no auto execution.")
    return hierarchy


def render_allocation_timing_recommendation(
    symbol,
    conviction_data,
    signal_data,
    opportunity_data,
    regime_data,
    news_context,
    catalyst_data,
    backtest_results,
    strategy_lab_results,
    benchmark_results,
    risk,
    research_mode,
):
    """Render research-only allocation and timing recommendation."""
    recommendation = generate_allocation_timing_recommendation(
        symbol,
        conviction_data,
        signal_data,
        opportunity_data,
        regime_data,
        news_context,
        catalyst_data,
        backtest_results,
        strategy_lab_results,
        benchmark_results,
        risk,
        research_mode=research_mode,
    )

    st.header("Allocation & Timing Recommendation")
    col1, col2, col3 = st.columns(3)
    col1.metric("Recommended action", recommendation.get("recommended_action", "Watch"))
    col2.metric("Suggested allocation %", f"{recommendation.get('suggested_allocation_pct', 0):.2f}%")
    col3.metric("Confidence level", recommendation.get("confidence_level", "Low"))

    st.markdown("**Timing view**")
    st.write(recommendation.get("timing_view", "No timing view available."))

    st.markdown("**Why**")
    for item in recommendation.get("why", []):
        st.success(f"- {item}")

    st.markdown("**Risks**")
    for item in recommendation.get("risks", []):
        st.warning(f"- {item}")

    st.markdown("**Benchmark comparison**")
    st.write(recommendation.get("benchmark_comparison", "No benchmark comparison available."))

    st.markdown("**Required conditions**")
    for item in recommendation.get("required_conditions", []):
        st.info(f"- {item}")

    st.caption(recommendation.get("disclaimer", "This is research-only decision support, not financial advice or trade execution."))


def render_alpha_engine(
    selected_asset,
    price_data,
    paper_trade_results=None,
    period="1mo",
    key_suffix="default",
):
    """Render alpha comparison versus a selected benchmark."""
    st.header("Alpha vs Benchmark Engine")
    benchmark_symbol = st.selectbox(
        "Benchmark",
        ["SPY", "QQQ", "VOO"],
        index=0,
        key=f"alpha_benchmark_select_{key_suffix}",
    )

    alpha = analyze_alpha_vs_benchmark(
        selected_asset,
        price_data,
        paper_trade_results=paper_trade_results,
        benchmark_symbol=benchmark_symbol,
        period=period,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Asset return", f"{alpha.get('asset_return_pct', 0.0):+.2f}%")
    col2.metric("Benchmark return", f"{alpha.get('benchmark_return_pct', 0.0):+.2f}%")
    col3.metric("Alpha", f"{alpha.get('alpha_pct', 0.0):+.2f}%")

    col4, col5, col6 = st.columns(3)
    col4.metric("Volatility gap", f"{alpha.get('volatility_gap', 0.0):+.2f}%")
    col5.metric("Drawdown gap", f"{alpha.get('drawdown_gap', 0.0):+.2f}%")
    col6.metric("Outperformance", alpha.get("outperformance_status", "Neutral"))

    st.write(f"Relative strength: {alpha.get('relative_strength', 'Mixed')}")
    st.write(alpha.get("summary", "No alpha summary available."))
    st.caption(
        "Research-only benchmark comparison. No broker APIs, no live trading, no auto execution, and no guaranteed alpha."
    )
    return alpha


def render_best_etf_benchmark(period):
    """Render the strongest ETF benchmark in the default benchmark basket."""
    benchmark = find_best_etf_benchmark(period=period)
    st.header("Best ETF Benchmark Basket")

    rows = benchmark.get("benchmark_basket", [])
    best = benchmark.get("best_benchmark", {})
    if best:
        st.metric(
            "Best ETF benchmark",
            f"{best.get('symbol', 'N/A')} ({best.get('return_pct', 0.0):+.2f}%)",
        )
    if rows:
        st.dataframe(rows, width="stretch")
    else:
        st.write("No benchmark basket data available.")

    st.write(benchmark.get("summary", "No benchmark summary available."))
    st.caption("Research-only benchmark comparison. No guaranteed outperformance.")
    return benchmark


def render_strategy_scorecard(paper_performance, benchmark_data, paper_positions):
    """Render paper strategy performance versus best ETF benchmark."""
    scorecard = generate_strategy_scorecard(
        paper_performance,
        benchmark_data,
        paper_positions=paper_positions,
    )

    st.header("Strategy Scorecard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Paper strategy return", f"{scorecard.get('strategy_total_return_pct', 0.0):+.2f}%")
    col2.metric("Best ETF", f"{scorecard.get('best_etf_symbol', 'N/A')} ({scorecard.get('best_etf_return_pct', 0.0):+.2f}%)")
    col3.metric("Alpha vs best ETF", f"{scorecard.get('alpha_vs_best_etf_pct', 0.0):+.2f}%")

    col4, col5, col6 = st.columns(3)
    col4.metric("Win rate", f"{scorecard.get('win_rate', 0.0):.2f}%")
    col5.metric("Trades", scorecard.get("number_of_trades", 0))
    col6.metric("Status", scorecard.get("status", "Needs More Data"))

    st.write(f"Average position size: {scorecard.get('average_position_size_pct', 0.0):.2f}%")
    st.write(f"Best position: {scorecard.get('best_position', 'N/A')}")
    st.write(f"Worst position: {scorecard.get('worst_position', 'N/A')}")
    st.write(scorecard.get("learning_state", "No learning state available."))
    st.write(scorecard.get("summary", "No scorecard summary available."))
    st.caption("Paper strategy evaluation only. No live trading, no broker APIs, no guaranteed alpha.")
    return scorecard


def render_auto_paper_trading_control_panel(
    symbol,
    snapshot,
    meta_decision,
    execution_data,
    position_size_data,
    entry_exit_data,
    exposure_limits_data,
    correlation_data,
    benchmark_data,
    data_confidence,
    existing_position,
    research_mode,
    final_recommendation=None,
):
    """Render auto paper trade ticket preview and save control."""
    ticket = build_auto_paper_trade_ticket(
        symbol,
        snapshot,
        meta_decision,
        execution_data,
        position_size_data,
        entry_exit_data,
        exposure_limits_data,
        correlation_data,
        benchmark_data,
        data_confidence=data_confidence,
        existing_position=existing_position,
        research_mode=research_mode,
        final_recommendation=final_recommendation,
    )

    st.header("Auto Paper Trading Control Panel")
    st.caption("Daily-close style simulated trading only. No live orders, broker APIs, shorts, leverage, options, or futures contracts.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Decision", ticket.get("action", "Skip"))
    col2.metric("Paper allocation", f"{ticket.get('suggested_paper_allocation_pct', 0.0):.2f}%")
    col3.metric("Quantity", ticket.get("quantity", 0.0))

    st.markdown("**Trade Ticket Preview**")
    st.write(f"Symbol: {ticket.get('symbol', 'N/A')}")
    st.write(f"Action: {ticket.get('action', 'Skip')}")
    st.write(f"Price: ${ticket.get('price', 0.0):,.2f}")
    st.write(f"Reason: {ticket.get('reason', 'N/A')}")
    st.write(ticket.get("benchmark_context", "No benchmark context available."))
    st.write(f"Data confidence: {ticket.get('data_confidence', 'Unknown')}")

    st.markdown("**Risk controls passed**")
    for item in ticket.get("risk_controls_passed", []):
        st.success(f"- {item}")
    if not ticket.get("risk_controls_passed"):
        st.write("No controls passed.")

    st.markdown("**Risk controls failed**")
    for item in ticket.get("risk_controls_failed", []):
        st.warning(f"- {item}")
    if not ticket.get("risk_controls_failed"):
        st.write("No failed controls.")

    if st.button("Save simulated auto paper trade"):
        result = save_auto_paper_trade(ticket)
        if result.get("saved"):
            st.success(result.get("message", "Simulated trade saved."))
            st.write(result.get("trade", {}))
        else:
            st.info(result.get("message", "No simulated trade saved."))

    st.caption(ticket.get("disclaimer", "Paper trade simulation only."))
    return ticket


def render_ranked_quant_decision_table(
    screened_assets,
    opportunity_data,
    selected_symbol,
    conviction_data,
    thesis_health,
):
    """Render a clear ranked decision table across screened assets."""
    st.header("Ranked Quant Decision Table")
    rows = build_ranked_decision_table(
        screened_assets,
        opportunity_data=opportunity_data,
        selected_symbol=selected_symbol,
        selected_conviction=conviction_data,
        selected_thesis_health=thesis_health,
    )
    if rows:
        st.dataframe(rows, width="stretch")
    else:
        st.info("No screened assets are available for ranking yet.")
    st.caption(
        "Actions are research-only labels. They are not broker orders, trade execution, or guaranteed outcomes."
    )
    return rows


def render_quant_decision_intelligence(
    ranked_assets,
    conviction_scores,
    signal_outputs,
    benchmark_truth,
    portfolio_optimizer,
    governance_review,
    walk_forward_results,
    research_mode="Balanced",
):
    """Render the primary research-first decision intelligence layer."""
    intelligence = build_quant_decision_intelligence(
        ranked_assets,
        conviction_scores,
        signal_outputs,
        benchmark_truth,
        portfolio_optimizer,
        governance_review,
        walk_forward_results,
        research_mode=research_mode,
    )

    st.header("Quant Decision Intelligence")
    st.caption(
        "Research-only decision support. No broker APIs, no live trading, no auto execution, "
        "no guaranteed returns, and no buy-now certainty."
    )

    opportunities = intelligence.get("best_opportunities", [])
    if opportunities:
        table_rows = []
        for row in opportunities:
            table_rows.append(
                {
                    "Rank": row.get("priority_rank", 0),
                    "Symbol": row.get("symbol", ""),
                    "Decision Score": row.get("decision_score", 0),
                    "Research Action": row.get("research_action", ""),
                    "Timing View": row.get("timing_view", ""),
                    "Position Size Hint": row.get("position_size_hint", ""),
                }
            )
        st.dataframe(table_rows, width="stretch")

        for row in opportunities[:5]:
            with st.expander(
                f"Why {row.get('symbol', 'asset')} ranked #{row.get('priority_rank', 0)}",
                expanded=row.get("priority_rank") == 1,
            ):
                st.write(f"Research action: {row.get('research_action', 'N/A')}")
                st.write(f"Timing view: {row.get('timing_view', 'N/A')}")
                st.write(f"Position size hint: {row.get('position_size_hint', 'N/A')}")
                st.markdown("**Why**")
                for item in row.get("why", []):
                    st.info(f"- {item}")
    else:
        st.info("No ranked opportunities are available for decision intelligence yet.")

    col1, col2 = st.columns(2)
    col1.metric("Portfolio stance", intelligence.get("portfolio_stance", "N/A"))
    col2.metric(
        "Human review required",
        "Yes" if intelligence.get("human_review_required", True) else "No",
    )

    st.markdown("**Capital deployment view**")
    st.write(intelligence.get("capital_deployment_view", "No capital view available."))

    st.markdown("**Risk summary**")
    st.warning(intelligence.get("risk_summary", "No risk summary available."))

    st.markdown("**Benchmark truth summary**")
    st.write(intelligence.get("benchmark_truth_summary", "No benchmark summary available."))

    st.write(intelligence.get("summary", "No decision intelligence summary available."))
    return intelligence


def render_explainability_panel(
    signal_data,
    conviction_data,
    regime_data,
    news_context,
    opportunity_data,
    risk,
    exposure_limits_data,
    thesis_health,
    confidence_data,
):
    """Render weighted engine contributions to the final decision-support score."""
    st.header("Explainability Panel")
    explanation = calculate_explainability_panel(
        signal_data,
        conviction_data,
        regime_data,
        news_context,
        opportunity_data,
        risk,
        exposure_limits_data,
        thesis_health,
        confidence_data,
    )
    st.metric("Final explainability score", f"{explanation.get('final_score', 0):.1f}/100")
    st.dataframe(explanation.get("contributions", []), width="stretch")
    st.write(explanation.get("summary", "No explainability summary available."))
    st.caption("Transparent weighted logic only. No fake certainty and no guaranteed profit language.")
    return explanation


def render_timing_explanation(regime_data, risk, catalyst_data, thesis_health, signal_data):
    """Render plain-English timing state for the selected asset."""
    st.header("Timing Explanation")
    timing = generate_timing_explanation(
        regime_data,
        risk,
        catalyst_data,
        thesis_health,
        signal_data,
    )
    st.metric("Timing state", timing.get("timing_label", "wait"))
    st.write(timing.get("reasoning", "No timing explanation available."))
    st.caption("Timing language is research-only and does not predict an exact entry price.")
    return timing


def render_position_sizing_modes(position_size_data, risk):
    """Render conservative, balanced, and aggressive paper sizing recommendations."""
    st.header("Position Sizing by Research Mode")
    rows = generate_position_sizing_modes(position_size_data, risk)
    st.dataframe(rows, width="stretch")
    st.caption("Paper-trading sizing only. No leverage, options, broker APIs, or live orders.")
    return rows


def render_etf_benchmark_dashboard(period, paper_scorecard=None):
    """Render ETF benchmark comparisons for the selected evaluation period."""
    st.header("ETF Benchmark Dashboard")
    benchmark = compare_etf_benchmarks(period=period)
    rows = benchmark.get("benchmarks", [])
    if paper_scorecard:
        rows = [
            {
                "benchmark": "AI paper portfolio",
                "return_pct": paper_scorecard.get("strategy_total_return_pct", 0.0),
                "volatility_pct": paper_scorecard.get("drawdown_pct", 0.0),
                "max_drawdown_pct": paper_scorecard.get("drawdown_pct", 0.0),
                "sharpe": 0.0,
                "diversification": "Strategy-dependent",
            }
        ] + rows
    st.dataframe(rows, width="stretch")
    st.write(benchmark.get("summary", "No benchmark summary available."))
    st.caption("Benchmarks are comparison baselines only. No guaranteed outperformance.")
    return benchmark


def render_execution_readiness(
    signal_data,
    conviction_data,
    opportunity_data,
    alpha_data,
    regime_data,
    news_context,
    catalyst_data,
    risk,
    research_mode,
    confidence_data=None,
):
    """Render paper-trade execution readiness from multi-engine context."""
    readiness = evaluate_execution_readiness(
        signal_data,
        conviction_data,
        opportunity_data,
        alpha_data,
        regime_data,
        news_context,
        catalyst_data,
        risk,
        research_mode=research_mode,
        confidence_data=confidence_data,
    )

    st.header("Execution Readiness Engine")
    col1, col2 = st.columns(2)
    col1.metric("Execution score", readiness.get("execution_score", 0))
    col2.metric("Readiness level", readiness.get("readiness_level", "Not Ready"))

    st.markdown("**Positive checks**")
    for item in readiness.get("positive_checks", []):
        st.success(f"- {item}")
    if not readiness.get("positive_checks"):
        st.write("No strong positive checks currently.")

    st.markdown("**Failed checks**")
    for item in readiness.get("failed_checks", []):
        st.warning(f"- {item}")
    if not readiness.get("failed_checks"):
        st.write("No failed checks currently.")

    st.write(f"Entry quality: {readiness.get('entry_quality', 'Unknown')}")
    st.write(f"Risk note: {readiness.get('risk_note', 'N/A')}")
    st.write(f"Recommended action: {readiness.get('recommended_action', 'Watch')}")
    st.write(readiness.get("summary", "No readiness summary available."))
    st.caption("Paper-trading research only. No live execution, no broker APIs, no guaranteed returns.")
    return readiness


def render_position_sizing_engine(
    execution_data,
    conviction_data,
    risk,
    research_mode,
    portfolio_value=100000,
):
    """Render position sizing guidance for paper-trading research."""
    sizing = calculate_position_size_v1(
        execution_data,
        conviction_data,
        risk,
        portfolio_value=portfolio_value,
        research_mode=research_mode,
    )

    st.header("Position Sizing Engine")
    col1, col2, col3 = st.columns(3)
    col1.metric("Recommended position %", f"{sizing.get('recommended_position_pct', 0.0):.2f}%")
    col2.metric("Recommended value", f"${sizing.get('recommended_position_value', 0.0):,.2f}")
    col3.metric("Risk bucket", sizing.get("risk_bucket", "Low"))

    st.write(f"Max loss tolerance: {sizing.get('max_loss_tolerance_pct', 0.0):.2f}%")

    st.markdown("**Sizing reasoning**")
    for item in sizing.get("sizing_reasoning", []):
        st.info(f"- {item}")
    if not sizing.get("sizing_reasoning"):
        st.write("No sizing reasoning provided.")

    st.markdown("**Caution flags**")
    for item in sizing.get("caution_flags", []):
        st.warning(f"- {item}")
    if not sizing.get("caution_flags"):
        st.write("No caution flags triggered.")

    st.write(sizing.get("summary", "No sizing summary available."))
    st.caption("Paper-trading research only. No live execution, no broker APIs, and no guaranteed returns.")
    return sizing


def render_entry_exit_framework(
    execution_data,
    conviction_data,
    signal_data,
    alpha_data,
    risk,
    research_mode,
):
    """Render a research-only entry/hold/trim/exit framework."""
    plan = generate_entry_exit_plan(
        execution_data,
        conviction_data,
        signal_data,
        alpha_data,
        risk,
        position_data=None,
        research_mode=research_mode,
    )

    st.header("Entry / Exit Framework")
    col1, col2, col3 = st.columns(3)
    col1.metric("Entry zone", plan.get("entry_zone", "Watch Zone"))
    col2.metric("Entry readiness", plan.get("entry_readiness", "Low"))
    col3.metric("Stop-loss guidance", f"{plan.get('stop_loss_guidance_pct', 0):.2f}%")

    st.markdown("**Trim conditions**")
    for item in plan.get("trim_conditions", []):
        st.warning(f"- {item}")

    st.markdown("**Hold conditions**")
    for item in plan.get("hold_conditions", []):
        st.info(f"- {item}")

    st.markdown("**Exit conditions**")
    for item in plan.get("exit_conditions", []):
        st.error(f"- {item}")

    st.write(f"Risk-to-reward view: {plan.get('risk_to_reward_view', 'Balanced')}")
    st.write(f"Recommended action: {plan.get('recommended_action', 'Watch')}")
    st.write(plan.get("summary", "No framework summary available."))
    st.caption("Paper-trading research only. No live execution, no broker APIs, and no guaranteed returns.")
    return plan


def render_meta_decision_engine(
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
    research_mode,
):
    """Render final research-only synthesis verdict."""
    meta = generate_meta_decision(
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
        research_mode=research_mode,
    )

    st.header("Meta Decision Engine")
    col1, col2 = st.columns(2)
    col1.metric("Final verdict", meta.get("final_verdict", "Watch"))
    col2.metric("Decision score", f"{meta.get('decision_score', 0)}/100")
    st.write(f"Recommended next step: {meta.get('recommended_next_step', 'N/A')}")
    st.write(f"Capital priority: {meta.get('capital_priority', 'N/A')}")
    st.write(f"Timing view: {meta.get('timing_view', 'N/A')}")

    st.markdown("**Main reasons**")
    for item in meta.get("main_reasons", []):
        st.success(f"- {item}")

    st.markdown("**Main risks**")
    for item in meta.get("main_risks", []):
        st.warning(f"- {item}")

    st.markdown("**Conditions to change view**")
    for item in meta.get("conditions_to_change_view", []):
        st.info(f"- {item}")

    st.write(f"Human review required: {'Yes' if meta.get('human_review_required', True) else 'No'}")
    st.write(meta.get("summary", "No summary available."))
    st.caption("Research-only synthesis layer for paper-trading workflows. Not financial advice.")
    return meta


def render_scenario_engine(
    symbol,
    risk,
    signal_data,
    news_context,
    regime_data,
    exposure_data=None,
    asset_class=None,
):
    """Render simple research-only scenario analysis."""
    st.header("Scenario Engine")
    scenario_output = run_scenarios(
        symbol,
        risk,
        signal_data,
        news_context,
        regime_data,
        exposure_data=exposure_data,
        asset_class=asset_class,
    )

    rows = scenario_output.get("scenarios", [])
    if rows:
        st.dataframe(rows, width="stretch")
    else:
        st.write("No scenario results available.")

    st.write(scenario_output.get("overall_scenario_summary", "No summary available."))
    st.caption("Scenario analysis is hypothetical and research-only.")


def render_research_brief(
    symbol,
    snapshot,
    risk,
    macro_context,
    sector_context,
    news_context,
    regime_data,
    signal_data,
    opportunity_data,
    exposure_data,
    trade_decision,
    research_memo,
    scenario_results,
    stress_test_results,
    factor_attribution,
):
    """Render a concise research brief from current workflow outputs."""
    brief = generate_research_brief(
        symbol,
        snapshot,
        risk,
        macro_context,
        sector_context,
        news_context,
        regime_data,
        signal_data,
        opportunity_data,
        exposure_data,
        trade_decision,
        research_memo,
        scenario_results,
        stress_test_results,
        factor_attribution,
    )

    st.header("Research Brief Generator")
    st.subheader(brief.get("title", "Research Brief"))
    st.write(brief.get("summary", ""))
    st.markdown("**Market context**")
    st.write(brief.get("market_context", ""))
    st.markdown("**Signal summary**")
    st.write(brief.get("signal_summary", ""))
    st.markdown("**Risk summary**")
    st.write(brief.get("risk_summary", ""))
    st.markdown("**Scenario summary**")
    st.write(brief.get("scenario_summary", ""))
    st.markdown("**Portfolio implication**")
    st.write(brief.get("portfolio_implication", ""))
    st.markdown("**Decision summary**")
    st.write(brief.get("decision_summary", ""))
    st.markdown("**Watch items**")
    for item in brief.get("watch_items", []):
        st.info(f"- {item}")
    st.caption(brief.get("disclaimer", "Research-only."))

    lines = [
        brief.get("title", "Research Brief"),
        "",
        f"Summary: {brief.get('summary', '')}",
        f"Market Context: {brief.get('market_context', '')}",
        f"Signal Summary: {brief.get('signal_summary', '')}",
        f"Risk Summary: {brief.get('risk_summary', '')}",
        f"Scenario Summary: {brief.get('scenario_summary', '')}",
        f"Portfolio Implication: {brief.get('portfolio_implication', '')}",
        f"Decision Summary: {brief.get('decision_summary', '')}",
        "Watch Items:",
    ]
    for item in brief.get("watch_items", []):
        lines.append(f"- {item}")
    lines.extend(["", f"Disclaimer: {brief.get('disclaimer', '')}"])
    brief_text = "\n".join(lines)

    st.download_button(
        "Download brief as .txt",
        data=brief_text,
        file_name=f"{symbol}_research_brief.txt",
        mime="text/plain",
    )


def render_daily_research_report(watchlist, research_mode, period):
    """Render a daily-style watchlist research report."""
    report = generate_daily_report(
        watchlist,
        research_mode=research_mode,
        period=period,
    )

    st.header("Daily Research Report")
    st.write(report.get("market_summary", "No market summary available."))

    st.markdown("**Top opportunities**")
    top_rows = report.get("top_opportunities", [])
    if top_rows:
        st.dataframe(top_rows, width="stretch")
    else:
        st.write("No top opportunities available.")

    st.markdown("**Highest risk assets**")
    risk_rows = report.get("highest_risk_assets", [])
    if risk_rows:
        st.dataframe(risk_rows, width="stretch")
    else:
        st.write("No high-risk assets available.")

    st.markdown("**Notable news**")
    news_rows = report.get("notable_news", [])
    if news_rows:
        for item in news_rows:
            st.info(f"- {item}")
    else:
        st.write("No notable news items available.")

    st.markdown("**Full watchlist table**")
    full_table = report.get("watchlist_table", [])
    if full_table:
        st.dataframe(full_table, width="stretch")
    else:
        st.write("No watchlist rows available.")

    st.markdown("**Recommended focus**")
    for item in report.get("recommended_focus", []):
        st.write(f"- {item}")

    st.caption(report.get("disclaimer", "Research-only."))

    lines = [
        report.get("report_title", "Daily Research Report"),
        "",
        f"Market Summary: {report.get('market_summary', '')}",
        "",
        "Top Opportunities:",
    ]
    for row in top_rows:
        lines.append(
            f"- {row.get('symbol', 'N/A')} | {row.get('signal', 'N/A')} | "
            f"Score {row.get('score', 0)} | Regime {row.get('regime', 'Unknown')}"
        )
    lines.append("")
    lines.append("Highest Risk Assets:")
    for row in risk_rows:
        lines.append(
            f"- {row.get('symbol', 'N/A')} | Vol {row.get('volatility_pct', 0):.2f}% | "
            f"Drawdown {row.get('max_drawdown_pct', 0):.2f}%"
        )
    lines.append("")
    lines.append("Notable News:")
    for item in news_rows:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Recommended Focus:")
    for item in report.get("recommended_focus", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append(f"Disclaimer: {report.get('disclaimer', '')}")
    report_text = "\n".join(lines)

    st.download_button(
        "Download daily report as .txt",
        data=report_text,
        file_name="daily_research_report.txt",
        mime="text/plain",
    )


def render_thesis_tracker(
    symbol,
    snapshot,
    signal_data,
    regime_data,
    news_context,
):
    """Render a multi-asset thesis tracker and health check for the selected symbol."""
    st.header("Multi-Asset Thesis Tracker")
    entries = load_theses()
    current_entry = next((row for row in entries if row.get("symbol") == symbol), None)

    health = evaluate_thesis_health(
        symbol,
        snapshot.get("price") if isinstance(snapshot, dict) else None,
        signal_data,
        regime_data,
        news_context,
    )

    if current_entry:
        st.markdown("**Current thesis**")
        st.write(f"- Thesis: {current_entry.get('thesis', '')}")
        st.write(f"- Confidence: {current_entry.get('confidence', 'N/A')}")
        st.write(f"- Stance: {current_entry.get('stance', 'N/A')}")
        st.write(f"- Last note: {current_entry.get('last_note', '') or 'None'}")
    else:
        st.write("No thesis saved yet for this symbol.")

    st.markdown("**Thesis health**")
    col1, col2 = st.columns(2)
    col1.metric("Status", health.get("thesis_status", "Stable"))
    col2.metric("Confidence change", health.get("confidence_change", 0))
    st.write(f"Suggested action: {health.get('suggested_action', 'Review')}")
    for line in health.get("reasoning", []):
        st.info(f"- {line}")

    default_thesis = current_entry.get("thesis", "") if current_entry else ""
    default_conf = int(current_entry.get("confidence", "5")) if current_entry else 5
    default_stance = current_entry.get("stance", "Watch") if current_entry else "Watch"
    default_note = current_entry.get("last_note", "") if current_entry else ""

    with st.form("thesis_tracker_form"):
        thesis_text = st.text_area("Thesis", value=default_thesis, height=120)
        confidence = st.slider("Confidence", min_value=1, max_value=10, value=max(1, min(10, default_conf)))
        stance = st.selectbox(
            "Stance",
            ["Watch", "Constructive", "Cautious", "Defensive"],
            index=["Watch", "Constructive", "Cautious", "Defensive"].index(default_stance)
            if default_stance in {"Watch", "Constructive", "Cautious", "Defensive"}
            else 0,
        )
        note = st.text_input("Note", value=default_note)
        save = st.form_submit_button("Save / Update Thesis")
        if save:
            adjusted_conf = max(1, min(10, confidence + int(health.get("confidence_change", 0))))
            saved = save_or_update_thesis(
                symbol=symbol,
                thesis=thesis_text,
                confidence=adjusted_conf,
                stance=stance,
                thesis_status=health.get("thesis_status", "Stable"),
                last_price=snapshot.get("price") if isinstance(snapshot, dict) else "",
                last_signal=signal_data.get("signal", "Unknown"),
                last_regime=regime_data.get("regime", "Unknown"),
                last_news_sentiment=news_context.get("market_sentiment", "Neutral"),
                last_note=note,
            )
            st.success("Thesis saved.")
            st.write(saved)

    st.markdown("**Recent tracked theses**")
    recent = list(reversed(entries))[:8]
    if recent:
        st.dataframe(recent, width="stretch")
    else:
        st.write("No tracked theses yet.")


def render_conviction_engine(
    signal_data,
    opportunity_data,
    thesis_health,
    regime_data,
    news_context,
    factor_attribution,
    confidence_data,
    research_mode,
):
    """Render unified conviction scoring from existing research context."""
    conviction = calculate_conviction_score(
        signal_data,
        opportunity_data,
        thesis_health,
        regime_data,
        news_context,
        factor_attribution,
        confidence_data,
        research_mode=research_mode,
    )

    st.header("Conviction Scoring Engine")
    col1, col2, col3 = st.columns(3)
    col1.metric("Conviction score", conviction.get("conviction_score", 0))
    col2.metric("Conviction level", conviction.get("conviction_level", "Low"))
    col3.metric("Research priority", conviction.get("research_priority", "Low"))

    st.markdown("**Positive drivers**")
    positives = conviction.get("positive_drivers", [])
    if positives:
        for driver in positives:
            st.success(f"- {driver}")
    else:
        st.write("No strong positive drivers identified.")

    st.markdown("**Negative drivers**")
    negatives = conviction.get("negative_drivers", [])
    if negatives:
        for driver in negatives:
            st.warning(f"- {driver}")
    else:
        st.write("No major negative drivers identified.")

    st.write(conviction.get("summary", "No conviction summary available."))
    st.caption(
        "Research-only conviction scoring. No broker APIs, no live trading, no auto execution, and no guaranteed returns."
    )


def render_catalyst_tracker(symbol, news_context, thesis_health, conviction_data):
    """Render catalyst tracking for conviction and thesis changes."""
    tracker = generate_catalyst_tracker(
        symbol,
        news_context,
        thesis_health,
        conviction_data,
    )

    st.header("Catalyst Tracker")
    catalysts = tracker.get("catalysts", [])
    if catalysts:
        st.dataframe(catalysts, width="stretch")
    else:
        st.write("No catalysts available.")

    highest = tracker.get("highest_priority_catalyst", {})
    if highest:
        st.write(
            f"**Highest priority catalyst:** {highest.get('catalyst', 'N/A')} "
            f"({highest.get('type', 'N/A')} | {highest.get('urgency', 'N/A')})"
        )
    st.write(f"**Conviction risk:** {tracker.get('conviction_risk', 'Low')}")
    st.write(tracker.get("summary", "No catalyst summary available."))
    st.caption(
        "Research-only catalyst tracking. No broker APIs, no live trading, no auto execution, and no guaranteed outcomes."
    )


def render_alternative_data_context(symbol):
    """Render delayed/noisy alternative data as supporting research evidence."""
    context = generate_alternative_data_context(symbol)

    st.header("Alternative Data Intelligence")
    col1, col2 = st.columns(2)
    col1.metric("Alternative data score", f"{context.get('alternative_data_score', 0)}/100")
    col2.metric("Politician trade signal", context.get("politician_trade_signal", "N/A"))

    st.write(
        f"**Insider activity signal:** {context.get('insider_activity_signal', 'N/A')}"
    )
    st.write(
        "**Institutional attention signal:** "
        f"{context.get('institutional_attention_signal', 'N/A')}"
    )

    st.markdown("**Positive signals**")
    positives = context.get("positive_signals", [])
    if positives:
        for item in positives:
            st.success(f"- {item}")
    else:
        st.write("No positive alternative-data signals available.")

    st.markdown("**Risk flags**")
    flags = context.get("risk_flags", [])
    if flags:
        for item in flags:
            st.warning(f"- {item}")
    else:
        st.write("No alternative-data risk flags in the placeholder layer.")

    st.markdown("**Data limitations**")
    for item in context.get("data_limitations", []):
        st.info(f"- {item}")

    with st.expander("Future optional data sources", expanded=False):
        for name, description in context.get("future_data_sources", {}).items():
            st.write(f"- {name}: {description}")

    st.write(context.get("summary", "No alternative data summary available."))
    st.caption(
        "Research-only alternative data context. Supporting evidence only; no live trading, broker APIs, auto execution, or guaranteed profit claims."
    )
    return context


def render_fundamental_catalyst_quality(symbol, catalyst_data=None):
    """Render lightweight fundamental and catalyst quality context."""
    context = generate_fundamental_catalyst_context(symbol, catalyst_data=catalyst_data)
    st.header("Fundamental & Catalyst Quality")

    col1, col2, col3 = st.columns(3)
    col1.metric("Fundamental quality", context.get("fundamental_quality", "Neutral"))
    col2.metric("Fundamental score", f"{context.get('fundamental_score', 0)}/100")
    col3.metric("Earnings date", context.get("earnings_date", "Unknown"))

    st.write(f"Recent filing status: {context.get('recent_filing_status', 'Not connected')}")

    st.markdown("**Positive factors**")
    positives = context.get("positive_factors", [])
    if positives:
        for item in positives:
            st.success(f"- {item}")
    else:
        st.write("No verified positive fundamental factors yet.")

    st.markdown("**Risk flags**")
    flags = context.get("risk_flags", [])
    if flags:
        for item in flags:
            st.warning(f"- {item}")
    else:
        st.write("No major fundamental/catalyst risk flags.")

    st.markdown("**Data limitations**")
    for item in context.get("data_limitations", []):
        st.info(f"- {item}")

    st.write(context.get("summary", "No fundamental/catalyst summary available."))
    st.caption("Fundamental and catalyst context is supporting evidence only. No guaranteed returns.")
    return context


def render_factor_attribution(
    screened_assets,
    portfolio_allocations,
    research_mode,
):
    """Render a simple factor attribution summary for research context."""
    st.header("Factor Attribution Engine")
    attribution = analyze_factor_attribution(
        screened_assets,
        portfolio_allocations=portfolio_allocations,
        research_mode=research_mode,
    )

    positive = attribution.get("positive_factors", [])
    negative = attribution.get("negative_factors", [])
    dominant = attribution.get("dominant_factor", {})
    risk_driver = attribution.get("risk_driver", {})

    st.markdown("**Positive factors**")
    if positive:
        st.dataframe(positive, width="stretch")
    else:
        st.write("No strong positive factor cluster detected.")

    st.markdown("**Negative factors**")
    if negative:
        st.dataframe(negative, width="stretch")
    else:
        st.write("No major negative factor cluster detected.")

    col1, col2 = st.columns(2)
    col1.metric("Dominant factor", dominant.get("factor", "N/A"))
    col2.metric("Main risk driver", risk_driver.get("factor", "N/A"))

    st.write(attribution.get("summary", "No attribution summary available."))
    st.caption(
        "Research-only factor attribution. This is rule-based context, not guaranteed performance."
    )


def render_portfolio_simulator(watchlist):
    """Render a simple research-only portfolio simulator."""
    st.header("Portfolio Simulator")

    selected_assets = st.multiselect(
        "Select assets",
        watchlist,
        default=watchlist[:2] if len(watchlist) >= 2 else watchlist,
    )

    if not selected_assets:
        st.info("Select at least one asset to simulate.")
        return {}

    allocation_inputs = {}
    for asset in selected_assets:
        allocation_inputs[asset] = st.number_input(
            f"{asset} allocation (%)",
            min_value=0.0,
            max_value=100.0,
            value=round(100 / len(selected_assets), 2),
            step=1.0,
            key=f"portfolio_alloc_{asset}",
        )

    total_allocation = sum(allocation_inputs.values())
    if total_allocation <= 0:
        normalized_allocations = {asset: 100 / len(selected_assets) for asset in selected_assets}
    else:
        normalized_allocations = {
            asset: (allocation_inputs[asset] / total_allocation) * 100
            for asset in selected_assets
        }

    if abs(total_allocation - 100) > 1e-9:
        st.caption("Allocations were normalized to sum to 100% for the simulation.")

    results = simulate_portfolio(selected_assets, normalized_allocations, period="6mo")
    portfolio_curve = results.get("portfolio_equity_curve")

    if portfolio_curve is None or portfolio_curve.empty:
        st.write("Not enough data to simulate this portfolio.")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Total return", f"{results.get('total_return_pct', 0.0):+.2f}%")
    col2.metric("Best asset", results.get("best_asset", "N/A"))
    col3.metric("Worst asset", results.get("worst_asset", "N/A"))

    st.line_chart(portfolio_curve.set_index("Date"))
    st.caption(
        "Research-only simulator: this is not a recommendation and does not place trades."
    )
    return normalized_allocations


def render_paper_trading_simulator(watchlist):
    """Render a simple paper-trading simulator."""
    st.header("Paper Trading Simulator")
    st.caption("Paper trading is simulation only. This does not execute real trades.")

    symbol = st.selectbox("Symbol", watchlist)
    action = st.selectbox("Action", ["Buy", "Sell"])
    quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
    reason = st.text_input("Reason", value="Research signal")

    current_price = 0.0
    try:
        from market_data import get_market_snapshot

        current_price = float(get_market_snapshot(symbol).get("price", 0.0) or 0.0)
    except Exception:
        current_price = 0.0

    if st.button("Save simulated trade"):
        add_paper_trade(symbol, action.lower(), quantity, current_price, reason)
        st.success("Paper trade saved.")

    current_prices = {}
    for asset in watchlist:
        try:
            current_prices[asset] = float(get_market_snapshot(asset).get("price", 0.0) or 0.0)
        except Exception:
            current_prices[asset] = 0.0

    positions = calculate_paper_positions(current_prices)
    performance = calculate_paper_performance(current_prices)
    paper_positions = positions.get("positions", {})
    trades = load_paper_trades()

    st.subheader("Performance summary")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total market value", f"${performance.get('total_market_value', 0.0):,.2f}")
    col2.metric("Total unrealized P&L", f"${performance.get('total_unrealized_pnl', 0.0):,.2f}")
    col3.metric("Total unrealized P&L %", f"{performance.get('total_unrealized_pnl_pct', 0.0):+.2f}%")
    col4.metric("Best position", performance.get("best_position", "N/A"))
    col5.metric("Worst position", performance.get("worst_position", "N/A"))
    col6.metric("Number of trades", performance.get("number_of_trades", 0))

    if performance.get("win_rate") is not None:
        st.caption(f"Win rate (simple current-price check): {performance.get('win_rate', 0.0):.2f}%")

    st.subheader("Open positions")
    col7, col8, col9 = st.columns(3)
    col7.metric("Open shares", positions.get("total_shares", 0))
    col8.metric("Market value", f"${positions.get('market_value', 0.0):,.2f}")
    col9.metric("Unrealized P&L", f"${positions.get('unrealized_pnl', 0.0):,.2f}")

    if paper_positions:
        st.dataframe(
            [
                {
                    "Symbol": symbol,
                    "Shares": info["shares"],
                    "Avg cost": info["average_cost"],
                    "Current price": info["current_price"],
                    "Market value": info["market_value"],
                    "Unrealized P&L": info["unrealized_pnl"],
                    "Unrealized P&L %": info["unrealized_pnl_pct"],
                }
                for symbol, info in paper_positions.items()
            ],
            width="stretch",
        )
    else:
        st.write("No open paper positions yet.")

    st.subheader("Trade review")
    st.write("**What worked:**")
    st.info("Use the strongest positions and keep notes on why they worked.")
    st.write("**What did not work:**")
    st.warning("Use this space to note weak entries, poor timing, or low-quality signals.")
    st.write("**Lesson learned:**")
    st.success("Paper trading should improve your research process, not replace it.")

    st.subheader("Trade history")
    if trades:
        st.dataframe(trades, width="stretch")
    else:
        st.write("No paper trades saved yet.")


def render_stress_test_engine(paper_positions):
    """Render research-only paper portfolio stress tests."""
    st.header("Stress Test Engine")
    stress_output = run_stress_tests(paper_positions)
    rows = stress_output.get("stress_tests", [])

    if rows:
        st.dataframe(rows, width="stretch")
    else:
        st.write(stress_output.get("summary", "No stress test results available."))
        st.caption("Research-only paper stress testing. No live trading or broker APIs.")
        return

    st.write(stress_output.get("summary", "No summary available."))
    st.caption(
        "Research-only paper portfolio stress test. Hypothetical scenarios only, with no guaranteed performance."
    )


def render_trade_decision_assistant(selected_asset, snapshot, risk, news_context, backtest_results, paper_positions):
    """Render a research-only paper-trading decision summary."""
    signal_data = generate_signal(selected_asset, snapshot, risk, news_context=news_context)
    decision = generate_trade_decision(
        selected_asset,
        snapshot,
        risk,
        signal_data,
        news_context,
        backtest_results,
        paper_positions,
    )

    st.header("Trade Decision Assistant")
    st.caption("This is paper-trading research only.")

    col1, col2 = st.columns(2)
    col1.metric("Suggested action", decision.get("suggested_action", "Watch"))
    col2.metric("Confidence", f"{decision.get('confidence', 1)}/10")

    st.markdown("**Reasons**")
    for reason in decision.get("reasons", []):
        st.info(f"- {reason}")

    st.markdown("**Risks**")
    for risk_item in decision.get("risks", []):
        st.warning(f"- {risk_item}")

    st.write(f"**Approval required:** {decision.get('approval_required', True)}")
    st.caption("This assistant does not auto-execute or place trades.")
    return decision


def render_confidence_engine(
    signal_data,
    evaluation_summary,
    regime_data,
    adaptive_learning,
    research_mode="Balanced",
    analysis_depth="Standard",
):
    """Render confidence calibration for the current research signal."""
    confidence = calculate_confidence_adjustment(
        signal_data,
        evaluation_summary,
        regime_data,
        adaptive_learning,
        research_mode=research_mode,
        analysis_depth=analysis_depth,
    )

    st.header("Confidence Calibration")
    st.caption("Research-only trust calibration. This never guarantees future outcomes.")

    col1, col2 = st.columns(2)
    col1.metric("Trust level", confidence["trust_level"])
    col2.metric("Adjusted confidence", f"{confidence['adjusted_confidence']}/10")

    st.markdown("**Reasoning**")
    for reason in confidence["confidence_reasoning"]:
        st.info(f"- {reason}")

    st.warning(
        "Caution: confidence calibration is descriptive only. It does not execute trades, connect to brokers, or remove the need for human review."
    )


def render_save_research_run(
    selected_asset,
    snapshot,
    risk,
    price_data,
    news_context,
    notes,
    current_symbol_exposure,
    total_portfolio_value,
    decision=None,
):
    """Render a button to save the current research run and show recent runs."""
    signal_data = generate_signal(selected_asset, snapshot, risk, news_context=news_context)
    if decision is None:
        decision = generate_trade_decision(
            selected_asset,
            snapshot,
            risk,
            signal_data,
            news_context,
            {},
            {"positions": {}},
        )

    summary = generate_research_summary(selected_asset, snapshot, risk, notes=notes)
    regime = detect_market_regime(price_data, risk)

    exposure_pct = 0.0
    if total_portfolio_value > 0:
        exposure_pct = (current_symbol_exposure / total_portfolio_value) * 100

    if exposure_pct >= 30:
        exposure_level = "High"
    elif exposure_pct >= 15:
        exposure_level = "Medium"
    elif exposure_pct > 0:
        exposure_level = "Low"
    else:
        exposure_level = "None"

    research_summary = (
        f"{summary['overall_stance']} | {summary['bull_case']} | "
        f"{summary['bear_case']} | {summary['risk_summary']}"
    )

    st.header("Save Research Run")
    st.caption("Research-only snapshot. This does not place trades or connect to a broker.")

    if st.button("Save Research Run"):
        save_research_run(
            symbol=selected_asset,
            price=snapshot.get("price", 0.0),
            return_pct=risk.get("return_pct", 0.0),
            volatility_pct=risk.get("volatility_pct", 0.0),
            max_drawdown_pct=risk.get("max_drawdown_pct", 0.0),
            regime=regime.get("regime", "Unknown"),
            signal=signal_data.get("signal", "Unknown"),
            signal_score=signal_data.get("score", 0),
            exposure_level=exposure_level,
            trade_decision=decision.get("suggested_action", "Watch"),
            research_summary=research_summary,
        )
        st.success("Research run saved.")

    with st.expander("View Recent Research Runs", expanded=False):
        runs = load_research_runs()
        recent_runs = sorted(runs, key=lambda row: row.get("date", ""), reverse=True)[:5]

        if not recent_runs:
            st.write("No research runs saved yet.")
            return

        for run in recent_runs:
            st.markdown(f"**{run.get('symbol', 'Unknown')} — {run.get('date', '')}**")
            st.write(f"Signal: {run.get('signal', 'Unknown')} ({run.get('signal_score', 0)})")
            st.write(f"Regime: {run.get('regime', 'Unknown')} | Exposure: {run.get('exposure_level', 'Unknown')}")
            st.write(f"Decision: {run.get('trade_decision', 'Watch')}")
            st.write(run.get("research_summary", ""))
            st.caption("Research-only snapshot. No live orders or broker APIs used.")


def render_research_run_evaluation(symbol, current_price):
    """Render a simple evaluation summary for saved research runs."""
    st.header("Research Run Evaluation")
    st.caption("Research-only comparison of saved research runs versus the current price. This does not guarantee future outcomes.")

    evaluation = evaluate_research_runs(symbol, current_price)

    if evaluation["total_runs"] == 0:
        st.write("No saved research runs found for this symbol yet.")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Saved runs", evaluation["total_runs"])
    col2.metric("Average realized return", f"{evaluation['average_realized_return']:+.2f}%")
    col3.metric("Best run return", f"{evaluation['best_run']['realized_return_pct']:+.2f}%")

    st.markdown("**Best run**")
    st.write(f"- Date: {evaluation['best_run']['date']}")
    st.write(f"- Return: {evaluation['best_run']['realized_return_pct']:+.2f}%")
    st.write(f"- Outcome: {evaluation['best_run']['outcome']}")

    st.markdown("**Worst run**")
    st.write(f"- Date: {evaluation['worst_run']['date']}")
    st.write(f"- Return: {evaluation['worst_run']['realized_return_pct']:+.2f}%")
    st.write(f"- Outcome: {evaluation['worst_run']['outcome']}")

    st.markdown("**Recent evaluated runs**")
    for run in evaluation["recent_evaluated_runs"]:
        st.info(
            f"{run['date']} | {run['signal']} | {run['realized_return_pct']:+.2f}% | {run['outcome']}"
        )


def render_adaptive_learning():
    """Render simple adaptive learning insights from saved predictions and research runs."""
    st.header("Adaptive Learning Engine")
    st.caption("Research-only adaptive notes. This does not auto-execute trades or claim future performance.")

    predictions = load_predictions()
    research_runs = load_research_runs()
    insights = calculate_factor_insights(predictions, research_runs)

    col1, col2 = st.columns(2)
    col1.metric("Learning confidence", insights["learning_confidence"], delta="Rule-based")
    col2.metric("Sample size", insights.get("sample_size", 0))

    st.markdown("**Positive factors**")
    for factor in insights["strong_positive_factors"]:
        st.success(f"- {factor}")

    st.markdown("**Weak negative factors**")
    for factor in insights["weak_negative_factors"]:
        st.warning(f"- {factor}")

    st.markdown("**Suggested weight adjustments**")
    adjustment_rows = insights.get("reviewable_adjustments", [])
    if adjustment_rows:
        st.dataframe(adjustment_rows, width="stretch")
    else:
        for factor, adjustment in insights["suggested_weight_adjustments"].items():
            st.write(f"- {factor}: {adjustment:.2f}x")

    st.markdown("**Summary**")
    st.write(insights["summary"])
    st.caption(insights.get("disclaimer", "Research-only adaptive learning."))


def render_risk_engine(
    selected_asset,
    snapshot,
    risk,
    confidence=5,
    total_portfolio_value=1000.0,
    current_symbol_exposure=0.0,
    asset_class=None,
):
    """Render a simple risk-based position sizing summary."""
    current_price = float(snapshot.get("price", 0.0) or 0.0)
    sizing = calculate_position_size(
        total_portfolio_value=total_portfolio_value,
        current_price=current_price,
        confidence=confidence,
        volatility_pct=risk.get("volatility_pct", 0.0),
        current_symbol_exposure=current_symbol_exposure,
        symbol=selected_asset,
        asset_class=asset_class,
    )

    st.header("Risk Engine")
    st.caption("Research-only position sizing based on confidence, volatility, and current exposure.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Recommended value", f"${sizing['recommended_position_value']:,.2f}")
    col2.metric("Recommended shares", sizing["recommended_shares"])
    col3.metric("Portfolio risk %", f"{sizing['portfolio_risk_pct'] * 100:.2f}%")

    st.warning(sizing["risk_warning"])

    st.markdown("**Sizing reasoning**")
    for point in sizing.get("sizing_reasoning", sizing.get("reasoning", [])):
        st.info(f"- {point}")


def render_exposure_engine(exposure_data):
    """Render a simple research-only exposure summary."""
    st.header("Exposure Engine")
    st.caption("Research-only exposure summary. No live trading or broker APIs.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Exposure level", exposure_data.get("exposure_level", "Unknown"))
    col2.metric("Exposure %", f"{exposure_data.get('exposure_pct', 0.0):.2f}%")
    col3.metric(
        "Current exposure value",
        f"${exposure_data.get('current_symbol_exposure', 0.0):,.2f}",
    )

    st.write(
        f"Total portfolio value used for sizing context: ${exposure_data.get('total_portfolio_value', 0.0):,.2f}"
    )


def render_research_notes(selected_asset, notes):
    """Render the research notes section."""
    st.header("Research Notes")
    if notes:
        st.write("**Current notes:**")
        st.write(notes)


def render_research_agent(selected_asset, snapshot, risk, notes=""):
    """Render the research agent summary section."""
    summary = generate_research_summary(selected_asset, snapshot, risk, notes=notes)
    with st.expander("Research Agent", expanded=True):
        st.subheader("Rule-based decision-support summary")

        st.markdown("**Bull case**")
        st.success(summary["bull_case"])

        st.markdown("**Bear case**")
        st.warning(summary["bear_case"])

        st.markdown("**Risk summary**")
        st.metric("Risk summary", summary["risk_summary"])

        st.markdown("**Learning questions**")
        for question in summary["learning_questions"]:
            st.write(f"- {question}")

        st.markdown("**Overall research stance**")
        st.markdown(f"### {summary['overall_stance']}")


def _display_agent_list(value):
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            return [value] if value else []
    return value or []


def _save_agent_result_to_recommendation_log(result):
    agent_names = [row.get("agent_name", "") for row in result.get("agent_evidence", [])]
    return save_recommendation_log(
        symbol=result.get("symbol"),
        action=result.get("final_verdict"),
        horizon=result.get("lane"),
        score=result.get("score"),
        price=result.get("price"),
        engine_inputs={
            "source": "Agent Research Desk",
            "lane": result.get("lane"),
            "data_confidence": result.get("data_quality", {}).get("data_confidence", "Unknown"),
            "agent_names": agent_names,
            "memory_delta": result.get("memory_delta", ""),
        },
        data_gate=result.get("data_quality", {}).get("recommendation_gate", ""),
        suitability_status="Human review required",
        sector=map_asset_to_sector(result.get("symbol")),
        market_regime=result.get("market_regime", ""),
        benchmark_symbol="SPY",
    )


def render_agent_research_desk(
    selected_asset,
    screened_assets,
    financial_profile=None,
    current_prices=None,
    key_suffix="agent_research_desk",
):
    """Render the hybrid agent research desk with memory and evaluation."""
    st.header("Agent Research Desk")
    st.caption(
        "Hybrid research agents: daily queue plus on-demand ticker research. "
        "Research-only; no broker APIs, live trading, margin, leverage, direct futures contracts, or guaranteed profit."
    )

    financial_profile = financial_profile or {}
    current_prices = current_prices or {}
    if f"{key_suffix}_queue" not in st.session_state:
        st.session_state[f"{key_suffix}_queue"] = []
    if f"{key_suffix}_result" not in st.session_state:
        st.session_state[f"{key_suffix}_result"] = None

    col1, col2, col3 = st.columns(3)
    if col1.button("Generate Next Research Queue", key=f"generate_queue_{key_suffix}"):
        queue_result = generate_daily_agent_queue(screened_assets, limit=12)
        st.session_state[f"{key_suffix}_queue"] = queue_result.get("queue", [])
        st.success(queue_result.get("summary", "Generated research queue."))

    ticker = col2.text_input(
        "Ticker",
        value=selected_asset or "",
        key=f"agent_research_ticker_{key_suffix}",
    ).upper().strip()
    run_type = col3.selectbox(
        "Run type",
        ["On Demand", "Daily Queue"],
        key=f"agent_run_type_{key_suffix}",
    )

    queue_rows = st.session_state.get(f"{key_suffix}_queue", [])
    st.subheader("Daily Agent Queue")
    if queue_rows:
        st.dataframe(queue_rows, width="stretch")
        options = [f"{row.get('symbol')} | {row.get('lane')} | score {row.get('score')}" for row in queue_rows]
        selected_queue = st.selectbox("Queue candidate", options, key=f"queue_pick_{key_suffix}")
        selected_symbol = selected_queue.split(" | ")[0]
        if st.button("Run Selected Queue Candidate", key=f"run_queue_candidate_{key_suffix}"):
            st.session_state[f"{key_suffix}_result"] = run_agent_research_desk(
                selected_symbol,
                run_type="Daily Queue",
                profile=financial_profile,
                save_memory=False,
            )
    else:
        st.write("No queue generated yet.")

    if st.button("Run Agent Research", key=f"run_agent_research_{key_suffix}"):
        st.session_state[f"{key_suffix}_result"] = run_agent_research_desk(
            ticker,
            run_type=run_type,
            profile=financial_profile,
            save_memory=False,
        )

    result = st.session_state.get(f"{key_suffix}_result")
    if result:
        st.subheader("Judge Verdict")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Verdict", result.get("final_verdict", "Watch"))
        c2.metric("Lane", result.get("lane", "Needs Data"))
        c3.metric("Score", f"{result.get('score', 0):.1f}")
        c4.metric("Data", result.get("data_quality", {}).get("data_confidence", "Unknown"))
        st.write(result.get("summary", "No agent summary available."))
        st.info(result.get("memory_delta", "No memory comparison available."))

        if result.get("lane_scores"):
            st.markdown("**Lane scores**")
            st.dataframe(
                [{"lane": lane, "score": score} for lane, score in result.get("lane_scores", {}).items()],
                width="stretch",
            )

        st.markdown("**Agent vote table**")
        evidence_table = []
        for row in result.get("agent_evidence", []):
            evidence_table.append(
                {
                    "agent": row.get("agent_name"),
                    "status": row.get("status"),
                    "score": row.get("score"),
                    "key_points": " | ".join(_display_agent_list(row.get("key_points"))[:2]),
                    "concerns": " | ".join(_display_agent_list(row.get("concerns"))[:2]),
                    "recommendation": row.get("recommendation"),
                }
            )
        st.dataframe(evidence_table, width="stretch")

        c_bull, c_bear = st.columns(2)
        with c_bull:
            st.markdown("**Bull case**")
            for item in result.get("bull_case", []) or ["No bull case saved."]:
                st.write(f"- {item}")
        with c_bear:
            st.markdown("**Bear case**")
            for item in result.get("bear_case", []) or ["No bear case saved."]:
                st.write(f"- {item}")

        st.markdown("**Invalidation triggers**")
        for item in result.get("invalidation_triggers", []):
            st.write(f"- {item}")

        if st.button("Save Verdict To Memory", key=f"save_agent_memory_{key_suffix}"):
            run_row = save_agent_run(
                symbol=result.get("symbol"),
                run_type=result.get("run_type", "On Demand"),
                lane=result.get("lane"),
                data_confidence=result.get("data_quality", {}).get("data_confidence", "Unknown"),
                final_verdict=result.get("final_verdict"),
                confidence=result.get("confidence"),
                score=result.get("score"),
                summary=result.get("summary"),
                thesis_snapshot=result.get("thesis_snapshot", ""),
                memory_delta=result.get("memory_delta", ""),
                human_review_required=True,
            )
            result["run_id"] = run_row.get("id")
            for evidence_row in result.get("agent_evidence", []):
                save_agent_evidence(run_id=result["run_id"], **evidence_row)
            save_ticker_memory(
                symbol=result.get("symbol"),
                thesis=result.get("thesis_snapshot", result.get("summary", "")),
                bull_case=" | ".join(result.get("bull_case", [])[:4]),
                bear_case=" | ".join(result.get("bear_case", [])[:4]),
                last_verdict=result.get("final_verdict"),
                last_lane=result.get("lane"),
                lessons=(result.get("memory") or {}).get("lessons", ""),
            )
            _save_agent_result_to_recommendation_log(result)
            st.session_state[f"{key_suffix}_result"] = result
            st.success("Saved structured agent memory, narrative ticker memory, evidence, and recommendation log entry.")

    st.subheader("Prior Memory")
    memory_symbol = ticker or selected_asset
    prior_memory = load_ticker_memory(memory_symbol)
    prior_runs = load_agent_runs(symbol=memory_symbol, limit=10)
    if prior_memory:
        st.write(prior_memory.get("thesis", "No thesis memory available."))
        st.caption(
            f"Last verdict: {prior_memory.get('last_verdict', 'Unknown')} | "
            f"Last lane: {prior_memory.get('last_lane', 'Unknown')} | "
            f"Updated: {prior_memory.get('updated_at', '')}"
        )
    else:
        st.write("No narrative memory saved for this ticker yet.")
    if prior_runs:
        st.dataframe(prior_runs, width="stretch")

    st.subheader("Update Outcome")
    logs = load_recommendation_log(symbol=memory_symbol)
    if logs:
        options = [
            f"{row.get('id')} | {row.get('symbol')} | {row.get('action')} | {row.get('horizon')}"
            for row in logs
        ]
        selected = st.selectbox("Agent-linked recommendation", options, key=f"agent_outcome_pick_{key_suffix}")
        log_id = int(selected.split(" | ")[0])
        outcome_price = st.number_input("Outcome price", min_value=0.0, value=0.0, step=1.0, key=f"agent_outcome_price_{key_suffix}")
        realized_return = st.number_input("Realized return %", value=0.0, step=0.5, key=f"agent_realized_{key_suffix}")
        drawdown = st.number_input("Max drawdown after signal %", value=0.0, step=0.5, key=f"agent_drawdown_{key_suffix}")
        alpha = st.number_input("Alpha vs benchmark %", value=0.0, step=0.5, key=f"agent_alpha_{key_suffix}")
        label = st.selectbox("Outcome label", ["", "Win", "Loss", "Flat", "Good", "Poor"], key=f"agent_label_{key_suffix}")
        lesson = st.text_input("Lesson", value="", key=f"agent_lesson_{key_suffix}")
        if st.button("Update Outcome", key=f"agent_update_outcome_{key_suffix}"):
            update_recommendation_outcome(
                log_id,
                outcome_price=outcome_price,
                realized_return_pct=realized_return,
                max_drawdown_after_signal=drawdown,
                alpha_vs_benchmark_pct=alpha,
                outcome_label=label,
                lesson=lesson,
            )
            st.success("Outcome updated for evaluation memory.")
    else:
        st.write("No saved recommendation log rows for this ticker yet.")

    st.subheader("Agent Evaluation")
    evaluation = evaluate_agent_research_memory(
        agent_runs=load_agent_runs(limit=250),
        evidence_rows=load_agent_evidence(limit=1000),
        recommendation_log=load_recommendation_log(),
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Agent runs", evaluation.get("total_agent_runs", 0))
    c2.metric("Evidence rows", evaluation.get("total_agent_evidence", 0))
    c3.metric("Evaluated", evaluation.get("evaluated_recommendations", 0))
    st.write(evaluation.get("summary", "No evaluation summary available."))
    if evaluation.get("lane_stats"):
        st.markdown("**By lane**")
        st.dataframe(evaluation.get("lane_stats"), width="stretch")
    if evaluation.get("verdict_stats"):
        st.markdown("**By verdict**")
        st.dataframe(evaluation.get("verdict_stats"), width="stretch")
    if evaluation.get("agent_activity"):
        st.markdown("**Agent activity**")
        st.dataframe(evaluation.get("agent_activity"), width="stretch")

    return {
        "queue": queue_rows,
        "latest_result": result,
        "evaluation": evaluation,
    }


def render_agent_task_runner(
    symbol,
    snapshot,
    price_data,
    risk,
    news_context,
    signal_data,
    regime_data,
    exposure_data,
    backtest_results,
    strategy_lab_results,
    trade_decision,
    research_memo,
    research_mode="Balanced",
    analysis_depth="Standard",
):
    """Render a structured research-only agent workflow report."""
    report = run_research_workflow(
        symbol,
        snapshot,
        price_data,
        risk,
        news_context,
        signal_data,
        regime_data,
        exposure_data,
        backtest_results,
        strategy_lab_results,
        trade_decision,
        research_memo,
        research_mode=research_mode,
        analysis_depth=analysis_depth,
    )

    st.header("Agent Task Runner")
    st.caption("Research-only workflow report. No broker APIs, live trading, or auto execution.")

    col1, col2 = st.columns(2)
    col1.metric("Workflow status", report["workflow_status"])
    col2.metric("Human review required", "Yes" if report["needs_human_review"] else "No")

    st.markdown("**Steps completed**")
    for step in report["steps_completed"]:
        st.write(f"- {step}")

    st.markdown("**Key findings**")
    for finding in report["key_findings"]:
        st.info(f"- {finding}")

    st.markdown("**Concerns**")
    for concern in report["concerns"]:
        st.warning(f"- {concern}")

    st.markdown("**Recommended next actions**")
    for action in report["recommended_next_actions"]:
        st.write(f"- {action}")


def render_signal_engine(selected_asset, snapshot, risk, price_data=None):
    """Render the signal engine section and allow saving predictions."""
    news_context = generate_news_context(selected_asset)
    alternative_data_context = generate_alternative_data_context(selected_asset)
    adaptive_context = calculate_factor_insights(load_predictions(), load_research_runs())
    signal_data = generate_signal(
        selected_asset,
        snapshot,
        risk,
        news_context=news_context,
        adaptive_context=adaptive_context,
        alternative_data_context=alternative_data_context,
    )
    backtest_return = None
    if price_data is not None:
        try:
            backtest_results = run_simple_backtest(price_data)
            backtest_return = backtest_results.get("strategy_return_pct")
        except Exception:
            backtest_return = None

    with st.expander("Signal Engine", expanded=True):
        st.subheader("Research-only composite signal")
        st.write(f"**Signal:** {signal_data['signal']}")
        st.write(f"**Final score:** {signal_data['score']}/100")
        st.write(f"- Quant score: {signal_data.get('quant_score', 0)}")
        st.write(f"- News score: {signal_data.get('news_score', 0)}")
        st.write(f"- Alternative data adjustment: {signal_data.get('alternative_data_score', 0)}")

        st.markdown("**Reasons**")
        for reason in signal_data["reasons"]:
            st.info(f"- {reason}")

        st.markdown("**Risks**")
        for risk_item in signal_data["risks"]:
            st.warning(f"- {risk_item}")

        with st.form("save_prediction_form"):
            time_horizon = st.text_input("Time horizon (optional)", value="")
            save_prediction = st.form_submit_button("Save prediction")
            if save_prediction:
                entry = add_prediction(
                    symbol=signal_data["symbol"],
                    signal=signal_data["signal"],
                    score=signal_data["score"],
                    reasons=signal_data["reasons"],
                    risks=signal_data["risks"],
                    price_at_signal=snapshot.get("price", ""),
                    time_horizon=time_horizon,
                    quant_score=signal_data.get("quant_score", ""),
                    news_score=signal_data.get("news_score", ""),
                    volatility=risk.get("volatility_pct", ""),
                    max_drawdown=risk.get("max_drawdown_pct", ""),
                    backtest_return=backtest_return,
                    suggested_action=signal_data["signal"],
                )
                st.success("Prediction saved to prediction log.")
                st.write(entry)


def render_learning_engine(selected_asset=None, current_price=None):
    """Render a simple rule-based learning summary from saved predictions."""
    st.header("Learning Engine")
    st.caption(
        "Research-only learning summary. This is descriptive, not a model, and does not auto-execute trades."
    )

    predictions = load_predictions()
    if selected_asset:
        predictions = [row for row in predictions if row.get("symbol") == selected_asset]

    if not predictions:
        st.write("No saved predictions yet. Save a prediction and revisit this section to see learning insights.")
        return

    evaluated_predictions = []
    for prediction in predictions:
        if current_price is not None:
            evaluation = evaluate_prediction(prediction, current_price)
        else:
            evaluation = {
                "realized_return_pct": prediction.get("realized_return"),
                "correct_direction": prediction.get("correct_direction"),
                "evaluation_label": prediction.get("evaluation_label"),
            }
        merged = dict(prediction)
        merged.update(evaluation)
        evaluated_predictions.append(merged)

    analysis = analyze_signal_effectiveness(evaluated_predictions)

    st.write("**Top positive factors**")
    if analysis["top_positive_factors"]:
        for factor in analysis["top_positive_factors"]:
            st.success(f"- {factor}")
    else:
        st.info("No strong positive patterns were found in the current sample.")

    st.write("**Top negative factors**")
    if analysis["top_negative_factors"]:
        for factor in analysis["top_negative_factors"]:
            st.warning(f"- {factor}")
    else:
        st.info("No strong negative patterns were found in the current sample.")

    st.write("**Hit rate by signal type**")
    hit_rate_rows = [
        {"Signal type": signal_type, "Hit rate %": value}
        for signal_type, value in analysis["hit_rate_by_signal_type"].items()
    ]
    if hit_rate_rows:
        st.dataframe(hit_rate_rows, width="stretch")
    else:
        st.write("Not enough evaluated predictions to compare hit rates yet.")

    st.write("**Average return by signal type**")
    avg_return_rows = [
        {"Signal type": signal_type, "Average return %": value}
        for signal_type, value in analysis["avg_return_by_signal_type"].items()
    ]
    if avg_return_rows:
        st.dataframe(avg_return_rows, width="stretch")
    else:
        st.write("Not enough evaluated predictions to compare average returns yet.")

    st.markdown("**Learning summary**")
    st.write(analysis["learning_summary"])


def render_news_intelligence(symbol, show_debug=False):
    """Render event-aware news intelligence research context.

    Args:
        symbol: asset symbol
        show_debug: if True, show raw news debug expander
    """
    context = generate_news_context(symbol)
    with st.expander("News Intelligence", expanded=True):
        st.subheader("Event-aware research context")
        st.write("This is event-aware research context, not prediction.")

        st.markdown("**Headline summary**")
        # Prefer concise bullet summary generated from recent headlines
        recent = context.get("recent_headlines") or get_recent_news(symbol)
        if recent:
            # Use top 2-3 headlines as short bullets
            for item in recent[:3]:
                title = item.get("title") or "Untitled headline"
                # Shorten long titles for readability
                short = title if len(title) <= 140 else title[:137] + "..."
                st.write(f"- {short}")
        else:
            # fallback to whatever summary exists
            summary = context.get("headline_summary") or "No summary available."
            # keep it short: truncate to ~200 chars
            if len(summary) > 200:
                summary = summary[:197] + "..."
            st.write(summary)

        st.markdown("**Market sentiment**")
        sentiment_color = {
            "Bullish": "✅",
            "Neutral": "⚖️",
            "Bearish": "⚠️",
        }.get(context["market_sentiment"], "")
        st.write(f"{sentiment_color} {context['market_sentiment']}")

        st.markdown("**Event tags**")
        if context["event_tags"]:
            st.write(", ".join(context["event_tags"]))
        else:
            st.write("None")

        st.markdown("**Risk flags**")
        if context["risk_flags"]:
            for flag in context["risk_flags"]:
                st.warning(f"- {flag}")
        else:
            st.write("None")

        # Show recent headlines if available (numbered top 5)
        recent = context.get("recent_headlines") or get_recent_news(symbol)
        st.markdown("**Recent headlines**")
        if recent:
            md_lines = []
            count = 0
            for i, item in enumerate(recent[:5], start=1):
                title = item.get("title") or "Untitled headline"
                publisher = item.get("publisher") or "Unknown publisher"
                link = item.get("link") or ""
                pubtime = item.get("publish_time")
                time_str = ""
                try:
                    if hasattr(pubtime, "strftime"):
                        time_str = pubtime.strftime("%Y-%m-%d %H:%M")
                    elif pubtime:
                        time_str = str(pubtime)
                except Exception:
                    time_str = str(pubtime)

                # Skip empty items
                if not title and not publisher and not link:
                    continue

                count += 1
                if link:
                    md_lines.append(f"{count}. [{title}]({link}) — {publisher} {time_str}")
                else:
                    md_lines.append(f"{count}. {title} — {publisher} {time_str}")

            if md_lines:
                st.markdown("\n".join(md_lines))
            else:
                st.write("No recent headlines available.")
        else:
            st.write("No recent headlines available.")

        # Raw news debug: only show when explicitly requested
        if show_debug:
            try:
                import yfinance as yf

                raw = getattr(yf.Ticker(symbol), "news", None)
                if raw:
                    with st.expander("Raw news debug", expanded=False):
                        first = raw[0]
                        try:
                            st.json(first)
                        except Exception:
                            st.write(first)
            except Exception:
                # ignore debug fetch failures silently
                pass


def render_prediction_log(selected_asset, current_price):
    """Render the saved prediction log and evaluation section."""
    predictions = [
        entry
        for entry in load_predictions()
        if entry.get("symbol") == selected_asset
    ]

    with st.expander("View Prediction Log", expanded=False):
        st.subheader("Prediction Learning")
        st.write(
            "This section stores research-only signals for later evaluation."
        )

        if not predictions:
            st.write("No saved predictions yet.")
            return

        recent = list(reversed(predictions))[:5]
        for entry in recent:
            st.markdown(
                f"**{entry['date']} | {entry['symbol']} | {entry['signal']} | Score {entry['score']}**"
            )
            st.write(f"- Price at signal: {entry['price_at_signal']}")
            st.write(f"- Time horizon: {entry['time_horizon'] or 'None'}")
            st.write(f"- Outcome: {entry['outcome'] or 'Pending'}")
            st.write("- Reasons:")
            for reason in entry["reasons"].split(" | "):
                st.info(f"  - {reason}")
            st.write("- Risks:")
            for risk_item in entry["risks"].split(" | "):
                st.warning(f"  - {risk_item}")
            st.write("---")


def render_prediction_evaluation(symbol, current_price):
    """Render research-only evaluation results for saved predictions."""
    summary = evaluate_all_predictions(symbol, current_price)

    with st.expander("Prediction Learning Summary", expanded=True):
        st.write("Research-only signal evaluation. This is not trading advice.")

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total predictions", summary["total_predictions"])
        col2.metric("Hit rate", f"{summary['hit_rate']:.2f}%")
        col3.metric("Avg return", f"{summary['average_return']:+.2f}%")
        best = summary["best_trade"]
        worst = summary["worst_trade"]
        col4.metric("Best", f"{best:+.2f}%" if best is not None else "N/A")
        col5.metric("Worst", f"{worst:+.2f}%" if worst is not None else "N/A")

        st.markdown("**Recent evaluated predictions**")
        if not summary["recent_predictions"]:
            st.write("No evaluated predictions yet.")
            return

        for entry in summary["recent_predictions"]:
            return_pct = entry.get("realized_return_pct")
            return_text = (
                f"{return_pct:+.2f}%" if return_pct is not None else "N/A"
            )
            st.markdown(
                f"**{entry['date']} | {entry['symbol']} | {entry['signal']}**"
            )
            st.write(f"- Price at signal: {entry['price_at_signal']}")
            st.write(f"- Current price: {current_price}")
            st.write(f"- Realized return: {return_text}")
            st.write(f"- Correct direction: {entry['correct_direction']}")
            st.write(f"- Evaluation: {entry['evaluation_label']}")
            st.write("---")


def render_decision_journal(symbol, trade_decision, snapshot):
    """Render decision journal capture and feedback loop for one symbol."""
    st.header("Decision Journal")
    st.caption("Research-only feedback loop for Trade Decision Assistant outcomes.")

    current_price = snapshot.get("price") if isinstance(snapshot, dict) else None

    with st.form("save_decision_journal_form"):
        time_horizon = st.text_input("Decision time horizon (optional)", value="")
        lesson = st.text_input("Lesson (optional)", value="")
        save_now = st.form_submit_button("Save Current Decision")
        if save_now:
            entry = save_decision(
                symbol=symbol,
                suggested_action=trade_decision.get("suggested_action", "Watch"),
                confidence=trade_decision.get("confidence", 5),
                price_at_decision=current_price if current_price is not None else "",
                reasons=trade_decision.get("reasons", []),
                risks=trade_decision.get("risks", []),
                time_horizon=time_horizon,
                lesson=lesson,
            )
            st.success("Decision saved to journal.")
            st.write(entry)

    all_decisions = load_decisions()
    recent = [row for row in all_decisions if row.get("symbol") == symbol]
    recent = list(reversed(recent))[:5]

    st.markdown("**Recent saved decisions**")
    if recent:
        for row in recent:
            st.write(
                f"- {row.get('date', '')} | {row.get('suggested_action', 'N/A')} | "
                f"Confidence {row.get('confidence', 'N/A')} | Horizon {row.get('time_horizon', 'None') or 'None'}"
            )
    else:
        st.write("No saved decisions yet for this symbol.")

    evaluated = evaluate_decisions_for_symbol(symbol, current_price)
    counts = evaluated.get("summary_counts", {})
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Good", counts.get("Good", 0))
    col2.metric("Mixed", counts.get("Mixed", 0))
    col3.metric("Poor", counts.get("Poor", 0))
    col4.metric("Pending", counts.get("Pending", 0))

    st.markdown("**Evaluated outcomes**")
    rows = evaluated.get("evaluated_decisions", [])[:5]
    if rows:
        for row in rows:
            ret = row.get("realized_return_pct")
            ret_text = f"{ret:+.2f}%" if isinstance(ret, (int, float)) else "Pending"
            st.write(
                f"- {row.get('date', '')} | {row.get('suggested_action', 'N/A')} | "
                f"Return {ret_text} | Outcome {row.get('outcome_label', 'Pending')}"
            )
            lesson = row.get("lesson", "")
            if lesson:
                st.info(f"Lesson: {lesson}")
    else:
        st.write("No evaluated outcomes yet.")


def render_experiment_tracker():
    """Render experiment tracking for research/model strategy iterations."""
    st.header("Experiment Tracker")
    st.caption("Quick examples:")
    st.code(
        "Test SMA50 vs SMA20\n"
        "Add news-aware scoring\n"
        "Change conservative allocation cap\n"
        "Add sector context to portfolio optimizer",
        language="text",
    )

    with st.form("experiment_form"):
        experiment_name = st.text_input("Experiment name")
        experiment_type = st.selectbox(
            "Experiment type",
            ["Strategy", "Signal", "Research Mode", "Portfolio", "Data", "Other"],
            index=0,
        )
        description = st.text_area("Description", height=80)
        changed_modules = st.text_input("Changed modules (comma separated)")
        hypothesis = st.text_area("Hypothesis", height=70)
        metrics_before = st.text_input("Metrics before")
        status = st.selectbox(
            "Status",
            ["Planned", "Running", "Completed", "Rejected"],
            index=0,
        )
        save_clicked = st.form_submit_button("Save experiment")

    if save_clicked:
        if experiment_name.strip():
            save_experiment(
                experiment_name=experiment_name.strip(),
                experiment_type=experiment_type,
                description=description.strip(),
                changed_modules=changed_modules.strip(),
                hypothesis=hypothesis.strip(),
                metrics_before=metrics_before.strip(),
                status=status,
            )
            st.success("Experiment saved.")
        else:
            st.warning("Experiment name is required.")

    experiments = load_experiments()
    st.subheader("Recent experiments")
    if experiments:
        st.dataframe(experiments[:10], width="stretch")
    else:
        st.write("No experiments tracked yet.")

    with st.expander("Update Experiment Result", expanded=False):
        names = [
            row.get("experiment_name", "")
            for row in experiments
            if row.get("experiment_name")
        ]
        selected_name = st.selectbox("Experiment", names) if names else ""
        result_summary = st.text_input("Result summary", value="")
        lesson = st.text_area("Lesson learned", height=70)
        metrics_after = st.text_input("Metrics after", value="")
        update_status = st.selectbox(
            "Status update",
            ["Completed", "Running", "Rejected", "Planned"],
            index=0,
        )
        if st.button("Update experiment"):
            if selected_name:
                updated = update_experiment_result(
                    experiment_name=selected_name,
                    result=result_summary.strip() or "Updated",
                    lesson=lesson.strip(),
                    status=update_status,
                    metrics_after=metrics_after.strip(),
                )
                if updated:
                    st.success("Experiment updated.")
                else:
                    st.warning("Could not find that experiment name.")
            else:
                st.warning("No experiment selected.")

    st.subheader("Experiment Comparator")
    st.caption(
        "Example metrics format: win_rate=55, avg_return=4.2, avg_alpha=1.1, max_drawdown=-8, consistency_score=70"
    )
    comparator_before = st.text_input(
        "Metrics before",
        value="win_rate=55, avg_return=4.2, avg_alpha=1.1, max_drawdown=-8, consistency_score=70",
        key="experiment_comparator_before",
    )
    comparator_after = st.text_input(
        "Metrics after",
        value="win_rate=58, avg_return=4.8, avg_alpha=1.4, max_drawdown=-6.5, consistency_score=75",
        key="experiment_comparator_after",
    )

    if st.button("Compare Results"):
        comparison = compare_experiment_results(comparator_before, comparator_after)
        st.markdown("**Improved metrics**")
        if comparison.get("improved_metrics"):
            for row in comparison["improved_metrics"]:
                st.success(f"- {row}")
        else:
            st.write("None")

        st.markdown("**Worsened metrics**")
        if comparison.get("worsened_metrics"):
            for row in comparison["worsened_metrics"]:
                st.warning(f"- {row}")
        else:
            st.write("None")

        st.metric("Overall result", comparison.get("overall_result", "Inconclusive"))
        st.write(comparison.get("summary", "No summary available."))

    st.caption(
        "Research-only experiment tracking. No live trading, no broker APIs, no auto execution."
    )


def render_research_review_agent(
    prediction_summary=None,
    research_run_summary=None,
    experiment_summary=None,
    leaderboard_summary=None,
    portfolio_performance=None,
):
    """Render an automated review agent for research learning quality."""
    review = generate_research_review(
        prediction_summary=prediction_summary,
        research_run_summary=research_run_summary,
        experiment_summary=experiment_summary,
        leaderboard_summary=leaderboard_summary,
        portfolio_performance=portfolio_performance,
    )

    st.header("Automated Research Review Agent")
    st.metric("System status", review.get("overall_system_status", "Insufficient Data"))

    st.markdown("**What is working**")
    for item in review.get("what_is_working", []):
        st.success(f"- {item}")

    st.markdown("**What is not working**")
    for item in review.get("what_is_not_working", []):
        st.warning(f"- {item}")

    st.markdown("**Biggest risks**")
    for item in review.get("biggest_risks", []):
        st.error(f"- {item}")

    st.markdown("**Recommended next experiments**")
    for item in review.get("recommended_next_experiments", []):
        st.info(f"- {item}")

    st.markdown("**Developer notes**")
    for item in review.get("developer_notes", []):
        st.write(f"- {item}")

    st.write(review.get("summary", "No summary available."))
    st.caption(
        "Research-only review guidance. No broker APIs, no live trading, no auto execution, and no guaranteed returns."
    )
    return review


def render_governance_review(
    meta_decision=None,
    conviction_data=None,
    execution_data=None,
    position_size_data=None,
    prediction_accuracy=None,
    benchmark_data=None,
    research_mode="Balanced",
):
    """Render model governance and safety checks for research conclusions."""
    governance = run_governance_review(
        meta_decision=meta_decision,
        conviction_data=conviction_data,
        execution_data=execution_data,
        position_size_data=position_size_data,
        prediction_accuracy=prediction_accuracy,
        benchmark_data=benchmark_data,
        research_mode=research_mode,
    )

    st.header("Model Governance / Safety Review")
    col1, col2 = st.columns(2)
    col1.metric("Governance status", governance.get("governance_status", "Needs Review"))
    col2.metric("Evidence quality", governance.get("evidence_quality", "Low"))

    st.markdown("**Overconfidence flags**")
    flags = governance.get("overconfidence_flags", [])
    if flags:
        for item in flags:
            st.warning(f"- {item}")
    else:
        st.write("None")

    st.markdown("**Risk flags**")
    risks = governance.get("risk_flags", [])
    if risks:
        for item in risks:
            st.error(f"- {item}")
    else:
        st.write("None")

    st.markdown("**Required disclaimers**")
    for item in governance.get("required_disclaimers", []):
        st.info(f"- {item}")

    st.markdown("**Approval notes**")
    for item in governance.get("approval_notes", []):
        st.write(f"- {item}")

    st.write(governance.get("summary", "No governance summary available."))
    st.caption(
        "Research-only governance review. Human review is always required. No broker APIs, live trading, or auto execution."
    )
    return governance


def render_research_journal(watchlist, selected_asset):
    """Render the research journal form and recent entries."""
    with st.expander("Add Research Journal Entry", expanded=True):
        with st.form("journal_form"):
            journal_symbol = st.selectbox(
                "Journal symbol", watchlist, index=watchlist.index(selected_asset)
            )
            thesis = st.text_area("Thesis", height=120)
            signal = st.selectbox("Signal", ["Watch", "Buy Thesis", "Sell Thesis", "Hold"])
            confidence = st.slider("Confidence", min_value=1, max_value=10, value=5)
            risk_notes = st.text_area("Risk notes", height=100)
            entry_price = st.number_input("Entry price", min_value=0.0, value=0.0, step=0.01)
            target_price = st.number_input("Target price", min_value=0.0, value=0.0, step=0.01)
            time_horizon = st.text_input("Time horizon", value="")
            save = st.form_submit_button("Save journal entry")
            if save:
                entry = add_journal_entry(
                    symbol=journal_symbol,
                    thesis=thesis,
                    signal=signal,
                    confidence=confidence,
                    risk_notes=risk_notes,
                    entry_price=entry_price,
                    target_price=target_price,
                    time_horizon=time_horizon,
                )
                st.success("Journal entry saved.")
                st.write(entry)

    journal_entries = load_journal()
    with st.expander("View Recent Journal Entries", expanded=False):
        if journal_entries:
            for entry in reversed(journal_entries[-5:]):
                st.markdown(
                    f"**{entry['date']} | {entry['symbol']} | {entry['signal']}**\n"
                    f"- Confidence: {entry['confidence']}\n"
                    f"- Thesis: {entry['thesis']}\n"
                    f"- Risk notes: {entry['risk_notes']}"
                )
        else:
            st.write("No recent journal entries available.")


def render_roadmap():
    """Render the project roadmap section."""
    st.header("Roadmap")
    st.markdown(
        """
    - Backtesting
    - Portfolio comparison
    - AI summaries
    - Risk insights
    """
    )


def render_health_check():
    """Render a simple system health check for core research engines."""
    health = run_health_check()
    st.header("System Health Check")
    st.metric("Status", health.get("status", "Warning"))

    st.markdown("**Checks**")
    for item in health.get("checks", []):
        st.success(f"- {item}")
    if not health.get("checks"):
        st.write("No checks were completed.")

    st.markdown("**Issues**")
    issues = health.get("issues", [])
    if issues:
        for item in issues:
            st.warning(f"- {item}")
    else:
        st.write("No issues detected.")

    st.write(health.get("summary", "No summary available."))


def render_database_status():
    """Render centralized SQLite research database status."""
    db = get_database_status()
    st.header("Research Database Status")
    st.metric("Connected", "Yes" if db.get("connected") else "No")
    st.write(f"Database path: {db.get('db_path', 'N/A')}")

    st.markdown("**Tables available**")
    for table in db.get("tables", []):
        st.write(f"- {table}")

    st.markdown("**Row counts**")
    row_counts = db.get("row_counts", {})
    if row_counts:
        st.dataframe(
            [{"table": name, "rows": count} for name, count in row_counts.items()],
            width="stretch",
        )
    else:
        st.write("No row count data available.")

    summary = (
        f"SQLite status: {'connected' if db.get('connected') else 'disconnected'} with "
        f"{len(row_counts)} tracked table count(s)."
    )
    st.write(summary)


def render_workflow_orchestrator(
    symbol,
    price_data,
    snapshot,
    research_mode,
):
    """Render central orchestrated workflow state for major research modules."""
    report = run_orchestrated_workflow(
        symbol=symbol,
        price_data=price_data,
        snapshot=snapshot,
        research_mode=research_mode,
    )

    st.header("Agent Workflow Orchestrator")
    col1, col2 = st.columns(2)
    col1.metric("Workflow status", report.get("workflow_status", "Failed"))
    col2.metric("Runtime (ms)", f"{report.get('workflow_runtime_ms', 0):.2f}")

    st.markdown("**Steps completed**")
    for step in report.get("steps_completed", []):
        st.success(f"- {step}")
    if not report.get("steps_completed"):
        st.write("No steps completed.")

    st.markdown("**Failed steps**")
    for step in report.get("steps_failed", []):
        st.warning(f"- {step}")
    if not report.get("steps_failed"):
        st.write("No failed steps.")

    st.markdown("**Final summary**")
    st.write(report.get("final_summary", "No summary available."))
    st.write(
        f"Human review required: {'Yes' if report.get('human_review_required', True) else 'No'}"
    )
    st.caption("Research-only orchestration layer. No broker APIs, no live trading, no auto execution.")
    return report


def render_subagent_reviews(workflow_outputs, research_mode):
    """Render a role-based sub-agent review board."""
    board = run_subagent_reviews(workflow_outputs, research_mode=research_mode)
    st.header("Sub-Agent Review Board")

    for review in board.get("agent_reviews", []):
        with st.expander(f"{review.get('agent_name', 'Agent')} — {review.get('status', 'Needs Review')}", expanded=False):
            st.markdown("**Key points**")
            for point in review.get("key_points", []):
                st.info(f"- {point}")

            st.markdown("**Concerns**")
            concerns = review.get("concerns", [])
            if concerns:
                for concern in concerns:
                    st.warning(f"- {concern}")
            else:
                st.write("No major concerns flagged.")

            st.markdown("**Recommendation**")
            st.write(review.get("recommendation", "No recommendation available."))

    st.markdown("**Consensus view**")
    st.write(board.get("consensus_view", "Mixed Consensus"))

    st.markdown("**Major disagreements**")
    disagreements = board.get("major_disagreements", [])
    if disagreements:
        for item in disagreements:
            st.warning(f"- {item}")
    else:
        st.write("No major disagreements.")

    st.write(
        f"Human review required: {'Yes' if board.get('human_review_required', True) else 'No'}"
    )
    st.write(board.get("summary", "No summary available."))
    st.caption("Research-only multi-agent review board. No broker APIs, no live trading, no auto execution.")
    return board


def render_executive_dashboard(
    symbol,
    meta_decision,
    conviction_data,
    allocation_timing,
    position_size,
    entry_exit,
    exposure_limits,
    correlation_data,
    subagent_reviews,
    research_mode,
):
    """Render a top-level executive summary across major engines."""
    summary = generate_executive_summary(
        symbol,
        meta_decision,
        conviction_data,
        allocation_timing,
        position_size,
        entry_exit,
        exposure_limits,
        correlation_data,
        subagent_reviews,
        research_mode=research_mode,
    )

    st.header("Executive Dashboard")
    col1, col2 = st.columns(2)
    col1.metric("Headline verdict", summary.get("headline_verdict", "Watch"))
    col2.metric("Agent consensus", summary.get("agent_consensus", "Mixed Consensus"))

    st.write(f"Recommended next action: {summary.get('recommended_next_action', 'N/A')}")
    st.write(f"Suggested paper allocation: {summary.get('suggested_paper_allocation', 'N/A')}")
    st.write(f"Timing view: {summary.get('timing_view', 'N/A')}")

    st.markdown("**Top reasons**")
    for item in summary.get("top_reasons", []):
        st.success(f"- {item}")

    st.markdown("**Top risks**")
    for item in summary.get("top_risks", []):
        st.warning(f"- {item}")

    st.markdown("**Portfolio warning**")
    st.write(summary.get("portfolio_warning", "N/A"))
    st.write(
        f"Human review required: {'Yes' if summary.get('human_review_required', True) else 'No'}"
    )
    st.write(summary.get("summary", "No summary available."))
    st.caption("Research-only decision support. No broker APIs, no live trading, no auto execution.")
    return summary


def render_prediction_accuracy_dashboard(prediction_log, benchmark_returns=None):
    """Render prediction accuracy and calibration quality over time."""
    st.header("Prediction Accuracy Dashboard")
    accuracy = evaluate_prediction_accuracy(
        prediction_log,
        benchmark_returns=benchmark_returns,
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Win rate", f"{accuracy.get('win_rate', 0.0):.2f}%")
    col2.metric("Avg return after signal", f"{accuracy.get('avg_return_after_signal', 0.0):+.2f}%")
    col3.metric("False positive rate", f"{accuracy.get('false_positive_rate', 0.0):.2f}%")
    col4.metric("Alpha vs ETF benchmark", f"{accuracy.get('alpha_vs_benchmark', 0.0):+.2f}%")

    col5, col6, col7 = st.columns(3)
    col5.metric("Avg drawdown after signal", f"{accuracy.get('avg_drawdown_after_signal', 0.0):.2f}%")
    col6.metric("Best holding window", accuracy.get("best_holding_window", "Not enough data"))
    col7.metric("Sample confidence", accuracy.get("sample_confidence", "No evidence yet"))

    st.write(f"Worst holding window: {accuracy.get('worst_holding_window', 'Not enough data')}")

    with st.expander("Calibration breakdowns", expanded=False):
        grouped_sections = [
            ("By signal", accuracy.get("grouped_by_signal", [])),
            ("By regime", accuracy.get("grouped_by_regime", [])),
            ("By horizon", accuracy.get("grouped_by_horizon", [])),
            ("By asset class", accuracy.get("grouped_by_asset_class", [])),
        ]
        for label, rows in grouped_sections:
            st.markdown(f"**{label}**")
            if rows:
                st.dataframe(rows, width="stretch")
            else:
                st.write("No grouped data yet.")

    st.write("**Lessons learned**")
    lessons = accuracy.get("lessons", [])
    if lessons:
        for lesson in lessons:
            st.info(f"- {lesson}")
    else:
        st.write("No lessons available yet.")

    st.write("**Calibration summary**")
    st.write(accuracy.get("summary", "No calibration summary available."))
    st.caption(
        accuracy.get(
            "disclaimer",
            "Research-only accuracy tracking. No broker APIs, no auto execution, and no guaranteed future returns.",
        )
    )
    return accuracy
