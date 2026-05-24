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

    connection.commit()


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
    tables = ["assets", "research_runs", "predictions", "theses", "paper_trades"]

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
