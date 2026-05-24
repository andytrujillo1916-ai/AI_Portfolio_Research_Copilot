from datetime import datetime, timezone


def _parse_timestamp(value):
    if value is None or value == "":
        return None
    try:
        if hasattr(value, "to_pydatetime"):
            value = value.to_pydatetime()
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)
        text = str(value).replace("Z", "+00:00")
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return None


def evaluate_data_quality(data_result, max_age_hours=72):
    """Classify source/freshness quality for one market-data result."""
    data_result = data_result or {}
    source = str(data_result.get("source", "unknown"))
    error = data_result.get("error", "")
    is_fallback = bool(data_result.get("is_fallback", source == "mock"))
    timestamp = _parse_timestamp(data_result.get("last_timestamp"))
    issues = []

    if source == "mock" or is_fallback:
        issues.append("Using fallback/mock data.")
    if error:
        issues.append(f"Data fetch issue: {error}")
    if timestamp is None:
        issues.append("No last timestamp available.")

    age_hours = None
    if timestamp is not None:
        age_hours = (datetime.now(timezone.utc) - timestamp).total_seconds() / 3600
        if age_hours > max_age_hours:
            issues.append(f"Data may be stale ({age_hours:.1f} hours old).")

    if is_fallback or source == "mock":
        confidence = "Low"
        status = "Fallback"
    elif issues:
        confidence = "Medium"
        status = "Warning"
    else:
        confidence = "High"
        status = "Fresh"

    return {
        "source": source,
        "last_timestamp": timestamp.isoformat() if timestamp else "",
        "is_fallback": is_fallback,
        "is_stale": any("stale" in issue.lower() for issue in issues),
        "data_confidence": confidence,
        "status": status,
        "issues": issues,
    }


def summarize_data_sources(screened_assets=None, selected_snapshot=None, selected_price_data=None):
    """Summarize data-source health across selected asset and screened rows."""
    rows = []

    if selected_snapshot:
        quality = evaluate_data_quality(selected_snapshot)
        rows.append(
            {
                "symbol": selected_snapshot.get("symbol", "Selected"),
                "dataset": "snapshot",
                "source": quality["source"],
                "confidence": quality["data_confidence"],
                "status": quality["status"],
                "last_timestamp": quality["last_timestamp"],
                "issues": " | ".join(quality["issues"]),
            }
        )

    if selected_price_data:
        quality = evaluate_data_quality(selected_price_data)
        rows.append(
            {
                "symbol": selected_snapshot.get("symbol", "Selected") if selected_snapshot else "Selected",
                "dataset": "history",
                "source": quality["source"],
                "confidence": quality["data_confidence"],
                "status": quality["status"],
                "last_timestamp": quality["last_timestamp"],
                "issues": " | ".join(quality["issues"]),
            }
        )

    for asset in screened_assets or []:
        rows.append(
            {
                "symbol": asset.get("symbol", ""),
                "dataset": "screener",
                "source": asset.get("data_source", "unknown"),
                "confidence": asset.get("data_confidence", "Unknown"),
                "status": asset.get("data_quality_status", "Unknown"),
                "last_timestamp": asset.get("last_timestamp", ""),
                "issues": asset.get("data_issues", ""),
            }
        )

    fallback_count = sum(1 for row in rows if row.get("source") == "mock" or row.get("status") == "Fallback")
    warning_count = sum(1 for row in rows if row.get("status") in {"Warning", "Fallback"})
    confidence = "High" if warning_count == 0 else "Medium" if fallback_count == 0 else "Low"

    return {
        "rows": rows,
        "total_checks": len(rows),
        "fallback_count": fallback_count,
        "warning_count": warning_count,
        "overall_confidence": confidence,
        "summary": f"{len(rows)} data checks reviewed; {fallback_count} fallback/mock result(s), {warning_count} warning(s).",
    }
