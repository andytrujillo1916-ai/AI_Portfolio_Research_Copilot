import streamlit as st

from market_data import get_asset_comparison, get_risk_metrics
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
from data_quality_engine import summarize_data_sources
from opportunistic_screener_engine import rank_opportunistic_stocks
from benchmark_basket_engine import find_best_etf_benchmark
from strategy_scorecard_engine import generate_strategy_scorecard
from auto_paper_trader import build_auto_paper_trade_ticket, save_auto_paper_trade


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
    st.write(status.get("summary", "No data-source summary available."))


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
):
    """Render alpha comparison versus a selected benchmark."""
    st.header("Alpha vs Benchmark Engine")
    benchmark_symbol = st.selectbox(
        "Benchmark",
        ["SPY", "QQQ", "VOO"],
        index=0,
        key="alpha_benchmark_select",
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
    col2.metric("Suggested adjustments", len(insights["suggested_weight_adjustments"]))

    st.markdown("**Positive factors**")
    for factor in insights["strong_positive_factors"]:
        st.success(f"- {factor}")

    st.markdown("**Weak negative factors**")
    for factor in insights["weak_negative_factors"]:
        st.warning(f"- {factor}")

    st.markdown("**Suggested weight adjustments**")
    for factor, adjustment in insights["suggested_weight_adjustments"].items():
        st.write(f"- {factor}: {adjustment:.2f}x")

    st.markdown("**Summary**")
    st.write(insights["summary"])


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
    adaptive_context = calculate_factor_insights(load_predictions(), load_research_runs())
    signal_data = generate_signal(
        selected_asset,
        snapshot,
        risk,
        news_context=news_context,
        adaptive_context=adaptive_context,
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
