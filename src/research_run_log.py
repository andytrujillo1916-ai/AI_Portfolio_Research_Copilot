from datetime import datetime
from pathlib import Path

from db_service import load_research_runs as db_load_research_runs
from db_service import save_research_run as db_save_research_run


def _ensure_file(csv_path=None):
    target_path = Path(csv_path) if csv_path is not None else Path(__file__).resolve().parent.parent / "data" / "research_runs.csv"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    return target_path


def load_research_runs(csv_path=None):
    """Load saved research runs from SQLite storage."""
    rows = db_load_research_runs()
    normalized = []
    for row in rows:
        normalized.append(
            {
                "date": str(row.get("date", "")),
                "symbol": str(row.get("symbol", "")),
                "price": str(row.get("price", "")),
                "return_pct": str(row.get("return_pct", "")),
                "volatility_pct": str(row.get("volatility_pct", "")),
                "max_drawdown_pct": str(row.get("max_drawdown_pct", "")),
                "regime": str(row.get("regime", "")),
                "signal": str(row.get("signal", "")),
                "signal_score": str(row.get("signal_score", "")),
                "exposure_level": str(row.get("exposure_level", "")),
                "trade_decision": str(row.get("trade_decision", "")),
                "research_summary": str(row.get("research_summary", row.get("summary", ""))),
            }
        )
    return normalized


def save_research_run(
    symbol,
    price,
    return_pct,
    volatility_pct,
    max_drawdown_pct,
    regime,
    signal,
    signal_score,
    exposure_level,
    trade_decision,
    research_summary,
    csv_path=None,
):
    """Save one research run snapshot to SQLite storage."""
    row = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "price": str(price),
        "return_pct": str(return_pct),
        "volatility_pct": str(volatility_pct),
        "max_drawdown_pct": str(max_drawdown_pct),
        "regime": regime,
        "signal": signal,
        "signal_score": str(signal_score),
        "exposure_level": exposure_level,
        "trade_decision": trade_decision,
        "research_summary": research_summary,
    }
    db_save_research_run(
        symbol=symbol,
        date=row["date"],
        signal_score=signal_score,
        conviction_score=None,
        decision_score=None,
        final_verdict="",
        summary=research_summary,
        price=price,
        return_pct=return_pct,
        volatility_pct=volatility_pct,
        max_drawdown_pct=max_drawdown_pct,
        regime=regime,
        signal=signal,
        exposure_level=exposure_level,
        trade_decision=trade_decision,
        research_summary=research_summary,
    )
    return row


def evaluate_research_runs(symbol, current_price, csv_path=None):
    """Evaluate saved research runs against the current market price."""
    runs = load_research_runs(csv_path)
    matching_runs = [run for run in runs if run.get("symbol") == symbol]

    evaluated_runs = []
    for run in matching_runs:
        saved_price = float(run.get("price") or 0)
        realized_return_pct = 0.0

        if current_price is not None and saved_price > 0:
            realized_return_pct = ((float(current_price) - saved_price) / saved_price) * 100

        if realized_return_pct > 0.5:
            outcome = "Positive"
        elif realized_return_pct < -0.5:
            outcome = "Negative"
        else:
            outcome = "Flat"

        evaluated_runs.append(
            {
                "date": run.get("date"),
                "symbol": run.get("symbol"),
                "saved_price": saved_price,
                "current_price": float(current_price) if current_price is not None else None,
                "realized_return_pct": round(realized_return_pct, 2),
                "outcome": outcome,
                "signal": run.get("signal"),
                "signal_score": run.get("signal_score"),
                "regime": run.get("regime"),
                "trade_decision": run.get("trade_decision"),
                "research_summary": run.get("research_summary"),
            }
        )

    evaluated_runs = sorted(evaluated_runs, key=lambda row: row.get("date", ""), reverse=True)

    if not evaluated_runs:
        return {
            "total_runs": 0,
            "average_realized_return": 0.0,
            "best_run": None,
            "worst_run": None,
            "recent_evaluated_runs": [],
        }

    average_realized_return = round(
        sum(row["realized_return_pct"] for row in evaluated_runs) / len(evaluated_runs),
        2,
    )

    best_run = max(evaluated_runs, key=lambda row: row["realized_return_pct"])
    worst_run = min(evaluated_runs, key=lambda row: row["realized_return_pct"])

    return {
        "total_runs": len(evaluated_runs),
        "average_realized_return": average_realized_return,
        "best_run": best_run,
        "worst_run": worst_run,
        "recent_evaluated_runs": evaluated_runs[:5],
    }
