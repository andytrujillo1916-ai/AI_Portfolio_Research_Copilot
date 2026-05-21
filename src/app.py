import streamlit as st
from market_data import (
    get_watchlist,
    get_price_history,
    get_market_snapshot,
    get_asset_comparison,
    get_risk_metrics,
)
from journal import add_journal_entry, load_journal

st.set_page_config(page_title="AI Portfolio Research Copilot", layout="wide")

st.title("AI Portfolio Research Copilot")
st.write("Investment research dashboard, not a trading bot.")

watchlist = get_watchlist()
selected_asset = st.selectbox("Select an asset", watchlist)
period = st.selectbox("Period", ["5d", "1mo", "3mo", "6mo", "1y"], index=1)

st.header("Market Snapshot")
snapshot = get_market_snapshot(selected_asset)
col1, col2, col3 = st.columns(3)
price_display = f"${snapshot['price']:.2f}" if isinstance(snapshot.get('price'), (int, float)) else snapshot.get('price')
col1.metric("Price", price_display, delta=f"{snapshot.get('change_pct', 0):+.2f}%")
col2.metric("Daily change", f"{snapshot.get('change_pct', 0):+.2f}%")
col3.metric("Volume", f"{snapshot.get('volume', 0):,}")
if snapshot.get("source") == "mock":
    st.warning(f"Using fallback market snapshot data. Reason: {snapshot.get('error', 'unknown')}")

shares = st.number_input("Shares owned", min_value=0.0, value=0.0, step=1.0)
position_value = shares * snapshot.get("price", 0) if isinstance(snapshot.get("price"), (int, float)) else 0
st.metric("Position value", f"${position_value:,.2f}")

st.header("Price Chart")
price_data = get_price_history(selected_asset, period=period)
price_source = None
chart_data = price_data
if isinstance(price_data, dict) and "source" in price_data:
    price_source = price_data.get("source")
    chart_data = price_data.get("data")
    if price_source == "mock":
        st.warning(f"Using fallback price history data. Reason: {price_data.get('error', 'unknown')}")
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

st.header("Asset Comparison")
compare_assets = st.multiselect(
    "Compare with assets",
    [asset for asset in watchlist if asset != selected_asset],
    default=[asset for asset in watchlist if asset != selected_asset][:2],
)
normalize = st.checkbox("Normalize performance (start all at 100)", value=True)
st.caption("Normalized view compares growth, not raw asset price.")

if compare_assets:
    compare_symbols = [selected_asset] + compare_assets
    comparison = get_asset_comparison(compare_symbols, period=period, normalize=normalize)
    comp_source = None
    comp_data = comparison
    if isinstance(comparison, dict) and "source" in comparison:
        comp_source = comparison.get("source")
        comp_data = comparison.get("data")
        if comp_source == "mock":
            st.warning(f"Using fallback comparison data. Reason: {comparison.get('error', 'unknown')}")
        elif comp_source == "yfinance":
            st.caption("Real yfinance data used for comparison.")

    # Plot DataFrame or fallback dict/list
    if hasattr(comp_data, "set_index"):
        st.line_chart(comp_data)
    elif isinstance(comp_data, dict):
        # dict of lists
        st.line_chart(comp_data)
    else:
        st.line_chart(comp_data)

st.header("Research Notes")
notes = st.text_area(f"Notes for {selected_asset}", height=180)
if notes:
    st.write("**Current notes:**")
    st.write(notes)

st.header("Research Journal")
with st.form("journal_form"):
    journal_symbol = st.selectbox("Journal symbol", watchlist, index=watchlist.index(selected_asset))
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
if journal_entries:
    with st.expander("Recent journal entries", expanded=False):
        for i, entry in enumerate(reversed(journal_entries[-5:]), 1):
            st.markdown(
                f"**{entry['date']} | {entry['symbol']} | {entry['signal']}**\n"
                f"- Confidence: {entry['confidence']}\n"
                f"- Thesis: {entry['thesis']}\n"
                f"- Risk notes: {entry['risk_notes']}"
            )

st.header("Roadmap")
st.markdown(
    """
    - Backtesting
    - Portfolio comparison
    - AI summaries
    - Risk insights
    """
)
