from datetime import datetime
from pathlib import Path
import csv


EXPERIMENT_HEADERS = [
    "date",
    "experiment_name",
    "experiment_type",
    "description",
    "changed_modules",
    "hypothesis",
    "metrics_before",
    "metrics_after",
    "result",
    "lesson",
    "status",
]


def _csv_path(path=None):
    if path:
        return Path(path)
    return Path(__file__).resolve().parent.parent / "data" / "experiments.csv"


def _ensure_storage(path=None):
    target = _csv_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        with target.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=EXPERIMENT_HEADERS)
            writer.writeheader()
    return target


def load_experiments(path=None):
    """Load experiment tracking rows from CSV storage."""
    target = _ensure_storage(path)
    rows = []
    with target.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            normalized = {key: str(row.get(key, "")) for key in EXPERIMENT_HEADERS}
            rows.append(normalized)
    rows.sort(key=lambda row: row.get("date", ""), reverse=True)
    return rows


def save_experiment(
    experiment_name,
    experiment_type,
    description,
    changed_modules,
    hypothesis,
    metrics_before="",
    metrics_after="",
    result="Pending",
    lesson="",
    status="Planned",
    path=None,
):
    """Save a new experiment row to CSV storage."""
    target = _ensure_storage(path)
    row = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "experiment_name": str(experiment_name),
        "experiment_type": str(experiment_type),
        "description": str(description),
        "changed_modules": str(changed_modules),
        "hypothesis": str(hypothesis),
        "metrics_before": str(metrics_before),
        "metrics_after": str(metrics_after),
        "result": str(result),
        "lesson": str(lesson),
        "status": str(status),
    }
    with target.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=EXPERIMENT_HEADERS)
        writer.writerow(row)
    return row


def update_experiment_result(
    experiment_name,
    result,
    lesson,
    status="Completed",
    metrics_after="",
    path=None,
):
    """Update the most recent matching experiment entry by name."""
    target = _ensure_storage(path)
    rows = load_experiments(path)
    if not rows:
        return None

    updated = None
    for row in rows:
        if row.get("experiment_name") == experiment_name:
            row["result"] = str(result)
            row["lesson"] = str(lesson)
            row["status"] = str(status)
            if metrics_after:
                row["metrics_after"] = str(metrics_after)
            updated = row
            break

    if updated is None:
        return None

    # Persist in chronological order to keep file append-friendly when reloaded.
    rows_sorted_oldest_first = sorted(rows, key=lambda item: item.get("date", ""))
    with target.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=EXPERIMENT_HEADERS)
        writer.writeheader()
        writer.writerows(rows_sorted_oldest_first)
    return updated


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_metrics_input(metrics):
    """Parse metrics from dict or 'k=v, k=v' string format."""
    keys = [
        "win_rate",
        "avg_return",
        "avg_alpha",
        "max_drawdown",
        "consistency_score",
    ]

    if isinstance(metrics, dict):
        parsed = {}
        for key in keys:
            parsed[key] = _safe_float(metrics.get(key))
        return parsed

    if isinstance(metrics, str):
        parsed = {key: None for key in keys}
        parts = [part.strip() for part in metrics.split(",") if part.strip()]
        for part in parts:
            if "=" not in part:
                continue
            raw_key, raw_value = part.split("=", 1)
            key = raw_key.strip().lower()
            value = _safe_float(raw_value.strip())
            if key in parsed:
                parsed[key] = value
        return parsed

    return {key: None for key in keys}


def compare_experiment_results(metrics_before, metrics_after):
    """Compare key performance metrics and classify experiment outcome."""
    before = _parse_metrics_input(metrics_before)
    after = _parse_metrics_input(metrics_after)

    improved = []
    worsened = []

    higher_is_better = {"win_rate", "avg_return", "avg_alpha", "consistency_score"}
    lower_is_better = {"max_drawdown"}

    for metric in ["win_rate", "avg_return", "avg_alpha", "max_drawdown", "consistency_score"]:
        before_value = before.get(metric)
        after_value = after.get(metric)
        if before_value is None or after_value is None:
            continue

        if metric in higher_is_better:
            if after_value > before_value:
                improved.append(f"{metric}: {before_value:.2f} -> {after_value:.2f}")
            elif after_value < before_value:
                worsened.append(f"{metric}: {before_value:.2f} -> {after_value:.2f}")
        elif metric in lower_is_better:
            # For drawdown, closer to zero (less negative) is improvement.
            if after_value > before_value:
                improved.append(f"{metric}: {before_value:.2f} -> {after_value:.2f}")
            elif after_value < before_value:
                worsened.append(f"{metric}: {before_value:.2f} -> {after_value:.2f}")

    if not improved and not worsened:
        overall = "Inconclusive"
    elif improved and not worsened:
        overall = "Improved"
    elif worsened and not improved:
        overall = "Worse"
    else:
        overall = "Mixed"

    summary = (
        f"Comparison result: {overall}. "
        f"Improved metrics: {len(improved)} | Worsened metrics: {len(worsened)}."
    )

    return {
        "improved_metrics": improved,
        "worsened_metrics": worsened,
        "overall_result": overall,
        "summary": summary,
    }
