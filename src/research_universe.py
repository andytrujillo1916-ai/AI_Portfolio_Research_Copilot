def get_research_universe():
    """Return grouped research-only stock/ETF universes for screening."""
    return {
        "Broad ETFs": ["SPY", "VOO", "QQQ", "IWM", "DIA"],
        "Mega-Cap Tech": ["AAPL", "MSFT", "NVDA", "GOOGL", "META", "AMZN"],
        "Growth": ["TSLA", "NFLX", "AMD", "AVGO", "CRM"],
        "Defensive": ["JNJ", "PG", "KO", "PEP", "WMT", "COST"],
        "Semiconductors": ["NVDA", "AMD", "AVGO", "SMH", "SOXX"],
        "Financials": ["JPM", "BAC", "GS", "XLF"],
        "Energy": ["XOM", "CVX", "XLE"],
        "Healthcare": ["UNH", "LLY", "PFE", "MRK", "XLV"],
    }


def get_default_research_watchlist():
    """Return a deduplicated default research watchlist focused on stocks and ETFs."""
    symbols = []
    for group_symbols in get_research_universe().values():
        for symbol in group_symbols:
            if symbol not in symbols:
                symbols.append(symbol)
    return symbols


def get_future_asset_roadmap_symbols():
    """Return non-primary symbols kept as future research roadmap examples only."""
    return {
        "Crypto": ["BTC-USD", "ETH-USD"],
        "Futures Proxies": ["SPY", "QQQ", "USO", "GLD"],
        "Prediction Markets": ["POLYMARKET-RESEARCH"],
        "Sports Analytics": ["SPORTS-RESEARCH"],
    }
