from csv import DictReader, DictWriter
from datetime import datetime
from pathlib import Path

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


def evaluate_prediction(entry, current_price):
    """Evaluate a single prediction against the current price."""
    evaluated = dict(entry)
    try:
        price_at_signal = float(entry.get("price_at_signal", ""))
    except ValueError:
        price_at_signal = None

    if price_at_signal is not None and current_price is not None:
        price_change_pct = ((current_price - price_at_signal) / price_at_signal) * 100
        evaluated["current_price"] = current_price
        evaluated["price_change_pct"] = round(price_change_pct, 2)
    else:
        evaluated["current_price"] = None
        evaluated["price_change_pct"] = None

    signal = entry.get("signal", "")
    if evaluated["price_change_pct"] is not None and signal in {"Watch", "Strong Watch"}:
        if evaluated["price_change_pct"] > 0:
            evaluated["simple_result"] = "Correct direction"
        elif evaluated["price_change_pct"] < 0:
            evaluated["simple_result"] = "Wrong direction"
        else:
            evaluated["simple_result"] = "Neutral / unclear"
    else:
        evaluated["simple_result"] = "Neutral / unclear"

    return evaluated


def evaluate_all_predictions(current_prices_by_symbol):
    """Evaluate all saved predictions against a mapping of current prices."""
    entries = load_predictions()
    results = []
    for entry in entries:
        symbol = entry.get("symbol")
        current_price = current_prices_by_symbol.get(symbol)
        results.append(evaluate_prediction(entry, current_price))
    return results
