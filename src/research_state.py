"""Shared helpers for global research ticker selection."""


def _normalize_symbol(symbol):
    return str(symbol or "").upper().strip()


def _add_symbol(symbols, seen, symbol):
    normalized = _normalize_symbol(symbol)
    if normalized and normalized not in seen:
        seen.add(normalized)
        symbols.append(normalized)


def build_research_universe(watchlist, opportunity_rows=None, paper_positions=None, selected_asset=""):
    """Build the session research universe from watchlist, opportunities, positions, and selected ticker."""
    symbols = []
    seen = set()

    for symbol in watchlist or []:
        _add_symbol(symbols, seen, symbol)

    for row in opportunity_rows or []:
        if isinstance(row, dict):
            _add_symbol(symbols, seen, row.get("symbol"))
        else:
            _add_symbol(symbols, seen, row)

    positions = paper_positions or {}
    if isinstance(positions, dict):
        position_rows = positions.get("positions", positions)
        if isinstance(position_rows, dict):
            for symbol in position_rows:
                _add_symbol(symbols, seen, symbol)
    elif isinstance(positions, list):
        for row in positions:
            if isinstance(row, dict):
                _add_symbol(symbols, seen, row.get("symbol"))

    _add_symbol(symbols, seen, selected_asset)
    return symbols


def promote_symbol_to_selected(symbol, state=None):
    """Promote a ticker into the global selected asset state."""
    normalized = _normalize_symbol(symbol)
    if not normalized:
        return ""

    if state is None:
        import streamlit as st

        state = st.session_state

    state["selected_asset"] = normalized
    state["custom_research_symbol"] = normalized
    return normalized
