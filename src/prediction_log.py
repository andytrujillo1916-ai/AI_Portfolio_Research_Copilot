from csv import DictReader, DictWriter
from datetime import datetime
from pathlib import Path

from evaluation_engine import evaluate_prediction

DATA_PATH = Path(__file__).resolve().parent.parent / "data"
CSV_PATH = DATA_PATH / "prediction_log.csv"
HEADERS = [
    "date",
    "symbol",
    "signal",
    "score",
    "reasons",
    "risks",
    "price_at_signal",
    "time_horizon",
    "outcome",
    "lesson",
]


def _ensure_file():
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
            writer = DictWriter(file, fieldnames=HEADERS)
            writer.writeheader()


def load_predictions():
    """Load prediction log entries from CSV."""
    _ensure_file()
    with CSV_PATH.open("r", newline="", encoding="utf-8") as file:
        return [row for row in DictReader(file)]


def add_prediction(
    symbol,
    signal,
    score,
    reasons,
    risks,
    price_at_signal,
    time_horizon="",
    outcome="",
    lesson="",
):
    """Add a new prediction log entry."""
    _ensure_file()
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "signal": signal,
        "score": str(score),
        "reasons": " | ".join(reasons),
        "risks": " | ".join(risks),
        "price_at_signal": str(price_at_signal),
        "time_horizon": time_horizon,
        "outcome": outcome,
        "lesson": lesson,
    }
    with CSV_PATH.open("a", newline="", encoding="utf-8") as file:
        writer = DictWriter(file, fieldnames=HEADERS)
        writer.writerow(entry)
    return entry


def update_prediction_outcome(index, outcome, lesson):
    """Update the outcome and lesson for an existing prediction entry."""
    entries = load_predictions()
    if index < 0 or index >= len(entries):
        raise IndexError("Prediction entry index out of range")
    entries[index]["outcome"] = outcome
    entries[index]["lesson"] = lesson
    with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = DictWriter(file, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(entries)
    return entries[index]


def evaluate_all_predictions(symbol, current_price):
    """Evaluate saved predictions for one symbol against the current price."""
    entries = load_predictions()
    evaluated_predictions = []
    for entry in entries:
        if entry.get("symbol") != symbol:
            continue

        evaluation = evaluate_prediction(entry, current_price)
        evaluated_entry = dict(entry)
        evaluated_entry.update(evaluation)
        evaluated_predictions.append(evaluated_entry)

    total_predictions = len(evaluated_predictions)
    evaluated_returns = [
        entry["realized_return_pct"]
        for entry in evaluated_predictions
        if entry.get("realized_return_pct") is not None
    ]
    correct_count = sum(
        1 for entry in evaluated_predictions if entry.get("correct_direction")
    )

    hit_rate = (
        round((correct_count / total_predictions) * 100, 2)
        if total_predictions
        else 0.0
    )
    average_return = (
        round(sum(evaluated_returns) / len(evaluated_returns), 2)
        if evaluated_returns
        else 0.0
    )
    best_trade = max(evaluated_returns) if evaluated_returns else None
    worst_trade = min(evaluated_returns) if evaluated_returns else None

    return {
        "total_predictions": total_predictions,
        "hit_rate": hit_rate,
        "average_return": average_return,
        "best_trade": best_trade,
        "worst_trade": worst_trade,
        "recent_predictions": list(reversed(evaluated_predictions))[:5],
    }
