"""Database connection management."""

import sqlite3
from pathlib import Path
from typing import Any

from splitfool.db.schema import SCHEMA_SQL


def get_connection(db_path: str) -> sqlite3.Connection:
    """Get a database connection with proper settings.

    Args:
        db_path: Path to SQLite database file

    Returns:
        Configured SQLite connection
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database(db_path: str) -> None:
    """Initialize database with schema.

    Args:
        db_path: Path to SQLite database file
    """
    # Create parent directory if needed
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create and initialize database
    conn = get_connection(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()


def execute_query(
    conn: sqlite3.Connection,
    query: str,
    params: tuple[Any, ...] | None = None
) -> sqlite3.Cursor:
    """Execute a query with parameters.

    Args:
        conn: Database connection
        query: SQL query string
        params: Query parameters

    Returns:
        Cursor with results
    """
    if params:
        return conn.execute(query, params)
    return conn.execute(query)


def execute_many(
    conn: sqlite3.Connection,
    query: str,
    params_list: list[tuple[Any, ...]]
) -> None:
    """Execute a query multiple times with different parameters.

    Args:
        conn: Database connection
        query: SQL query string
        params_list: List of parameter tuples
    """
    conn.executemany(query, params_list)
