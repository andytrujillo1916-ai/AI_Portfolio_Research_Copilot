from csv import DictReader, DictWriter
from datetime import datetime
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data"
CSV_PATH = DATA_PATH / "decision_journal.csv"
HEADERS = [
    "date",
    "symbol",
    "suggested_action",
    "confidence",
    "price_at_decision",
    "reasons",
    "risks",
    "time_horizon",
    "current_price",
    "realized_return_pct",
    "outcome_label",
    "lesson",
]


def _ensure_file():
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
            writer = DictWriter(file, fieldnames=HEADERS)
            writer.writeheader()


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_decisions():
    """Load saved decision journal entries."""
    _ensure_file()
    with CSV_PATH.open("r", newline="", encoding="utf-8") as file:
        return [row for row in DictReader(file)]


def save_decision(
    symbol,
    suggested_action,
    confidence,
    price_at_decision,
    reasons,
    risks,
    time_horizon="",
    lesson="",
):
    """Save a trade decision assistant snapshot for later evaluation."""
    _ensure_file()
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "suggested_action": suggested_action,
        "confidence": str(confidence),
        "price_at_decision": str(price_at_decision),
        "reasons": " | ".join(reasons or []),
        "risks": " | ".join(risks or []),
        "time_horizon": time_horizon,
        "current_price": "",
        "realized_return_pct": "",
        "outcome_label": "Pending",
        "lesson": lesson,
    }
    with CSV_PATH.open("a", newline="", encoding="utf-8") as file:
        writer = DictWriter(file, fieldnames=HEADERS)
        writer.writerow(entry)
    return entry


def evaluate_decision(decision, current_price):
    """Evaluate a single decision entry against current price with simple rules."""
    evaluated = dict(decision)
    price_at_decision = _safe_float(decision.get("price_at_decision"))
    current_price_value = _safe_float(current_price)

    if price_at_decision in (None, 0) or current_price_value is None:
        evaluated["current_price"] = current_price
        evaluated["realized_return_pct"] = None
        evaluated["outcome_label"] = "Pending"
        return evaluated

    realized_return_pct = ((current_price_value - price_at_decision) / price_at_decision) * 100
    action = str(decision.get("suggested_action", "")).lower()

    outcome_label = "Mixed"
    if "buy" in action:
        outcome_label = "Good" if realized_return_pct > 0 else "Poor"
    elif "sell" in action:
        outcome_label = "Good" if realized_return_pct < 0 else "Poor"
    elif action in {"hold", "watch"}:
        if abs(realized_return_pct) <= 3:
            outcome_label = "Good"
        elif abs(realized_return_pct) <= 7:
            outcome_label = "Mixed"
        else:
            outcome_label = "Poor"
    else:
        outcome_label = "Pending"

    evaluated["current_price"] = round(current_price_value, 4)
    evaluated["realized_return_pct"] = round(realized_return_pct, 2)
    evaluated["outcome_label"] = outcome_label
    return evaluated


def evaluate_decisions_for_symbol(symbol, current_price):
    """Evaluate saved decisions for one symbol and return summary + evaluated rows."""
    decisions = [row for row in load_decisions() if row.get("symbol") == symbol]
    evaluated_rows = [evaluate_decision(row, current_price) for row in decisions]

    counts = {"Good": 0, "Mixed": 0, "Poor": 0, "Pending": 0}
    for row in evaluated_rows:
        label = row.get("outcome_label", "Pending")
        if label not in counts:
            label = "Pending"
        counts[label] += 1

    return {
        "evaluated_decisions": list(reversed(evaluated_rows)),
        "summary_counts": counts,
        "total_decisions": len(evaluated_rows),
    }
