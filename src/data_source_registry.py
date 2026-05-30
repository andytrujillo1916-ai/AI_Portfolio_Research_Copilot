DATA_SOURCES = {
    "yfinance": {
        "provider": "Yahoo Finance via yfinance",
        "source_type": "Free unofficial market-data wrapper",
        "source_url": "https://pypi.org/project/yfinance/",
        "recommended_use": "Research price history and snapshots only.",
        "trust_level": "Warning",
        "notes": "Useful free source, but not an official exchange feed.",
    },
    "sec_edgar": {
        "provider": "SEC EDGAR APIs",
        "source_type": "Official public filings and company facts",
        "source_url": "https://www.sec.gov/edgar/sec-api-documentation",
        "recommended_use": "Company filings, facts, and disclosure research.",
        "trust_level": "Trusted",
        "notes": "Requires fair-access behavior and a descriptive User-Agent for requests.",
    },
    "mock": {
        "provider": "Local fallback mock data",
        "source_type": "Generated fallback",
        "source_url": "",
        "recommended_use": "UI continuity only; never for buy/sell recommendations.",
        "trust_level": "Blocked",
        "notes": "Fallback data means the live data source failed or is unavailable.",
    },
    "manual": {
        "provider": "User-entered portfolio/profile data",
        "source_type": "Manual local input",
        "source_url": "",
        "recommended_use": "Suitability and portfolio context after user review.",
        "trust_level": "Warning",
        "notes": "Accuracy depends on the user's entries.",
    },
    "local_universe": {
        "provider": "Local opportunity universe seed",
        "source_type": "Manual/local research universe metadata",
        "source_url": "",
        "recommended_use": "Universe discovery only; must be confirmed with market data before recommendations.",
        "trust_level": "Warning",
        "notes": "Symbols and themes are local research seeds, not official buy lists.",
    },
    "nasdaq_ipo_calendar": {
        "provider": "Nasdaq IPO calendar",
        "source_type": "Public IPO calendar/reference",
        "source_url": "https://www.nasdaq.com/market-activity/ipos",
        "recommended_use": "IPO and recent-listing research context only.",
        "trust_level": "Warning",
        "notes": "Expected IPO dates can change and should be verified before use.",
    },
    "exchange_listing_metadata": {
        "provider": "NYSE/Nasdaq listing metadata",
        "source_type": "Public exchange/listing reference",
        "source_url": "",
        "recommended_use": "Listing status, ADR, and exchange metadata research.",
        "trust_level": "Warning",
        "notes": "Use as classification support; market-data gates still decide action eligibility.",
    },
    "future_paid_market_data": {
        "provider": "Future paid market-data adapter",
        "source_type": "Optional paid provider slot",
        "source_url": "",
        "recommended_use": "Future higher-confidence market/fundamental/news data integration.",
        "trust_level": "Warning",
        "notes": "Placeholder for providers such as Polygon, IEX, FMP, Quiver, or Benzinga.",
    },
}


def get_data_source_metadata(source):
    """Return source metadata used for data-quality and recommendation gating."""
    return DATA_SOURCES.get(
        str(source or "unknown"),
        {
            "provider": str(source or "Unknown"),
            "source_type": "Unknown",
            "source_url": "",
            "recommended_use": "Research only until source is verified.",
            "trust_level": "Warning",
            "notes": "Unknown source; treat as lower confidence.",
        },
    )


def list_data_sources():
    return [{"source": key, **value} for key, value in DATA_SOURCES.items()]
