import streamlit as st

from market_data import get_market_snapshot, get_price_history, get_watchlist
from ui_sections import (
    render_asset_comparison,
    render_market_snapshot,
    render_price_chart,
    render_backtest_section,
    render_news_intelligence,
    render_prediction_log,
    render_prediction_evaluation,
    render_research_agent,
    render_signal_engine,
    render_research_journal,
    render_research_notes,
    render_roadmap,
)

st.set_page_config(page_title="AI Portfolio Research Copilot", layout="wide")

st.title("AI Portfolio Research Copilot")
st.write("Investment research dashboard, not a trading bot.")

watchlist = get_watchlist()
selected_asset = st.sidebar.selectbox("Select an asset", watchlist)
period = st.sidebar.selectbox(
    "Period", ["5d", "1mo", "3mo", "6mo", "1y"], index=1
)
shares = st.sidebar.number_input("Shares owned", min_value=0.0, value=0.0, step=1.0)

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

render_market_snapshot(snapshot, shares)

risk = render_price_chart(price_data)
render_news_intelligence(selected_asset)
render_backtest_section(price_data)

compare_assets = st.multiselect(
    "Compare with assets",
    [asset for asset in watchlist if asset != selected_asset],
    default=[asset for asset in watchlist if asset != selected_asset][:2],
)
normalize = st.checkbox("Normalize performance (start all at 100)", value=True)
render_asset_comparison(selected_asset, watchlist, compare_assets, period, normalize)

notes = st.text_area(f"Notes for {selected_asset}", height=180)
render_research_notes(selected_asset, notes)
render_research_agent(selected_asset, snapshot, risk, notes)
render_signal_engine(selected_asset, snapshot, risk)
render_prediction_log(selected_asset, snapshot.get("price"))
render_prediction_evaluation(selected_asset, snapshot.get("price"))

render_research_journal(watchlist, selected_asset)
render_roadmap()
