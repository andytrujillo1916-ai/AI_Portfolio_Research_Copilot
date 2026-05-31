from data_quality_engine import evaluate_data_quality
from opportunistic_screener_engine import rank_opportunistic_stocks
from research_universe import get_default_research_watchlist, get_research_universe


def test_data_quality_flags_yfinance_as_high_confidence_when_timestamp_present():
    result = evaluate_data_quality(
        {
            "source": "yfinance",
            "last_timestamp": "2026-05-23T12:00:00+00:00",
            "is_fallback": False,
            "error": "",
        },
        max_age_hours=10_000,
    )
    assert result["data_confidence"] == "High"
    assert result["freshness_confidence"] == "High"
    assert result["source_trust"] == "Warning"
    assert result["is_fallback"] is False


def test_data_quality_flags_mock_as_low_confidence():
    result = evaluate_data_quality({"source": "mock", "error": "fallback used", "is_fallback": True})
    assert result["data_confidence"] == "Low"
    assert result["status"] == "Fallback"


def test_data_quality_flags_stale_data():
    result = evaluate_data_quality(
        {
            "source": "yfinance",
            "last_timestamp": "2020-01-01T00:00:00+00:00",
            "is_fallback": False,
        },
        max_age_hours=1,
    )
    assert result["is_stale"] is True
    assert result["data_confidence"] == "Medium"


def test_research_universe_returns_non_empty_stock_etf_groups():
    universe = get_research_universe()
    watchlist = get_default_research_watchlist()
    assert "Broad ETFs" in universe
    assert "Mega-Cap Tech" in universe
    assert len(watchlist) > 10


def test_opportunistic_screener_never_uses_execution_language():
    screened_assets = [
        {
            "symbol": "AAPL",
            "score": 80,
            "return_pct": 8,
            "volatility_pct": 18,
            "max_drawdown_pct": -8,
            "news_sentiment": "Bullish",
            "signal": "Watch",
            "regime": "Bull Trend",
            "data_confidence": "High",
            "data_source": "yfinance",
        }
    ]
    result = rank_opportunistic_stocks(screened_assets)
    labels = {row["opportunity_label"] for row in result["ranked_opportunities"]}
    forbidden = {"Buy", "Sell", "Guaranteed", "Execute"}
    assert labels.isdisjoint(forbidden)


def test_opportunistic_screener_accepts_partial_rows():
    result = rank_opportunistic_stocks([{"symbol": "BROKEN"}])
    assert len(result["ranked_opportunities"]) == 1
    assert result["ranked_opportunities"][0]["opportunity_label"] in {
        "Research Candidate",
        "Watch",
        "Avoid",
    }
