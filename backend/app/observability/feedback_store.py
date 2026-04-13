from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List


def _db_path() -> Path:
    # backend/app/observability/feedback_store.py -> backend/data/feedback.db
    return Path(__file__).resolve().parents[2] / "data" / "feedback.db"


def _connect() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_feedback_table() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recommendation_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                location_city TEXT,
                cuisines_json TEXT,
                min_rating REAL,
                max_budget REAL,
                top_restaurant_names_json TEXT,
                label TEXT NOT NULL
            )
            """
        )
        conn.commit()


def insert_feedback(payload: Dict[str, Any]) -> int:
    init_feedback_table()
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO recommendation_feedback (
                location_city, cuisines_json, min_rating, max_budget, top_restaurant_names_json, label
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload.get("location_city"),
                payload.get("cuisines_json"),
                payload.get("min_rating"),
                payload.get("max_budget"),
                payload.get("top_restaurant_names_json"),
                payload.get("label"),
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def fetch_feedback(limit: int = 100) -> List[Dict[str, Any]]:
    init_feedback_table()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, location_city, cuisines_json, min_rating, max_budget, top_restaurant_names_json, label
            FROM recommendation_feedback
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]

