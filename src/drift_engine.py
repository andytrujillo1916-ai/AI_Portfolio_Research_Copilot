from csv import DictReader, DictWriter
from datetime import datetime
from pathlib import Path

from asset_sector_map import map_asset_to_sector

DATA_PATH = Path(__file__).resolve().parent.parent / "data"
SNAPSHOT_PATH = DATA_PATH / "watchlist_snapshots.csv"
SNAPSHOT_HEADERS = [
    "timestamp",
    "symbol",
    "score",
    "volatility_pct",
    "max_drawdown_pct",
    "regime",
    "news_sentiment",
    "opportunity_priority",
    "mapped_sector",
]


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _priority_from_score(score):
    if score >= 70:
        return "High"
    if score >= 50:
        return "Medium"
    return "Low"


def _ensure_snapshot_file():
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    if not SNAPSHOT_PATH.exists():
        with SNAPSHOT_PATH.open("w", newline="", encoding="utf-8") as file:
            writer = DictWriter(file, fieldnames=SNAPSHOT_HEADERS)
            writer.writeheader()


def save_watchlist_snapshot(screened_assets):
    """Save the current screener snapshot for future drift checks."""
    _ensure_snapshot_file()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    for asset in screened_assets or []:
        score = _safe_float(asset.get("score", 0.0))
        rows.append(
            {
                "timestamp": timestamp,
                "symbol": asset.get("symbol", ""),
                "score": score,
                "volatility_pct": _safe_float(asset.get("volatility_pct", 0.0)),
                "max_drawdown_pct": _safe_float(asset.get("max_drawdown_pct", 0.0)),
                "regime": asset.get("regime", "Unknown"),
                "news_sentiment": asset.get("news_sentiment", "Neutral"),
                "opportunity_priority": _priority_from_score(score),
                "mapped_sector": map_asset_to_sector(asset.get("symbol", "")),
            }
        )

    if not rows:
        return

    with SNAPSHOT_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = DictWriter(file, fieldnames=SNAPSHOT_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def load_previous_watchlist_snapshot():
    """Load the most recent saved watchlist snapshot rows."""
    _ensure_snapshot_file()
    with SNAPSHOT_PATH.open("r", newline="", encoding="utf-8") as file:
        return [row for row in DictReader(file)]


def _mode_thresholds(research_mode):
    if research_mode == "Conservative":
        return {"score_delta": 8, "vol_spike": 4.0, "drawdown_delta": 2.5}
    if research_mode == "Aggressive":
        return {"score_delta": 14, "vol_spike": 8.0, "drawdown_delta": 5.0}
    return {"score_delta": 10, "vol_spike": 6.0, "drawdown_delta": 3.5}


def _severity_label(score):
    if score >= 8:
        return "High"
    if score >= 4:
        return "Medium"
    return "Low"


def detect_watchlist_drift(
    screened_assets,
    prior_screened_assets=None,
    research_mode="Balanced",
):
    """Detect simple watchlist drift signals from current vs prior screener snapshots."""
    screened_assets = screened_assets or []
    prior_screened_assets = prior_screened_assets or []
    thresholds = _mode_thresholds(research_mode)

    prior_map = {row.get("symbol"): row for row in prior_screened_assets if row.get("symbol")}
    ranked_now = sorted(
        screened_assets,
        key=lambda row: _safe_float(row.get("score", 0.0)),
        reverse=True,
    )
    current_rank = {row.get("symbol"): idx + 1 for idx, row in enumerate(ranked_now)}
    prior_ranked = sorted(
        prior_screened_assets,
        key=lambda row: _safe_float(row.get("score", 0.0)),
        reverse=True,
    )
    prior_rank = {row.get("symbol"): idx + 1 for idx, row in enumerate(prior_ranked)}

    alerts = []
    stable_assets = []

    for asset in screened_assets:
        symbol = asset.get("symbol", "")
        score = _safe_float(asset.get("score", 0.0))
        vol = _safe_float(asset.get("volatility_pct", 0.0))
        drawdown = _safe_float(asset.get("max_drawdown_pct", 0.0))
        regime = str(asset.get("regime", "Unknown"))
        sentiment = str(asset.get("news_sentiment", "Neutral"))
        sector = map_asset_to_sector(symbol)

        prev = prior_map.get(symbol)
        asset_alerts = []

        if prev is None:
            asset_alerts.append(
                {
                    "symbol": symbol,
                    "drift_type": "New asset snapshot",
                    "severity": "Low",
                    "reasoning": "No prior snapshot found for this asset.",
                    "suggested_action": "Watch",
                }
            )
        else:
            prev_score = _safe_float(prev.get("score", 0.0))
            prev_vol = _safe_float(prev.get("volatility_pct", 0.0))
            prev_drawdown = _safe_float(prev.get("max_drawdown_pct", 0.0))
            prev_regime = str(prev.get("regime", "Unknown"))
            prev_sentiment = str(prev.get("news_sentiment", "Neutral"))

            score_delta = score - prev_score
            if abs(score_delta) >= thresholds["score_delta"]:
                sev_score = 6 if score_delta < 0 else 4
                asset_alerts.append(
                    {
                        "symbol": symbol,
                        "drift_type": "Signal score changed significantly",
                        "severity": _severity_label(sev_score),
                        "reasoning": f"Signal score moved from {prev_score:.2f} to {score:.2f}.",
                        "suggested_action": "Re-run Research" if score_delta < 0 else "Review",
                    }
                )

            vol_delta = vol - prev_vol
            if vol_delta >= thresholds["vol_spike"]:
                asset_alerts.append(
                    {
                        "symbol": symbol,
                        "drift_type": "Volatility spike",
                        "severity": _severity_label(8 if vol >= 30 else 6),
                        "reasoning": f"Volatility increased from {prev_vol:.2f}% to {vol:.2f}%.",
                        "suggested_action": "Reduce Confidence",
                    }
                )

            drawdown_delta = abs(drawdown) - abs(prev_drawdown)
            if drawdown_delta >= thresholds["drawdown_delta"]:
                asset_alerts.append(
                    {
                        "symbol": symbol,
                        "drift_type": "Drawdown deepened",
                        "severity": _severity_label(7 if abs(drawdown) >= 15 else 5),
                        "reasoning": f"Max drawdown moved from {prev_drawdown:.2f}% to {drawdown:.2f}%.",
                        "suggested_action": "Review",
                    }
                )

            if prev_regime == "Bull Trend" and regime in {"Bear Trend", "High Volatility"}:
                asset_alerts.append(
                    {
                        "symbol": symbol,
                        "drift_type": "Regime changed Bull to Bear/Volatile",
                        "severity": "High",
                        "reasoning": f"Regime changed from {prev_regime} to {regime}.",
                        "suggested_action": "Re-run Research",
                    }
                )

            if prev_sentiment in {"Bullish", "Neutral"} and sentiment == "Bearish":
                asset_alerts.append(
                    {
                        "symbol": symbol,
                        "drift_type": "News sentiment weakened",
                        "severity": "Medium",
                        "reasoning": f"News sentiment moved from {prev_sentiment} to {sentiment}.",
                        "suggested_action": "Review",
                    }
                )

            rank_now = current_rank.get(symbol, 0)
            rank_prev = prior_rank.get(symbol, 0)
            if rank_prev and rank_now and (rank_now - rank_prev) >= 3:
                asset_alerts.append(
                    {
                        "symbol": symbol,
                        "drift_type": "Opportunity rank fell sharply",
                        "severity": "Medium",
                        "reasoning": f"Rank changed from {rank_prev} to {rank_now}.",
                        "suggested_action": "Watch",
                    }
                )

            prev_sector = str(prev.get("mapped_sector", "Unknown"))
            if sector == "Unknown" or prev_sector == "Unknown":
                pass
            elif sector != prev_sector:
                asset_alerts.append(
                    {
                        "symbol": symbol,
                        "drift_type": "Sector context changed",
                        "severity": "Low",
                        "reasoning": f"Mapped sector changed from {prev_sector} to {sector}.",
                        "suggested_action": "Review",
                    }
                )

        if asset_alerts:
            alerts.extend(asset_alerts)
        else:
            stable_assets.append(symbol)

    alerts.sort(
        key=lambda row: {"High": 3, "Medium": 2, "Low": 1}.get(row.get("severity", "Low"), 1),
        reverse=True,
    )
    highest_priority_alert = alerts[0] if alerts else {}

    if not prior_screened_assets:
        summary = "No prior snapshot found. Current snapshot saved for future drift comparisons."
    elif alerts:
        summary = (
            f"Detected {len(alerts)} drift alerts across {len(screened_assets)} assets. "
            "Review high-severity changes first."
        )
    else:
        summary = "No major drift detected; watchlist appears stable versus prior snapshot."

    return {
        "alerts": alerts,
        "highest_priority_alert": highest_priority_alert,
        "stable_assets": stable_assets,
        "summary": summary,
    }
