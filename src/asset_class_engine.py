def classify_asset(symbol):
    """Classify a symbol into a broad asset-class context for research-only workflows."""
    sym = str(symbol or "").upper().strip()

    etfs = {
        "SPY", "QQQ", "VOO", "IWM", "DIA", "XLK", "XLV", "XLF", "XLE",
        "XLY", "XLP", "XLI", "XLU", "XLRE", "XLB", "XLC", "SMH", "SOXX",
        "USO", "GLD",
    }
    equities = {
        "AAPL", "MSFT", "NVDA", "GOOGL", "META", "AMZN", "TSLA", "NFLX",
        "AMD", "AVGO", "CRM", "JNJ", "PG", "KO", "PEP", "WMT", "COST",
        "JPM", "BAC", "GS", "XOM", "CVX", "UNH", "LLY", "PFE", "MRK",
    }
    crypto = {"BTC", "ETH", "BTCUSD", "ETHUSD", "BTC-USD", "ETH-USD"}
    futures = {"ES", "NQ", "YM", "RTY", "CL", "GC"}

    if sym in equities:
        return {
            "asset_class": "Equity",
            "market_type": "Listed Equity",
            "trading_profile": "Company-specific",
            "risk_level": "Medium",
            "notes": ["Single-name exposure with earnings and company event sensitivity."],
        }
    if sym in etfs:
        return {
            "asset_class": "ETF",
            "market_type": "Listed Fund",
            "trading_profile": "Basket exposure",
            "risk_level": "Medium",
            "notes": ["Diversified exposure relative to single-name equities."],
        }
    if sym in crypto:
        return {
            "asset_class": "Crypto",
            "market_type": "Digital Asset",
            "trading_profile": "24/7 high-volatility",
            "risk_level": "High",
            "notes": ["Can show larger and faster swings than traditional assets."],
        }
    if sym in futures:
        return {
            "asset_class": "Futures",
            "market_type": "Derivative Contract",
            "trading_profile": "Macro/index-linked",
            "risk_level": "High",
            "notes": ["Futures can move quickly and require tighter risk framing."],
        }
    if "PRED" in sym or "PMKT" in sym:
        return {
            "asset_class": "Prediction Market",
            "market_type": "Event Contract",
            "trading_profile": "Event-driven",
            "risk_level": "High",
            "notes": ["Outcome probabilities can change sharply around news events."],
        }
    if any(token in sym for token in ["C", "P"]) and len(sym) > 6 and any(ch.isdigit() for ch in sym):
        return {
            "asset_class": "Options",
            "market_type": "Derivative Option",
            "trading_profile": "Nonlinear payoff",
            "risk_level": "High",
            "notes": ["Options involve expiry and strike sensitivity."],
        }

    return {
        "asset_class": "Unknown",
        "market_type": "Unknown",
        "trading_profile": "Unknown",
        "risk_level": "Unknown",
        "notes": ["No clear asset-class mapping was found for this symbol yet."],
    }
