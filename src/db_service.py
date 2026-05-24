from datetime import datetime
from csv import DictReader
from pathlib import Path

from database import get_db_connection


DATA_PATH = Path(__file__).resolve().parent.parent / "data"


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def save_research_run(**kwargs):
    row = {
        "symbol": kwargs.get("symbol", ""),
        "date": kwargs.get("date", _now()),
        "signal_score": kwargs.get("signal_score", 0),
        "conviction_score": kwargs.get("conviction_score"),
        "decision_score": kwargs.get("decision_score"),
        "final_verdict": kwargs.get("final_verdict", ""),
        "summary": kwargs.get("summary", ""),
        "price": kwargs.get("price"),
        "return_pct": kwargs.get("return_pct"),
        "volatility_pct": kwargs.get("volatility_pct"),
        "max_drawdown_pct": kwargs.get("max_drawdown_pct"),
        "regime": kwargs.get("regime", ""),
        "signal": kwargs.get("signal", ""),
        "exposure_level": kwargs.get("exposure_level", ""),
        "trade_decision": kwargs.get("trade_decision", ""),
        "research_summary": kwargs.get("research_summary", ""),
    }
    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT INTO research_runs (
                symbol, date, signal_score, conviction_score, decision_score, final_verdict, summary,
                price, return_pct, volatility_pct, max_drawdown_pct, regime, signal, exposure_level,
                trade_decision, research_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["symbol"], row["date"], row["signal_score"], row["conviction_score"],
                row["decision_score"], row["final_verdict"], row["summary"], row["price"],
                row["return_pct"], row["volatility_pct"], row["max_drawdown_pct"], row["regime"],
                row["signal"], row["exposure_level"], row["trade_decision"], row["research_summary"],
            ),
        )
        connection.commit()
    return row


def _table_count(table_name):
    with get_db_connection() as connection:
        row = connection.execute(f"SELECT COUNT(*) AS count FROM {table_name}").fetchone()
    return int(row["count"])


def _migrate_research_runs_if_needed():
    if _table_count("research_runs") > 0:
        return
    csv_path = DATA_PATH / "research_runs.csv"
    if not csv_path.exists():
        return
    with csv_path.open("r", newline="", encoding="utf-8") as file:
        for row in DictReader(file):
            save_research_run(
                symbol=row.get("symbol", ""),
                date=row.get("date", _now()),
                signal_score=row.get("signal_score", 0),
                summary=row.get("research_summary", ""),
                price=row.get("price"),
                return_pct=row.get("return_pct"),
                volatility_pct=row.get("volatility_pct"),
                max_drawdown_pct=row.get("max_drawdown_pct"),
                regime=row.get("regime", ""),
                signal=row.get("signal", ""),
                exposure_level=row.get("exposure_level", ""),
                trade_decision=row.get("trade_decision", ""),
                research_summary=row.get("research_summary", ""),
            )


def load_research_runs(symbol=None):
    _migrate_research_runs_if_needed()
    query = "SELECT * FROM research_runs"
    params = ()
    if symbol:
        query += " WHERE symbol = ?"
        params = (symbol,)
    query += " ORDER BY date ASC"
    with get_db_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def save_prediction(**kwargs):
    row = {
        "symbol": kwargs.get("symbol", ""),
        "date": kwargs.get("date", _now()),
        "signal": kwargs.get("signal", ""),
        "score": kwargs.get("score", 0),
        "time_horizon": kwargs.get("time_horizon", ""),
        "outcome": kwargs.get("outcome", ""),
        "lesson": kwargs.get("lesson", ""),
        "reasons": kwargs.get("reasons", ""),
        "risks": kwargs.get("risks", ""),
        "price_at_signal": kwargs.get("price_at_signal"),
        "quant_score": kwargs.get("quant_score"),
        "news_score": kwargs.get("news_score"),
        "volatility": kwargs.get("volatility"),
        "max_drawdown": kwargs.get("max_drawdown"),
        "backtest_return": kwargs.get("backtest_return"),
        "suggested_action": kwargs.get("suggested_action", ""),
        "realized_return": kwargs.get("realized_return"),
        "evaluation_label": kwargs.get("evaluation_label", ""),
    }
    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT INTO predictions (
                symbol, date, signal, score, time_horizon, outcome, lesson, reasons, risks,
                price_at_signal, quant_score, news_score, volatility, max_drawdown, backtest_return,
                suggested_action, realized_return, evaluation_label
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["symbol"], row["date"], row["signal"], row["score"], row["time_horizon"],
                row["outcome"], row["lesson"], row["reasons"], row["risks"], row["price_at_signal"],
                row["quant_score"], row["news_score"], row["volatility"], row["max_drawdown"],
                row["backtest_return"], row["suggested_action"], row["realized_return"],
                row["evaluation_label"],
            ),
        )
        connection.commit()
    return row


def _migrate_predictions_if_needed():
    if _table_count("predictions") > 0:
        return
    csv_path = DATA_PATH / "prediction_log.csv"
    if not csv_path.exists():
        return
    with csv_path.open("r", newline="", encoding="utf-8") as file:
        for row in DictReader(file):
            save_prediction(**row)


def load_predictions(symbol=None):
    _migrate_predictions_if_needed()
    query = "SELECT * FROM predictions"
    params = ()
    if symbol:
        query += " WHERE symbol = ?"
        params = (symbol,)
    query += " ORDER BY date ASC"
    with get_db_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def save_thesis(**kwargs):
    row = {
        "symbol": kwargs.get("symbol", ""),
        "thesis": kwargs.get("thesis", ""),
        "confidence": kwargs.get("confidence", 5),
        "thesis_status": kwargs.get("thesis_status", "Stable"),
        "updated_at": kwargs.get("updated_at", _now()),
        "stance": kwargs.get("stance", ""),
        "last_price": kwargs.get("last_price"),
        "last_signal": kwargs.get("last_signal", ""),
        "last_regime": kwargs.get("last_regime", ""),
        "last_news_sentiment": kwargs.get("last_news_sentiment", ""),
        "last_note": kwargs.get("last_note", ""),
        "date": kwargs.get("date", _now()),
    }
    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT INTO theses (
                symbol, thesis, confidence, thesis_status, updated_at, stance, last_price,
                last_signal, last_regime, last_news_sentiment, last_note, date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
                thesis=excluded.thesis,
                confidence=excluded.confidence,
                thesis_status=excluded.thesis_status,
                updated_at=excluded.updated_at,
                stance=excluded.stance,
                last_price=excluded.last_price,
                last_signal=excluded.last_signal,
                last_regime=excluded.last_regime,
                last_news_sentiment=excluded.last_news_sentiment,
                last_note=excluded.last_note,
                date=excluded.date
            """,
            (
                row["symbol"], row["thesis"], row["confidence"], row["thesis_status"], row["updated_at"],
                row["stance"], row["last_price"], row["last_signal"], row["last_regime"],
                row["last_news_sentiment"], row["last_note"], row["date"],
            ),
        )
        connection.commit()
    return row


def _migrate_theses_if_needed():
    if _table_count("theses") > 0:
        return
    csv_path = DATA_PATH / "thesis_tracker.csv"
    if not csv_path.exists():
        return
    with csv_path.open("r", newline="", encoding="utf-8") as file:
        for row in DictReader(file):
            save_thesis(
                symbol=row.get("symbol", ""),
                thesis=row.get("thesis", ""),
                confidence=row.get("confidence", 5),
                thesis_status=row.get("thesis_status", "Stable"),
                updated_at=row.get("date", _now()),
                stance=row.get("stance", ""),
                last_price=row.get("last_price"),
                last_signal=row.get("last_signal", ""),
                last_regime=row.get("last_regime", ""),
                last_news_sentiment=row.get("last_news_sentiment", ""),
                last_note=row.get("last_note", ""),
                date=row.get("date", _now()),
            )


def load_theses(symbol=None):
    _migrate_theses_if_needed()
    query = "SELECT * FROM theses"
    params = ()
    if symbol:
        query += " WHERE symbol = ?"
        params = (symbol,)
    query += " ORDER BY updated_at ASC"
    with get_db_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def save_paper_trade(**kwargs):
    row = {
        "symbol": kwargs.get("symbol", ""),
        "entry_price": kwargs.get("entry_price"),
        "size_pct": kwargs.get("size_pct"),
        "action": kwargs.get("action", ""),
        "status": kwargs.get("status", "open"),
        "created_at": kwargs.get("created_at", _now()),
        "quantity": kwargs.get("quantity"),
        "price": kwargs.get("price"),
        "reason": kwargs.get("reason", ""),
        "date": kwargs.get("date", _now()),
    }
    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT INTO paper_trades (
                symbol, entry_price, size_pct, action, status, created_at,
                quantity, price, reason, date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["symbol"], row["entry_price"], row["size_pct"], row["action"], row["status"],
                row["created_at"], row["quantity"], row["price"], row["reason"], row["date"],
            ),
        )
        connection.commit()
    return row


def _migrate_paper_trades_if_needed():
    if _table_count("paper_trades") > 0:
        return
    csv_path = DATA_PATH / "paper_trades.csv"
    if not csv_path.exists():
        return
    with csv_path.open("r", newline="", encoding="utf-8") as file:
        for row in DictReader(file):
            save_paper_trade(
                symbol=row.get("symbol", ""),
                entry_price=row.get("price"),
                size_pct=row.get("quantity"),
                action=row.get("action", ""),
                status=row.get("status", "open"),
                created_at=row.get("date", _now()),
                quantity=row.get("quantity"),
                price=row.get("price"),
                reason=row.get("reason", ""),
                date=row.get("date", _now()),
            )


def load_paper_trades(symbol=None):
    _migrate_paper_trades_if_needed()
    query = "SELECT * FROM paper_trades"
    params = ()
    if symbol:
        query += " WHERE symbol = ?"
        params = (symbol,)
    query += " ORDER BY date ASC"
    with get_db_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    return [dict(row) for row in rows]
