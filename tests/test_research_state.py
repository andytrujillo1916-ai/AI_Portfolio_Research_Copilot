import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from research_state import build_research_universe, promote_symbol_to_selected


def test_custom_ticker_outside_watchlist_becomes_research_universe_symbol():
    universe = build_research_universe(
        ["AAPL", "MSFT"],
        [{"symbol": "NVDA"}, {"symbol": "aapl"}],
        {"positions": {"TSLA": {"shares": 1}}},
        "pltr",
    )

    assert universe == ["AAPL", "MSFT", "NVDA", "TSLA", "PLTR"]


def test_promote_symbol_updates_selected_state():
    state = {}
    promoted = promote_symbol_to_selected(" rklb ", state=state)

    assert promoted == "RKLB"
    assert state["selected_asset"] == "RKLB"
    assert state["custom_research_symbol"] == "RKLB"
