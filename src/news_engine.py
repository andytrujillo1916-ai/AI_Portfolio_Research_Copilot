"""News intelligence engine for event-aware research context.

This module provides a simple yfinance-backed news fetcher and a rule-based
context generator that can be replaced later with a more advanced NLP stack.
All outputs are research context only — not trading signals or advice.
"""

from typing import List, Dict
import datetime
from dateutil import parser as date_parser


def get_recent_news(symbol: str, limit: int = 5) -> List[Dict]:
    """Return recent news items for `symbol` using yfinance if available.

    Each item is a dict with keys: title, publisher, link, publish_time
    If no news or yfinance is unavailable, returns an empty list.
    """
    try:
        import yfinance as yf
    except Exception:
        return []

    try:
        t = yf.Ticker(symbol)
        raw = getattr(t, "news", None)
        if not raw:
            return []

        def get_nested(obj, *keys):
            """Try to get nested keys from dict-like or object-like structures."""
            cur = obj
            for k in keys:
                if cur is None:
                    return None
                # dict-like
                if isinstance(cur, dict):
                    cur = cur.get(k)
                else:
                    cur = getattr(cur, k, None)
            return cur

        items = []
        for n in raw[:limit]:
            # Title candidates
            title = (
                get_nested(n, "title")
                or get_nested(n, "headline")
                or get_nested(n, "summary")
                or get_nested(n, "content", "title")
                or get_nested(n, "content", "headline")
                or get_nested(n, "content", "summary")
                or ""
            )

            # Publisher candidates
            publisher = (
                get_nested(n, "publisher")
                or get_nested(n, "source")
                or get_nested(n, "provider", "name")
                or get_nested(n, "provider", "displayName")
                or get_nested(n, "content", "provider", "displayName")
                or ""
            )

            # Link candidates
            link = (
                get_nested(n, "link")
                or get_nested(n, "url")
                or get_nested(n, "content", "clickThroughUrl", "url")
                or get_nested(n, "content", "clickThroughUrl")
                or ""
            )

            # Publish time candidates
            publish_time = (
                get_nested(n, "providerPublishTime")
                or get_nested(n, "pubDate")
                or get_nested(n, "content", "pubDate")
                or get_nested(n, "publish_time")
                or get_nested(n, "date")
                or ""
            )

            # Normalize publish_time to datetime when possible
            if publish_time:
                try:
                    # integer epoch
                    if isinstance(publish_time, (int, float)):
                        publish_time = datetime.datetime.fromtimestamp(int(publish_time))
                    else:
                        # try parsing string
                        publish_time = date_parser.parse(str(publish_time))
                except Exception:
                    # leave as-is (string) if parsing fails
                    pass

            # Clean fallbacks
            if not title:
                title = "Untitled headline"
            if not publisher:
                publisher = "Unknown publisher"
            if not link:
                link = ""
            if not publish_time:
                publish_time = ""

            items.append({
                "title": title,
                "publisher": publisher,
                "link": link,
                "publish_time": publish_time,
                "raw": n,
            })

        return items
    except Exception:
        return []


def generate_news_context(symbol: str) -> Dict:
    """Generate news-aware research context for a symbol.

    Uses `get_recent_news` to prefer real headlines when available, with a
    simple rule-based fallback when no headlines exist.
    """
    normalized = symbol.lower()
    news = get_recent_news(symbol)

    # Basic keyword lists for tagging and risk flags
    tag_keywords = [
        "earnings",
        "ai",
        "rates",
        "inflation",
        "regulation",
        "product",
        "lawsuit",
        "analyst",
        "guidance",
    ]
    risk_keywords = ["lawsuit", "regulation", "downgrade", "miss", "investigation"]

    if news:
        # Headline summary: concatenate top 3 titles in a readable sentence
        top_titles = [n.get("title", "") for n in news[:3] if n.get("title")]
        if top_titles:
            headline_summary = " | ".join(top_titles)
        else:
            headline_summary = f"Recent headlines available for {symbol}."

        # Simple rule-based sentiment: neutral unless obvious keywords present
        joined = " ".join([t.get("title", "") for t in news]).lower()
        sentiment = "Neutral"
        if any(w in joined for w in ["beat", "beats", "upgrade", "outperform", "surge", "record"]):
            sentiment = "Bullish"
        elif any(w in joined for w in ["miss", "downgrade", "loss", "fall", "investigation", "lawsuit"]):
            sentiment = "Bearish"

        # Event tags inferred from keywords in titles
        event_tags = []
        for kw in tag_keywords:
            if kw in joined:
                event_tags.append(kw)

        # Risk flags from matching risk keywords
        risk_flags = []
        for rk in risk_keywords:
            if rk in joined:
                risk_flags.append(f"Mention of {rk} in recent headlines.")

        return {
            "headline_summary": headline_summary,
            "market_sentiment": sentiment,
            "event_tags": event_tags or ["headline_monitoring"],
            "risk_flags": risk_flags,
            "recent_headlines": news,
        }

    # Fallback: previous mock behavior kept simple and student-readable
    sentiment = "Neutral"
    event_tags = ["event_calendar", "headline_monitoring"]
    risk_flags = []

    if any(keyword in normalized for keyword in ["aapl", "msft", "goog", "nvda", "tech"]):
        headline_summary = (
            f"{symbol} is in focus ahead of expected sector news and earnings commentary."
        )
        sentiment = "Bullish"
        event_tags = ["earnings", "product_launch", "sector_momentum"]
        risk_flags = ["Expect higher information flow around earnings and guidance."]
    elif any(keyword in normalized for keyword in ["xom", "cvx", "oil", "energy"]):
        headline_summary = (
            f"{symbol} is tracking commodity and policy headlines that could affect energy demand."
        )
        sentiment = "Neutral"
        event_tags = ["commodity", "macro_policy", "supply_chain"]
        risk_flags = ["Geopolitical or OPEC news may drive short-term volatility."]
    elif any(keyword in normalized for keyword in ["btc", "eth", "crypto"]):
        headline_summary = (
            f"{symbol} is sensitive to macro commentary and regulatory headlines in the crypto sector."
        )
        sentiment = "Bearish"
        event_tags = ["regulation", "macro_data", "digital_assets"]
        risk_flags = ["Regulatory headlines can quickly shift sentiment."]
    else:
        headline_summary = (
            f"{symbol} has limited public events right now, but keep monitoring broader market drivers."
        )
        sentiment = "Neutral"
        event_tags = ["economic_data", "company_updates"]
        risk_flags = ["Lack of strong news means research should stay cautious."]

    return {
        "headline_summary": headline_summary,
        "market_sentiment": sentiment,
        "event_tags": event_tags,
        "risk_flags": risk_flags,
        "recent_headlines": [],
    }
