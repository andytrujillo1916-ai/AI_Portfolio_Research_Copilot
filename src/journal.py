from csv import DictReader, DictWriter
from datetime import datetime
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data"
CSV_PATH = DATA_PATH / "research_journal.csv"
HEADERS = [
    "date",
    "symbol",
    "thesis",
    "signal",
    "confidence",
    "risk_notes",
    "entry_price",
    "target_price",
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


def load_journal():
    """Load journal entries from the CSV file."""
    _ensure_file()
    with CSV_PATH.open("r", newline="", encoding="utf-8") as file:
        return [row for row in DictReader(file)]


def add_journal_entry(
    symbol,
    thesis,
    signal,
    confidence,
    risk_notes="",
    entry_price="",
    target_price="",
    time_horizon="",
    outcome="",
    lesson="",
):
    """Append a new journal entry."""
    _ensure_file()
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "symbol": symbol,
        "thesis": thesis,
        "signal": signal,
        "confidence": str(confidence),
        "risk_notes": risk_notes,
        "entry_price": str(entry_price),
        "target_price": str(target_price),
        "time_horizon": time_horizon,
        "outcome": outcome,
        "lesson": lesson,
    }
    with CSV_PATH.open("a", newline="", encoding="utf-8") as file:
        writer = DictWriter(file, fieldnames=HEADERS)
        writer.writerow(entry)
    return entry


def update_journal_outcome(index, outcome, lesson):
    """Update the outcome and lesson for an existing entry by row index."""
    entries = load_journal()
    if index < 0 or index >= len(entries):
        raise IndexError("Journal entry index out of range")
    entries[index]["outcome"] = outcome
    entries[index]["lesson"] = lesson
    with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = DictWriter(file, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(entries)
    return entries[index]
