"""Low-level SQLite access helpers.

The backend intentionally stays on the built-in sqlite3 module so the demo is
portable and easy to extend later to PostgreSQL or a vector store.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .config import DB_PATH, DATABASE_DIR
from .seed import seed_database


DATABASE_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_database() -> None:
    """Create the database file, schema, and seed rows if needed."""

    seed_database()


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, object]]:
    return [dict(row) for row in rows]


def fetch_all(query: str, params: tuple[object, ...] = ()) -> list[dict[str, object]]:
    with connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return rows_to_dicts(rows)


def fetch_one(query: str, params: tuple[object, ...] = ()) -> dict[str, object] | None:
    with connect() as conn:
        row = conn.execute(query, params).fetchone()
    return dict(row) if row else None
