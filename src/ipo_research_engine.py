IPO_SEED_ROWS = [
    {
        "company": "Databricks",
        "symbol": "",
        "ipo_status": "Rumored / private",
        "expected_date": "Unknown",
        "exchange": "NASDAQ expected",
        "sector": "Data infrastructure",
        "filing_link": "",
        "deal_status": "No public S-1 in local data",
    },
    {
        "company": "Stripe",
        "symbol": "",
        "ipo_status": "Rumored / private",
        "expected_date": "Unknown",
        "exchange": "NYSE/NASDAQ expected",
        "sector": "Payments",
        "filing_link": "",
        "deal_status": "No public S-1 in local data",
    },
    {
        "company": "Recent IPO Watchlist",
        "symbol": "RDDT",
        "ipo_status": "Listed / recent IPO watch",
        "expected_date": "Listed",
        "exchange": "NYSE",
        "sector": "Social media",
        "filing_link": "https://www.sec.gov/edgar/search/",
        "deal_status": "Eligible for normal scoring only if data quality passes",
    },
]


def generate_ipo_research_context(symbol_or_company=None, ipo_rows=None):
    """Score IPOs as research-only opportunities until listing/data gates pass."""
    query = str(symbol_or_company or "").upper().strip()
    rows = ipo_rows or IPO_SEED_ROWS
    results = []

    for row in rows:
        symbol = str(row.get("symbol", "")).upper()
        company = str(row.get("company", ""))
        if query and query not in symbol and query not in company.upper():
            continue

        listed = "listed" in str(row.get("ipo_status", "")).lower() and bool(symbol)
        filing_quality = 30 if row.get("filing_link") else 10
        sector_theme = 20 if row.get("sector") not in {"", "Unknown"} else 10
        post_listing_data = 25 if listed else 0
        risk_penalty = 15 if not listed else 5
        score = max(0, min(100, filing_quality + sector_theme + post_listing_data - risk_penalty + 35))

        limitations = [
            "IPO dates are often estimates and may change.",
            "S-1/F-1 filings are research inputs, not investment guarantees.",
            "Pre-IPO names cannot be traded in this app.",
            "Post-listing IPOs need enough price history before buy/add/sell actions.",
        ]
        risk_flags = [
            "Limited trading history.",
            "Potential lockup, dilution, and valuation risk.",
        ]
        if not listed:
            risk_flags.append("Not publicly listed in local data; research-only watch.")

        results.append(
            {
                **row,
                "research_priority_score": score,
                "research_only": not listed,
                "post_listing_data_available": listed,
                "positive_factors": [
                    f"Sector/theme tracked: {row.get('sector', 'Unknown')}.",
                    "Can be reviewed against SEC EDGAR filings when available.",
                ],
                "risk_flags": risk_flags,
                "data_limitations": limitations,
                "summary": (
                    f"{company or symbol} IPO context is research-only"
                    if not listed
                    else f"{company or symbol} is listed but still carries recent-IPO risk."
                ),
            }
        )

    if not results and query:
        return {
            "ipo_candidates": [],
            "selected_ipo": {},
            "summary": f"No IPO research row found for {symbol_or_company}.",
        }

    selected = results[0] if results else {}
    return {
        "ipo_candidates": sorted(results, key=lambda item: item.get("research_priority_score", 0), reverse=True),
        "selected_ipo": selected,
        "summary": f"IPO research reviewed {len(results)} row(s). IPOs stay research-only until listed and data quality passes.",
    }
