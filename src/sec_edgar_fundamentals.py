SEC_USER_AGENT = "AI Portfolio Research Copilot research-only contact@example.com"
SEC_TICKER_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"


def _safe_float(value, default=None):
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _latest_values(facts, tag):
    units = facts.get("facts", {}).get("us-gaap", {}).get(tag, {}).get("units", {})
    rows = []
    for unit_rows in units.values():
        for row in unit_rows:
            if row.get("val") is None or not row.get("fy"):
                continue
            rows.append(row)
    rows.sort(key=lambda row: (row.get("fy", 0), row.get("filed", "")), reverse=True)
    return rows


def _period_value(facts, tag, offset=0):
    rows = _latest_values(facts, tag)
    if len(rows) <= offset:
        return None
    return _safe_float(rows[offset].get("val"))


def _trend(current, previous, threshold_pct=5.0):
    if current is None or previous in (None, 0):
        return ""
    pct = ((current - previous) / abs(previous)) * 100
    if pct >= threshold_pct:
        return "Improving"
    if pct <= -threshold_pct:
        return "Deteriorating"
    return "Stable"


def _revenue_growth(facts):
    current = _period_value(facts, "Revenues")
    previous = _period_value(facts, "Revenues", offset=1)
    if current is None:
        current = _period_value(facts, "RevenueFromContractWithCustomerExcludingAssessedTax")
        previous = _period_value(facts, "RevenueFromContractWithCustomerExcludingAssessedTax", offset=1)
    if current is None or previous in (None, 0):
        return None
    return round(((current - previous) / abs(previous)) * 100, 2)


def extract_sec_fundamental_context(facts):
    """Extract lightweight scoring inputs from SEC companyfacts JSON."""
    if not facts:
        return {
            "recent_filing_status": "Not connected",
            "source": "sec_edgar",
            "data_confidence": "Low",
            "limitations": ["SEC company facts were unavailable."],
        }

    revenue_growth = _revenue_growth(facts)
    net_income_current = _period_value(facts, "NetIncomeLoss")
    net_income_previous = _period_value(facts, "NetIncomeLoss", offset=1)
    debt_current = _period_value(facts, "LongTermDebtCurrent")
    debt_previous = _period_value(facts, "LongTermDebtCurrent", offset=1)
    shares_current = _period_value(facts, "CommonStocksIncludingAdditionalPaidInCapital")
    shares_previous = _period_value(facts, "CommonStocksIncludingAdditionalPaidInCapital", offset=1)

    dilution_risk = ""
    if shares_current is not None and shares_previous not in (None, 0):
        dilution_change = ((shares_current - shares_previous) / abs(shares_previous)) * 100
        if dilution_change >= 10:
            dilution_risk = "High"

    return {
        "revenue_growth_pct": revenue_growth,
        "profitability_trend": _trend(net_income_current, net_income_previous),
        "debt_trend": "Rising" if _trend(debt_current, debt_previous) == "Improving" else "Falling" if _trend(debt_current, debt_previous) == "Deteriorating" else "",
        "dilution_risk": dilution_risk,
        "recent_filing_status": "Connected",
        "source": "sec_edgar",
        "data_confidence": "Medium",
        "limitations": [
            "SEC companyfacts coverage varies by filer and taxonomy tag.",
            "This is fundamental context only, not a valuation model.",
        ],
    }


def fetch_sec_company_facts(symbol, timeout=8):
    """Fetch SEC companyfacts for a ticker; return {} on network/provider failure."""
    symbol = str(symbol or "").upper().strip()
    if not symbol:
        return {}
    try:
        import requests

        headers = {"User-Agent": SEC_USER_AGENT}
        ticker_response = requests.get(SEC_TICKER_URL, headers=headers, timeout=timeout)
        ticker_response.raise_for_status()
        tickers = ticker_response.json()
        cik = None
        for row in tickers.values():
            if str(row.get("ticker", "")).upper() == symbol:
                cik = str(row.get("cik_str", "")).zfill(10)
                break
        if not cik:
            return {}
        facts_response = requests.get(
            SEC_COMPANY_FACTS_URL.format(cik=cik),
            headers=headers,
            timeout=timeout,
        )
        facts_response.raise_for_status()
        return facts_response.json()
    except Exception:
        return {}


def get_sec_fundamental_context(symbol):
    """Fetch and summarize free official SEC company-facts context when available."""
    return extract_sec_fundamental_context(fetch_sec_company_facts(symbol))
