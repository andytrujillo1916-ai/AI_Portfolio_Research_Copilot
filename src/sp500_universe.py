SP500_STYLE_UNIVERSE = [
    {"symbol": "AAPL", "company": "Apple", "sector": "Technology"},
    {"symbol": "MSFT", "company": "Microsoft", "sector": "Technology"},
    {"symbol": "NVDA", "company": "NVIDIA", "sector": "Technology"},
    {"symbol": "GOOGL", "company": "Alphabet", "sector": "Communication Services"},
    {"symbol": "META", "company": "Meta Platforms", "sector": "Communication Services"},
    {"symbol": "AMZN", "company": "Amazon", "sector": "Consumer Discretionary"},
    {"symbol": "AVGO", "company": "Broadcom", "sector": "Technology"},
    {"symbol": "TSLA", "company": "Tesla", "sector": "Consumer Discretionary"},
    {"symbol": "JPM", "company": "JPMorgan Chase", "sector": "Financials"},
    {"symbol": "LLY", "company": "Eli Lilly", "sector": "Healthcare"},
    {"symbol": "UNH", "company": "UnitedHealth Group", "sector": "Healthcare"},
    {"symbol": "V", "company": "Visa", "sector": "Financials"},
    {"symbol": "MA", "company": "Mastercard", "sector": "Financials"},
    {"symbol": "XOM", "company": "Exxon Mobil", "sector": "Energy"},
    {"symbol": "COST", "company": "Costco", "sector": "Consumer Staples"},
    {"symbol": "WMT", "company": "Walmart", "sector": "Consumer Staples"},
    {"symbol": "PG", "company": "Procter & Gamble", "sector": "Consumer Staples"},
    {"symbol": "JNJ", "company": "Johnson & Johnson", "sector": "Healthcare"},
    {"symbol": "HD", "company": "Home Depot", "sector": "Consumer Discretionary"},
    {"symbol": "BAC", "company": "Bank of America", "sector": "Financials"},
    {"symbol": "KO", "company": "Coca-Cola", "sector": "Consumer Staples"},
    {"symbol": "PEP", "company": "PepsiCo", "sector": "Consumer Staples"},
    {"symbol": "MRK", "company": "Merck", "sector": "Healthcare"},
    {"symbol": "ABBV", "company": "AbbVie", "sector": "Healthcare"},
    {"symbol": "CVX", "company": "Chevron", "sector": "Energy"},
    {"symbol": "CRM", "company": "Salesforce", "sector": "Technology"},
    {"symbol": "AMD", "company": "Advanced Micro Devices", "sector": "Technology"},
    {"symbol": "NFLX", "company": "Netflix", "sector": "Communication Services"},
    {"symbol": "ADBE", "company": "Adobe", "sector": "Technology"},
    {"symbol": "TMO", "company": "Thermo Fisher Scientific", "sector": "Healthcare"},
    {"symbol": "MCD", "company": "McDonald's", "sector": "Consumer Discretionary"},
    {"symbol": "CSCO", "company": "Cisco", "sector": "Technology"},
    {"symbol": "ACN", "company": "Accenture", "sector": "Information Technology"},
    {"symbol": "ABT", "company": "Abbott Laboratories", "sector": "Healthcare"},
    {"symbol": "LIN", "company": "Linde", "sector": "Materials"},
    {"symbol": "DIS", "company": "Walt Disney", "sector": "Communication Services"},
    {"symbol": "WFC", "company": "Wells Fargo", "sector": "Financials"},
    {"symbol": "PM", "company": "Philip Morris International", "sector": "Consumer Staples"},
    {"symbol": "TXN", "company": "Texas Instruments", "sector": "Technology"},
    {"symbol": "NEE", "company": "NextEra Energy", "sector": "Utilities"},
    {"symbol": "RTX", "company": "RTX", "sector": "Industrials"},
    {"symbol": "QCOM", "company": "Qualcomm", "sector": "Technology"},
    {"symbol": "INTU", "company": "Intuit", "sector": "Technology"},
    {"symbol": "IBM", "company": "IBM", "sector": "Technology"},
    {"symbol": "AMGN", "company": "Amgen", "sector": "Healthcare"},
    {"symbol": "GS", "company": "Goldman Sachs", "sector": "Financials"},
    {"symbol": "CAT", "company": "Caterpillar", "sector": "Industrials"},
    {"symbol": "GE", "company": "GE Aerospace", "sector": "Industrials"},
    {"symbol": "SPY", "company": "SPDR S&P 500 ETF", "sector": "Broad ETF"},
    {"symbol": "VOO", "company": "Vanguard S&P 500 ETF", "sector": "Broad ETF"},
]


def get_sp500_style_universe(limit=None):
    """Return a local S&P 500-style universe with source metadata."""
    rows = []
    for row in SP500_STYLE_UNIVERSE[: limit or len(SP500_STYLE_UNIVERSE)]:
        rows.append(
            {
                **row,
                "universe": "S&P 500-style local universe",
                "source": "Local curated seed list",
                "source_url": "https://www.spglobal.com/spdji/en/indices/equity/sp-500/",
            }
        )
    return rows


def get_sp500_style_symbols(limit=None):
    return [row["symbol"] for row in get_sp500_style_universe(limit=limit)]
