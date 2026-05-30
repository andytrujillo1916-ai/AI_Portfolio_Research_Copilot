import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "research_os.db"


def _ensure_parent():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _initialize_tables(connection):
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE,
            asset_class TEXT,
            created_at TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS research_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            date TEXT,
            signal_score REAL,
            conviction_score REAL,
            decision_score REAL,
            final_verdict TEXT,
            summary TEXT,
            price REAL,
            return_pct REAL,
            volatility_pct REAL,
            max_drawdown_pct REAL,
            regime TEXT,
            signal TEXT,
            exposure_level TEXT,
            trade_decision TEXT,
            research_summary TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            date TEXT,
            signal TEXT,
            score REAL,
            time_horizon TEXT,
            outcome TEXT,
            lesson TEXT,
            reasons TEXT,
            risks TEXT,
            price_at_signal REAL,
            quant_score REAL,
            news_score REAL,
            volatility REAL,
            max_drawdown REAL,
            backtest_return REAL,
            suggested_action TEXT,
            realized_return REAL,
            evaluation_label TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS theses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE,
            thesis TEXT,
            confidence INTEGER,
            thesis_status TEXT,
            updated_at TEXT,
            stance TEXT,
            last_price REAL,
            last_signal TEXT,
            last_regime TEXT,
            last_news_sentiment TEXT,
            last_note TEXT,
            date TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS paper_trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            entry_price REAL,
            size_pct REAL,
            action TEXT,
            status TEXT,
            created_at TEXT,
            quantity REAL,
            price REAL,
            reason TEXT,
            date TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS financial_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            cash REAL,
            monthly_income REAL,
            monthly_expenses REAL,
            emergency_fund REAL,
            debt REAL,
            investment_horizon TEXT,
            risk_tolerance TEXT,
            liquidity_needs TEXT,
            goals TEXT,
            tax_account_type TEXT,
            max_single_stock_exposure REAL,
            max_sector_exposure REAL,
            updated_at TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS real_holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE,
            shares REAL,
            cost_basis REAL,
            account_type TEXT,
            current_value REAL,
            target_notes TEXT,
            updated_at TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS recommendation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            date TEXT,
            action TEXT,
            horizon TEXT,
            score REAL,
            price REAL,
            engine_inputs TEXT,
            data_gate TEXT,
            suitability_status TEXT,
            sector TEXT,
            market_regime TEXT,
            benchmark_symbol TEXT,
            benchmark_return_pct REAL,
            outcome_price REAL,
            realized_return_pct REAL,
            max_drawdown_after_signal REAL,
            alpha_vs_benchmark_pct REAL,
            outcome_label TEXT,
            lesson TEXT,
            evaluation_date TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS broker_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            action TEXT,
            confidence TEXT,
            ticket_details TEXT,
            status TEXT,
            created_at TEXT,
            resolved_at TEXT,
            outcome_notes TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_research_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            task_type TEXT,
            priority TEXT,
            assigned_agent_role TEXT,
            status TEXT,
            due_check_date TEXT,
            findings TEXT,
            linked_final_verdict TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            run_type TEXT,
            lane TEXT,
            started_at TEXT,
            completed_at TEXT,
            data_confidence TEXT,
            final_verdict TEXT,
            confidence TEXT,
            score REAL,
            summary TEXT,
            thesis_snapshot TEXT,
            memory_delta TEXT,
            human_review_required INTEGER
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            agent_name TEXT,
            status TEXT,
            score REAL,
            key_points TEXT,
            concerns TEXT,
            sources_used TEXT,
            memory_references TEXT,
            recommendation TEXT,
            created_at TEXT,
            FOREIGN KEY(run_id) REFERENCES agent_runs(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ticker_narrative_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE,
            thesis TEXT,
            bull_case TEXT,
            bear_case TEXT,
            last_verdict TEXT,
            last_lane TEXT,
            lessons TEXT,
            updated_at TEXT
        )
        """
    )

    _ensure_columns(
        cursor,
        "recommendation_log",
        {
            "evaluation_date": "TEXT",
        },
    )

    connection.commit()


def _ensure_columns(cursor, table_name, columns):
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing = {row[1] for row in cursor.fetchall()}
    for column, definition in columns.items():
        if column not in existing:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} {definition}")


def get_db_connection():
    """Return a SQLite connection and ensure required tables exist."""
    _ensure_parent()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    _initialize_tables(connection)
    return connection


def get_database_status():
    """Return connectivity and row counts for core research tables."""
    checks = []
    row_counts = {}
    tables = [
        "assets",
        "research_runs",
        "predictions",
        "theses",
        "paper_trades",
        "financial_profile",
        "real_holdings",
        "recommendation_log",
        "broker_alerts",
        "agent_research_queue",
        "agent_runs",
        "agent_evidence",
        "ticker_narrative_memory",
    ]

    try:
        with get_db_connection() as connection:
            checks.append("Connected to SQLite database.")
            cursor = connection.cursor()
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) AS count FROM {table}")
                row_counts[table] = int(cursor.fetchone()["count"])
            status = "connected"
    except Exception as exc:
        status = "disconnected"
        checks.append(f"Connection failed: {exc}")

    return {
        "connected": status == "connected",
        "tables": tables,
        "row_counts": row_counts,
        "checks": checks,
        "db_path": str(DB_PATH),
    }
