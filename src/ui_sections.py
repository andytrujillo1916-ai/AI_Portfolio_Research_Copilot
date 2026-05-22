import streamlit as st

from market_data import get_asset_comparison, get_risk_metrics
from journal import add_journal_entry, load_journal
from prediction_log import add_prediction, evaluate_all_predictions
from research_agent import generate_research_summary
from signal_engine import generate_signal
from backtester import run_simple_backtest


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


def render_backtest_section(price_data):
    """Run a simple backtest and display results."""
    results = run_simple_backtest(price_data)
    st.header("Backtesting")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Buy & Hold", f"{results['buy_and_hold_return_pct']:+.2f}%")
    col2.metric("Strategy", f"{results['strategy_return_pct']:+.2f}%")
    col3.metric("Max drawdown", f"{results['max_drawdown_pct']:.2f}%")
    col4.metric("Signal changes", f"{results['number_of_signal_changes']}")


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


def render_signal_engine(selected_asset, snapshot, risk):
    """Render the signal engine section and allow saving predictions."""
    signal_data = generate_signal(selected_asset, snapshot, risk)
    with st.expander("Signal Engine", expanded=True):
        st.subheader("Research-only quant signal")
        st.write(f"**Signal:** {signal_data['signal']}")
        st.write(f"**Score:** {signal_data['score']}/100")

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
                )
                st.success("Prediction saved to prediction log.")
                st.write(entry)


def render_prediction_log(selected_asset, current_price):
    """Render the saved prediction log and evaluation section."""
    predictions = evaluate_all_predictions({selected_asset: current_price})

    with st.expander("View Prediction Log", expanded=False):
        st.subheader("Prediction Learning")
        st.write(
            "This section checks whether saved signals were useful over time."
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
            if entry.get("current_price") is not None:
                st.write(f"- Current price: {entry['current_price']}")
                st.write(f"- Price change: {entry['price_change_pct']:+.2f}%")
                st.write(f"- Evaluation: {entry['simple_result']}")
            st.write("- Reasons:")
            for reason in entry["reasons"].split(" | "):
                st.info(f"  - {reason}")
            st.write("- Risks:")
            for risk_item in entry["risks"].split(" | "):
                st.warning(f"  - {risk_item}")
            st.write("---")


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
