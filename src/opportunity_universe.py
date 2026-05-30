"""Expanded research universe for opportunity discovery.

The universe is intentionally local and source-labeled in V1. It is broad enough
to test US all-cap, ETF, ADR, IPO, and thematic discovery workflows without
depending on paid screeners or broker APIs.
"""


US_ALL_CAP_ROWS = [
    {"symbol": "NVDA", "company": "NVIDIA", "sector": "Technology", "theme": "AI infrastructure", "region": "United States", "market_cap_bucket": "Mega cap"},
    {"symbol": "AMD", "company": "Advanced Micro Devices", "sector": "Technology", "theme": "AI semiconductors", "region": "United States", "market_cap_bucket": "Large cap"},
    {"symbol": "SMCI", "company": "Super Micro Computer", "sector": "Technology", "theme": "AI servers", "region": "United States", "market_cap_bucket": "Mid cap"},
    {"symbol": "PLTR", "company": "Palantir", "sector": "Technology", "theme": "AI software", "region": "United States", "market_cap_bucket": "Large cap"},
    {"symbol": "CRWD", "company": "CrowdStrike", "sector": "Technology", "theme": "Cybersecurity", "region": "United States", "market_cap_bucket": "Large cap"},
    {"symbol": "NET", "company": "Cloudflare", "sector": "Technology", "theme": "Cloud security", "region": "United States", "market_cap_bucket": "Mid cap"},
    {"symbol": "RKLB", "company": "Rocket Lab", "sector": "Industrials", "theme": "Space", "region": "United States", "market_cap_bucket": "Small cap"},
    {"symbol": "ACHR", "company": "Archer Aviation", "sector": "Industrials", "theme": "Advanced air mobility", "region": "United States", "market_cap_bucket": "Small cap"},
    {"symbol": "JOBY", "company": "Joby Aviation", "sector": "Industrials", "theme": "Advanced air mobility", "region": "United States", "market_cap_bucket": "Small cap"},
    {"symbol": "IONQ", "company": "IonQ", "sector": "Technology", "theme": "Quantum computing", "region": "United States", "market_cap_bucket": "Small cap"},
    {"symbol": "RGTI", "company": "Rigetti Computing", "sector": "Technology", "theme": "Quantum computing", "region": "United States", "market_cap_bucket": "Micro cap"},
    {"symbol": "SOUN", "company": "SoundHound AI", "sector": "Technology", "theme": "Voice AI", "region": "United States", "market_cap_bucket": "Small cap"},
    {"symbol": "BBAI", "company": "BigBear.ai", "sector": "Technology", "theme": "AI analytics", "region": "United States", "market_cap_bucket": "Micro cap"},
    {"symbol": "ASTS", "company": "AST SpaceMobile", "sector": "Communication Services", "theme": "Satellite communications", "region": "United States", "market_cap_bucket": "Small cap"},
    {"symbol": "HIMS", "company": "Hims & Hers Health", "sector": "Healthcare", "theme": "Digital health", "region": "United States", "market_cap_bucket": "Mid cap"},
    {"symbol": "TEM", "company": "Tempus AI", "sector": "Healthcare", "theme": "AI healthcare", "region": "United States", "market_cap_bucket": "Small cap"},
    {"symbol": "RXRX", "company": "Recursion Pharmaceuticals", "sector": "Healthcare", "theme": "AI biotech", "region": "United States", "market_cap_bucket": "Small cap"},
    {"symbol": "VRT", "company": "Vertiv", "sector": "Industrials", "theme": "Data center infrastructure", "region": "United States", "market_cap_bucket": "Large cap"},
    {"symbol": "CEG", "company": "Constellation Energy", "sector": "Utilities", "theme": "AI power demand", "region": "United States", "market_cap_bucket": "Large cap"},
    {"symbol": "OKLO", "company": "Oklo", "sector": "Energy", "theme": "Nuclear energy", "region": "United States", "market_cap_bucket": "Small cap"},
    {"symbol": "ENPH", "company": "Enphase Energy", "sector": "Energy", "theme": "Energy transition", "region": "United States", "market_cap_bucket": "Mid cap"},
    {"symbol": "SOFI", "company": "SoFi Technologies", "sector": "Financials", "theme": "Fintech", "region": "United States", "market_cap_bucket": "Mid cap"},
    {"symbol": "HOOD", "company": "Robinhood Markets", "sector": "Financials", "theme": "Fintech brokerage", "region": "United States", "market_cap_bucket": "Mid cap"},
    {"symbol": "DUOL", "company": "Duolingo", "sector": "Consumer Discretionary", "theme": "AI consumer app", "region": "United States", "market_cap_bucket": "Mid cap"},
    {"symbol": "CAVA", "company": "Cava Group", "sector": "Consumer Discretionary", "theme": "Emerging consumer brand", "region": "United States", "market_cap_bucket": "Mid cap"},
    {"symbol": "ELF", "company": "e.l.f. Beauty", "sector": "Consumer Staples", "theme": "Emerging consumer brand", "region": "United States", "market_cap_bucket": "Mid cap"},
]


GLOBAL_ADR_ROWS = [
    {"symbol": "TSM", "company": "Taiwan Semiconductor", "sector": "Technology", "theme": "Semiconductor foundry", "region": "Taiwan", "market_cap_bucket": "Mega cap"},
    {"symbol": "ASML", "company": "ASML", "sector": "Technology", "theme": "Semiconductor equipment", "region": "Netherlands", "market_cap_bucket": "Mega cap"},
    {"symbol": "ARM", "company": "Arm Holdings", "sector": "Technology", "theme": "Chip architecture", "region": "United Kingdom", "market_cap_bucket": "Large cap"},
    {"symbol": "SE", "company": "Sea Limited", "sector": "Communication Services", "theme": "Southeast Asia internet", "region": "Singapore", "market_cap_bucket": "Large cap"},
    {"symbol": "MELI", "company": "MercadoLibre", "sector": "Consumer Discretionary", "theme": "Latin America ecommerce", "region": "Latin America", "market_cap_bucket": "Large cap"},
    {"symbol": "NU", "company": "Nu Holdings", "sector": "Financials", "theme": "Latin America fintech", "region": "Brazil", "market_cap_bucket": "Large cap"},
    {"symbol": "SHOP", "company": "Shopify", "sector": "Technology", "theme": "Commerce software", "region": "Canada", "market_cap_bucket": "Large cap"},
    {"symbol": "SPOT", "company": "Spotify", "sector": "Communication Services", "theme": "Streaming platform", "region": "Sweden", "market_cap_bucket": "Large cap"},
    {"symbol": "NVO", "company": "Novo Nordisk", "sector": "Healthcare", "theme": "GLP-1 healthcare", "region": "Denmark", "market_cap_bucket": "Mega cap"},
    {"symbol": "BABA", "company": "Alibaba", "sector": "Consumer Discretionary", "theme": "China internet", "region": "China", "market_cap_bucket": "Large cap"},
    {"symbol": "PDD", "company": "PDD Holdings", "sector": "Consumer Discretionary", "theme": "China ecommerce", "region": "China", "market_cap_bucket": "Large cap"},
    {"symbol": "GRAB", "company": "Grab", "sector": "Technology", "theme": "Southeast Asia super app", "region": "Singapore", "market_cap_bucket": "Mid cap"},
]


ETF_ROWS = [
    {"symbol": "QQQ", "company": "Invesco QQQ", "sector": "ETF", "theme": "Large-cap growth", "region": "United States", "market_cap_bucket": "ETF"},
    {"symbol": "IWM", "company": "iShares Russell 2000 ETF", "sector": "ETF", "theme": "US small caps", "region": "United States", "market_cap_bucket": "ETF"},
    {"symbol": "SMH", "company": "VanEck Semiconductor ETF", "sector": "ETF", "theme": "Semiconductors", "region": "Global", "market_cap_bucket": "ETF"},
    {"symbol": "BOTZ", "company": "Global X Robotics & AI ETF", "sector": "ETF", "theme": "Robotics and AI", "region": "Global", "market_cap_bucket": "ETF"},
    {"symbol": "CIBR", "company": "First Trust Nasdaq Cybersecurity ETF", "sector": "ETF", "theme": "Cybersecurity", "region": "Global", "market_cap_bucket": "ETF"},
    {"symbol": "XBI", "company": "SPDR S&P Biotech ETF", "sector": "ETF", "theme": "Biotech", "region": "United States", "market_cap_bucket": "ETF"},
    {"symbol": "ITA", "company": "iShares US Aerospace & Defense ETF", "sector": "ETF", "theme": "Defense", "region": "United States", "market_cap_bucket": "ETF"},
    {"symbol": "ICLN", "company": "iShares Global Clean Energy ETF", "sector": "ETF", "theme": "Energy transition", "region": "Global", "market_cap_bucket": "ETF"},
]


IPO_RECENT_ROWS = [
    {"symbol": "RDDT", "company": "Reddit", "sector": "Communication Services", "theme": "Recent listing", "region": "United States", "market_cap_bucket": "Recent IPO"},
    {"symbol": "ARM", "company": "Arm Holdings", "sector": "Technology", "theme": "Recent listing", "region": "United Kingdom", "market_cap_bucket": "Recent IPO"},
    {"symbol": "CAVA", "company": "Cava Group", "sector": "Consumer Discretionary", "theme": "Recent listing", "region": "United States", "market_cap_bucket": "Recent IPO"},
    {"symbol": "TEM", "company": "Tempus AI", "sector": "Healthcare", "theme": "Recent listing", "region": "United States", "market_cap_bucket": "Recent IPO"},
]


def _with_metadata(rows, listing_type, source_name):
    output = []
    seen = set()
    for row in rows:
        symbol = str(row.get("symbol", "")).upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        output.append(
            {
                **row,
                "symbol": symbol,
                "listing_type": listing_type,
                "source": source_name,
                "source_url": "Local curated research seed; verify with exchange, SEC, and market-data sources.",
                "data_confidence_status": "Needs market-data check",
            }
        )
    return output


def build_opportunity_universe(scope="US_ADR", include_etfs=True, include_ipos=True):
    """Return a deduplicated US + ADR opportunity universe with metadata."""
    rows = []
    rows.extend(_with_metadata(US_ALL_CAP_ROWS, "US-listed equity", "Local all-cap opportunity seed"))
    if scope in {"US_ADR", "GLOBAL_ADR", "GLOBAL"}:
        rows.extend(_with_metadata(GLOBAL_ADR_ROWS, "US-listed ADR/global equity", "Local ADR opportunity seed"))
    if include_etfs:
        rows.extend(_with_metadata(ETF_ROWS, "ETF", "Local ETF theme seed"))
    if include_ipos:
        rows.extend(_with_metadata(IPO_RECENT_ROWS, "IPO/recent listing", "Local IPO/recent-listing seed"))

    deduped = {}
    for row in rows:
        symbol = row["symbol"]
        if symbol not in deduped:
            deduped[symbol] = row
        else:
            existing = deduped[symbol]
            existing["theme"] = existing.get("theme") or row.get("theme", "")
            if row.get("listing_type") == "IPO/recent listing":
                existing["listing_type"] = row["listing_type"]
                existing["market_cap_bucket"] = row.get("market_cap_bucket", existing.get("market_cap_bucket"))
    return list(deduped.values())


def get_opportunity_symbols(limit=None, scope="US_ADR", include_etfs=True, include_ipos=True):
    rows = build_opportunity_universe(scope=scope, include_etfs=include_etfs, include_ipos=include_ipos)
    return [row["symbol"] for row in rows[: limit or len(rows)]]

