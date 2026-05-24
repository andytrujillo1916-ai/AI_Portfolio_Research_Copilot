def map_asset_to_sector(symbol):
    """Map a symbol to a simple sector label for research-only context."""
    if symbol in {"AAPL", "MSFT", "NVDA", "XLK"}:
        return "Technology"
    if symbol == "XLE":
        return "Energy"
    if symbol == "XLV":
        return "Healthcare"
    if symbol in {"SPY", "VOO", "QQQ"}:
        return "Broad Market / Tech Tilt"
    return "Unknown"
