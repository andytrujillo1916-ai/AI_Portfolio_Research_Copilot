from datetime import datetime

from db_service import load_predictions as db_load_predictions
from db_service import save_prediction as db_save_prediction
from evaluation_engine import evaluate_prediction


def load_predictions():
    """Load prediction log entries from SQLite."""
    rows = db_load_predictions()
    normalized = []
    for row in rows:
        normalized.append(
            {
                "date": str(row.get("date", "")),
                "symbol": str(row.get("symbol", "")),
                "signal": str(row.get("signal", "")),
                "score": str(row.get("score", "")),
                "reasons": str(row.get("reasons", "")),
                "risks": str(row.get("risks", "")),
                "price_at_signal": str(row.get("price_at_signal", "")),
                "time_horizon": str(row.get("time_horizon", "")),
                "outcome": str(row.get("outcome", "")),
                "lesson": str(row.get("lesson", "")),
                "quant_score": str(row.get("quant_score", "")),
                "news_score": str(row.get("news_score", "")),
                "volatility": str(row.get("volatility", "")),
                "max_drawdown": str(row.get("max_drawdown", "")),
                "backtest_return": str(row.get("backtest_return", "")),
                "suggested_action": str(row.get("suggested_action", "")),
                "realized_return": str(row.get("realized_return", "")),
                "evaluation_label": str(row.get("evaluation_label", "")),
            }
        )
    return normalized


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
    quant_score="",
    news_score="",
    volatility="",
    max_drawdown="",
    backtest_return="",
    suggested_action="",
    realized_return="",
    evaluation_label="",
):
    """Add a new prediction log entry in SQLite storage."""
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
        "quant_score": str(quant_score),
        "news_score": str(news_score),
        "volatility": str(volatility),
        "max_drawdown": str(max_drawdown),
        "backtest_return": str(backtest_return),
        "suggested_action": str(suggested_action),
        "realized_return": str(realized_return),
        "evaluation_label": str(evaluation_label),
    }
    db_save_prediction(**entry)
    return entry


def update_prediction_outcome(
    index,
    outcome,
    lesson,
    realized_return=None,
    evaluation_label=None,
):
    """Update outcome fields in-memory return (legacy helper retained)."""
    entries = load_predictions()
    if index < 0 or index >= len(entries):
        raise IndexError("Prediction entry index out of range")
    entries[index]["outcome"] = outcome
    entries[index]["lesson"] = lesson
    if realized_return is not None:
        entries[index]["realized_return"] = str(realized_return)
    if evaluation_label is not None:
        entries[index]["evaluation_label"] = evaluation_label
    # Keep behavior simple: append updated snapshot row so learning views remain usable.
    db_save_prediction(**entries[index])
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
