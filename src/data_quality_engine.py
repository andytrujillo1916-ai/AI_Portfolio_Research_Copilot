from datetime import datetime, timezone

from data_source_registry import get_data_source_metadata


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
    metadata = get_data_source_metadata(source)
    error = data_result.get("error", "")
    is_fallback = bool(data_result.get("is_fallback", source == "mock"))
    timestamp = _parse_timestamp(data_result.get("last_timestamp"))
    data_payload = data_result.get("data", data_result)
    issues = []
    missing_fields = []

    if source == "mock" or is_fallback:
        issues.append("Using fallback/mock data.")
    if error:
        issues.append(f"Data fetch issue: {error}")
    if timestamp is None:
        issues.append("No last timestamp available.")
    has_explicit_payload = any(key in data_result for key in {"data", "price", "Close", "symbol"})
    if has_explicit_payload and isinstance(data_payload, dict) and not data_payload.get("Close") and "price" not in data_payload:
        missing_fields.append("price_or_close")
    if hasattr(data_payload, "empty") and data_payload.empty:
        missing_fields.append("price_history")
    if missing_fields:
        issues.append(f"Missing required field(s): {', '.join(missing_fields)}.")

    age_hours = None
    if timestamp is not None:
        age_hours = (datetime.now(timezone.utc) - timestamp).total_seconds() / 3600
        if age_hours > max_age_hours:
            issues.append(f"Data may be stale ({age_hours:.1f} hours old).")

    if is_fallback or source == "mock" or missing_fields:
        confidence = "Low"
        status = "Fallback"
    elif issues:
        confidence = "Medium"
        status = "Warning"
    else:
        confidence = "High"
        status = "Fresh"

    if is_fallback or source == "mock" or missing_fields:
        recommendation_gate = "Blocked"
    elif status == "Warning" or metadata.get("trust_level") == "Warning":
        recommendation_gate = "Warning"
    else:
        recommendation_gate = "Trusted"

    return {
        "source": source,
        "provider": metadata.get("provider", source),
        "source_url": metadata.get("source_url", ""),
        "source_type": metadata.get("source_type", "Unknown"),
        "source_trust": metadata.get("trust_level", "Warning"),
        "freshness_confidence": confidence,
        "allowed_use": "display_only"
        if recommendation_gate == "Blocked"
        else "research_and_recommendation"
        if recommendation_gate == "Trusted"
        else "research_only",
        "last_timestamp": timestamp.isoformat() if timestamp else "",
        "is_fallback": is_fallback,
        "is_stale": any("stale" in issue.lower() for issue in issues),
        "missing_fields": missing_fields,
        "data_confidence": confidence,
        "status": status,
        "recommendation_gate": recommendation_gate,
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
                "provider": quality["provider"],
                "source_trust": quality.get("source_trust", "Warning"),
                "freshness_confidence": quality.get("freshness_confidence", quality["data_confidence"]),
                "confidence": quality["data_confidence"],
                "status": quality["status"],
                "recommendation_gate": quality["recommendation_gate"],
                "allowed_use": quality.get("allowed_use", "research_only"),
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
                "provider": quality["provider"],
                "source_trust": quality.get("source_trust", "Warning"),
                "freshness_confidence": quality.get("freshness_confidence", quality["data_confidence"]),
                "confidence": quality["data_confidence"],
                "status": quality["status"],
                "recommendation_gate": quality["recommendation_gate"],
                "allowed_use": quality.get("allowed_use", "research_only"),
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
                "provider": asset.get("data_provider", asset.get("data_source", "unknown")),
                "source_trust": asset.get("source_trust", "Warning"),
                "freshness_confidence": asset.get("freshness_confidence", asset.get("data_confidence", "Unknown")),
                "confidence": asset.get("data_confidence", "Unknown"),
                "status": asset.get("data_quality_status", "Unknown"),
                "recommendation_gate": asset.get("recommendation_gate", "Warning"),
                "allowed_use": asset.get("allowed_use", "research_only"),
                "last_timestamp": asset.get("last_timestamp", ""),
                "issues": asset.get("data_issues", ""),
            }
        )

    fallback_count = sum(1 for row in rows if row.get("source") == "mock" or row.get("status") == "Fallback")
    warning_count = sum(1 for row in rows if row.get("status") in {"Warning", "Fallback"})
    blocked_count = sum(1 for row in rows if row.get("recommendation_gate") == "Blocked")
    confidence = "High" if warning_count == 0 else "Medium" if fallback_count == 0 else "Low"

    return {
        "rows": rows,
        "total_checks": len(rows),
        "fallback_count": fallback_count,
        "warning_count": warning_count,
        "blocked_count": blocked_count,
        "overall_confidence": confidence,
        "summary": (
            f"{len(rows)} data checks reviewed; {fallback_count} fallback/mock result(s), "
            f"{warning_count} warning(s), {blocked_count} blocked recommendation gate(s)."
        ),
    }
