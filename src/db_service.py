from datetime import datetime
from csv import DictReader
import json
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


def default_financial_profile():
    return {
        "cash": 0.0,
        "monthly_income": 0.0,
        "monthly_expenses": 0.0,
        "emergency_fund": 0.0,
        "debt": 0.0,
        "investment_horizon": "3-5 years",
        "risk_tolerance": "Moderate",
        "liquidity_needs": "Medium",
        "goals": "Grow long-term wealth while managing downside risk.",
        "tax_account_type": "Taxable",
        "max_single_stock_exposure": 15.0,
        "max_sector_exposure": 35.0,
        "updated_at": "",
    }


def load_financial_profile():
    with get_db_connection() as connection:
        row = connection.execute("SELECT * FROM financial_profile WHERE id = 1").fetchone()
    if not row:
        return default_financial_profile()
    profile = dict(row)
    profile.pop("id", None)
    return profile


def save_financial_profile(**kwargs):
    current = default_financial_profile()
    current.update(kwargs)
    current["updated_at"] = kwargs.get("updated_at", _now())
    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT INTO financial_profile (
                id, cash, monthly_income, monthly_expenses, emergency_fund, debt,
                investment_horizon, risk_tolerance, liquidity_needs, goals, tax_account_type,
                max_single_stock_exposure, max_sector_exposure, updated_at
            ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                cash=excluded.cash,
                monthly_income=excluded.monthly_income,
                monthly_expenses=excluded.monthly_expenses,
                emergency_fund=excluded.emergency_fund,
                debt=excluded.debt,
                investment_horizon=excluded.investment_horizon,
                risk_tolerance=excluded.risk_tolerance,
                liquidity_needs=excluded.liquidity_needs,
                goals=excluded.goals,
                tax_account_type=excluded.tax_account_type,
                max_single_stock_exposure=excluded.max_single_stock_exposure,
                max_sector_exposure=excluded.max_sector_exposure,
                updated_at=excluded.updated_at
            """,
            (
                current["cash"],
                current["monthly_income"],
                current["monthly_expenses"],
                current["emergency_fund"],
                current["debt"],
                current["investment_horizon"],
                current["risk_tolerance"],
                current["liquidity_needs"],
                current["goals"],
                current["tax_account_type"],
                current["max_single_stock_exposure"],
                current["max_sector_exposure"],
                current["updated_at"],
            ),
        )
        connection.commit()
    return current


def load_real_holdings():
    with get_db_connection() as connection:
        rows = connection.execute("SELECT * FROM real_holdings ORDER BY symbol ASC").fetchall()
    return [dict(row) for row in rows]


def save_real_holding(**kwargs):
    row = {
        "symbol": str(kwargs.get("symbol", "")).upper().strip(),
        "shares": kwargs.get("shares", 0.0),
        "cost_basis": kwargs.get("cost_basis", 0.0),
        "account_type": kwargs.get("account_type", "Taxable"),
        "current_value": kwargs.get("current_value", 0.0),
        "target_notes": kwargs.get("target_notes", ""),
        "updated_at": kwargs.get("updated_at", _now()),
    }
    if not row["symbol"]:
        return row
    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT INTO real_holdings (
                symbol, shares, cost_basis, account_type, current_value, target_notes, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
                shares=excluded.shares,
                cost_basis=excluded.cost_basis,
                account_type=excluded.account_type,
                current_value=excluded.current_value,
                target_notes=excluded.target_notes,
                updated_at=excluded.updated_at
            """,
            (
                row["symbol"],
                row["shares"],
                row["cost_basis"],
                row["account_type"],
                row["current_value"],
                row["target_notes"],
                row["updated_at"],
            ),
        )
        connection.commit()
    return row


def delete_real_holding(symbol):
    symbol = str(symbol or "").upper().strip()
    if not symbol:
        return False
    with get_db_connection() as connection:
        cursor = connection.execute("DELETE FROM real_holdings WHERE symbol = ?", (symbol,))
        connection.commit()
    return cursor.rowcount > 0


def save_recommendation_log(**kwargs):
    engine_inputs = kwargs.get("engine_inputs", {})
    if not isinstance(engine_inputs, str):
        engine_inputs = json.dumps(engine_inputs)
    row = {
        "symbol": str(kwargs.get("symbol", "")).upper().strip(),
        "date": kwargs.get("date", _now()),
        "action": kwargs.get("action", ""),
        "horizon": kwargs.get("horizon", ""),
        "score": kwargs.get("score", 0.0),
        "price": kwargs.get("price"),
        "engine_inputs": engine_inputs,
        "data_gate": kwargs.get("data_gate", ""),
        "suitability_status": kwargs.get("suitability_status", ""),
        "sector": kwargs.get("sector", ""),
        "market_regime": kwargs.get("market_regime", ""),
        "benchmark_symbol": kwargs.get("benchmark_symbol", "SPY"),
        "benchmark_return_pct": kwargs.get("benchmark_return_pct"),
        "outcome_price": kwargs.get("outcome_price"),
        "realized_return_pct": kwargs.get("realized_return_pct"),
        "max_drawdown_after_signal": kwargs.get("max_drawdown_after_signal"),
        "alpha_vs_benchmark_pct": kwargs.get("alpha_vs_benchmark_pct"),
        "outcome_label": kwargs.get("outcome_label", ""),
        "lesson": kwargs.get("lesson", ""),
    }
    if not row["symbol"]:
        return row
    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT INTO recommendation_log (
                symbol, date, action, horizon, score, price, engine_inputs, data_gate,
                suitability_status, sector, market_regime, benchmark_symbol, benchmark_return_pct,
                outcome_price, realized_return_pct, max_drawdown_after_signal,
                alpha_vs_benchmark_pct, outcome_label, lesson
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["symbol"],
                row["date"],
                row["action"],
                row["horizon"],
                row["score"],
                row["price"],
                row["engine_inputs"],
                row["data_gate"],
                row["suitability_status"],
                row["sector"],
                row["market_regime"],
                row["benchmark_symbol"],
                row["benchmark_return_pct"],
                row["outcome_price"],
                row["realized_return_pct"],
                row["max_drawdown_after_signal"],
                row["alpha_vs_benchmark_pct"],
                row["outcome_label"],
                row["lesson"],
            ),
        )
        connection.commit()
    return row


def load_recommendation_log(symbol=None):
    query = "SELECT * FROM recommendation_log"
    params = ()
    if symbol:
        query += " WHERE symbol = ?"
        params = (str(symbol).upper().strip(),)
    query += " ORDER BY date ASC"
    with get_db_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def update_recommendation_outcome(
    recommendation_id,
    outcome_price=None,
    realized_return_pct=None,
    max_drawdown_after_signal=None,
    alpha_vs_benchmark_pct=None,
    outcome_label="",
    lesson="",
    evaluation_date=None,
):
    evaluation_date = evaluation_date or _now()
    with get_db_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE recommendation_log
            SET outcome_price = ?,
                realized_return_pct = ?,
                max_drawdown_after_signal = ?,
                alpha_vs_benchmark_pct = ?,
                outcome_label = ?,
                lesson = ?,
                evaluation_date = ?
            WHERE id = ?
            """,
            (
                outcome_price,
                realized_return_pct,
                max_drawdown_after_signal,
                alpha_vs_benchmark_pct,
                outcome_label,
                lesson,
                evaluation_date,
                recommendation_id,
            ),
        )
        connection.commit()
    return cursor.rowcount > 0


def save_broker_alert(**kwargs):
    details = kwargs.get("ticket_details", {})
    if not isinstance(details, str):
        details = json.dumps(details)
    row = {
        "symbol": str(kwargs.get("symbol", "")).upper().strip(),
        "action": kwargs.get("action", ""),
        "confidence": kwargs.get("confidence", ""),
        "ticket_details": details,
        "status": kwargs.get("status", "Pending"),
        "created_at": kwargs.get("created_at", _now()),
        "resolved_at": kwargs.get("resolved_at", ""),
        "outcome_notes": kwargs.get("outcome_notes", ""),
    }
    if not row["symbol"]:
        return row
    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT INTO broker_alerts (
                symbol, action, confidence, ticket_details, status, created_at, resolved_at, outcome_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["symbol"],
                row["action"],
                row["confidence"],
                row["ticket_details"],
                row["status"],
                row["created_at"],
                row["resolved_at"],
                row["outcome_notes"],
            ),
        )
        connection.commit()
    return row


def load_broker_alerts(status=None):
    query = "SELECT * FROM broker_alerts"
    params = ()
    if status:
        query += " WHERE status = ?"
        params = (status,)
    query += " ORDER BY created_at DESC"
    with get_db_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def update_broker_alert_status(alert_id, status, outcome_notes="", resolved_at=None):
    resolved_at = resolved_at or (_now() if status in {"Resolved", "Dismissed"} else "")
    with get_db_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE broker_alerts
            SET status = ?, outcome_notes = ?, resolved_at = ?
            WHERE id = ?
            """,
            (status, outcome_notes, resolved_at, alert_id),
        )
        connection.commit()
    return cursor.rowcount > 0


def save_agent_research_task(**kwargs):
    row = {
        "symbol": str(kwargs.get("symbol", "")).upper().strip(),
        "task_type": kwargs.get("task_type", ""),
        "priority": kwargs.get("priority", "Medium"),
        "assigned_agent_role": kwargs.get("assigned_agent_role", "AIOS Assistant Agent"),
        "status": kwargs.get("status", "Open"),
        "due_check_date": kwargs.get("due_check_date", ""),
        "findings": kwargs.get("findings", ""),
        "linked_final_verdict": kwargs.get("linked_final_verdict", ""),
        "created_at": kwargs.get("created_at", _now()),
        "updated_at": kwargs.get("updated_at", _now()),
    }
    if not row["symbol"]:
        return row
    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT INTO agent_research_queue (
                symbol, task_type, priority, assigned_agent_role, status, due_check_date,
                findings, linked_final_verdict, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["symbol"],
                row["task_type"],
                row["priority"],
                row["assigned_agent_role"],
                row["status"],
                row["due_check_date"],
                row["findings"],
                row["linked_final_verdict"],
                row["created_at"],
                row["updated_at"],
            ),
        )
        connection.commit()
    return row


def load_agent_research_tasks(status=None):
    query = "SELECT * FROM agent_research_queue"
    params = ()
    if status:
        query += " WHERE status = ?"
        params = (status,)
    query += " ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, created_at DESC"
    with get_db_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def update_agent_research_task(task_id, status, findings="", updated_at=None):
    with get_db_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE agent_research_queue
            SET status = ?, findings = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, findings, updated_at or _now(), task_id),
        )
        connection.commit()
    return cursor.rowcount > 0


def save_agent_run(**kwargs):
    row = {
        "symbol": str(kwargs.get("symbol", "")).upper().strip(),
        "run_type": kwargs.get("run_type", "On Demand"),
        "lane": kwargs.get("lane", "Needs Data"),
        "started_at": kwargs.get("started_at", _now()),
        "completed_at": kwargs.get("completed_at", _now()),
        "data_confidence": kwargs.get("data_confidence", "Unknown"),
        "final_verdict": kwargs.get("final_verdict", "Watch"),
        "confidence": kwargs.get("confidence", "Low"),
        "score": kwargs.get("score", 0.0),
        "summary": kwargs.get("summary", ""),
        "thesis_snapshot": kwargs.get("thesis_snapshot", ""),
        "memory_delta": kwargs.get("memory_delta", ""),
        "human_review_required": 1 if kwargs.get("human_review_required", True) else 0,
    }
    if not row["symbol"]:
        return row
    with get_db_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO agent_runs (
                symbol, run_type, lane, started_at, completed_at, data_confidence,
                final_verdict, confidence, score, summary, thesis_snapshot,
                memory_delta, human_review_required
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["symbol"],
                row["run_type"],
                row["lane"],
                row["started_at"],
                row["completed_at"],
                row["data_confidence"],
                row["final_verdict"],
                row["confidence"],
                row["score"],
                row["summary"],
                row["thesis_snapshot"],
                row["memory_delta"],
                row["human_review_required"],
            ),
        )
        connection.commit()
        row["id"] = cursor.lastrowid
    return row


def load_agent_runs(symbol=None, limit=50):
    query = "SELECT * FROM agent_runs"
    params = []
    if symbol:
        query += " WHERE symbol = ?"
        params.append(str(symbol).upper().strip())
    query += " ORDER BY started_at DESC"
    if limit:
        query += " LIMIT ?"
        params.append(int(limit))
    with get_db_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
    return [dict(row) for row in rows]


def save_agent_evidence(**kwargs):
    def dumps(value):
        if isinstance(value, str):
            return value
        return json.dumps(value or [])

    row = {
        "run_id": kwargs.get("run_id"),
        "agent_name": kwargs.get("agent_name", "Unknown Agent"),
        "status": kwargs.get("status", "Needs Review"),
        "score": kwargs.get("score", 0.0),
        "key_points": dumps(kwargs.get("key_points", [])),
        "concerns": dumps(kwargs.get("concerns", [])),
        "sources_used": dumps(kwargs.get("sources_used", [])),
        "memory_references": dumps(kwargs.get("memory_references", [])),
        "recommendation": kwargs.get("recommendation", ""),
        "created_at": kwargs.get("created_at", _now()),
    }
    with get_db_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO agent_evidence (
                run_id, agent_name, status, score, key_points, concerns,
                sources_used, memory_references, recommendation, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["run_id"],
                row["agent_name"],
                row["status"],
                row["score"],
                row["key_points"],
                row["concerns"],
                row["sources_used"],
                row["memory_references"],
                row["recommendation"],
                row["created_at"],
            ),
        )
        connection.commit()
        row["id"] = cursor.lastrowid
    return row


def load_agent_evidence(run_id=None, symbol=None, limit=100):
    query = """
        SELECT e.*
        FROM agent_evidence e
        LEFT JOIN agent_runs r ON r.id = e.run_id
    """
    clauses = []
    params = []
    if run_id:
        clauses.append("e.run_id = ?")
        params.append(run_id)
    if symbol:
        clauses.append("r.symbol = ?")
        params.append(str(symbol).upper().strip())
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY e.created_at DESC"
    if limit:
        query += " LIMIT ?"
        params.append(int(limit))
    with get_db_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
    return [dict(row) for row in rows]


def load_ticker_memory(symbol):
    symbol = str(symbol or "").upper().strip()
    if not symbol:
        return {}
    with get_db_connection() as connection:
        row = connection.execute(
            "SELECT * FROM ticker_narrative_memory WHERE symbol = ?",
            (symbol,),
        ).fetchone()
    return dict(row) if row else {}


def save_ticker_memory(**kwargs):
    row = {
        "symbol": str(kwargs.get("symbol", "")).upper().strip(),
        "thesis": kwargs.get("thesis", ""),
        "bull_case": kwargs.get("bull_case", ""),
        "bear_case": kwargs.get("bear_case", ""),
        "last_verdict": kwargs.get("last_verdict", ""),
        "last_lane": kwargs.get("last_lane", ""),
        "lessons": kwargs.get("lessons", ""),
        "updated_at": kwargs.get("updated_at", _now()),
    }
    if not row["symbol"]:
        return row
    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT INTO ticker_narrative_memory (
                symbol, thesis, bull_case, bear_case, last_verdict, last_lane, lessons, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
                thesis=excluded.thesis,
                bull_case=excluded.bull_case,
                bear_case=excluded.bear_case,
                last_verdict=excluded.last_verdict,
                last_lane=excluded.last_lane,
                lessons=excluded.lessons,
                updated_at=excluded.updated_at
            """,
            (
                row["symbol"],
                row["thesis"],
                row["bull_case"],
                row["bear_case"],
                row["last_verdict"],
                row["last_lane"],
                row["lessons"],
                row["updated_at"],
            ),
        )
        connection.commit()
    return row
