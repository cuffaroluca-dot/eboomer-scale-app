"""Persistenza risposte congresso (SQLite condiviso tra tutti i partecipanti)."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "congress_data.db"
DEFAULT_EVENT = "congresso"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id TEXT NOT NULL,
                event_id TEXT NOT NULL,
                profile_key TEXT NOT NULL,
                scores_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(participant_id, event_id)
            )
            """
        )
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(submissions)").fetchall()
        }
        if "source_id" not in columns:
            conn.execute(
                "ALTER TABLE submissions ADD COLUMN source_id TEXT NOT NULL DEFAULT 'audience'"
            )
        conn.commit()


def save_submission(
    participant_id: str,
    event_id: str,
    source_id: str,
    profile_key: str,
    scores: dict,
) -> bool:
    """Salva risposta. Ritorna False se già inviata per questo evento."""
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    try:
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO submissions
                    (participant_id, event_id, source_id, profile_key, scores_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    participant_id,
                    event_id,
                    source_id,
                    profile_key,
                    json.dumps(scores),
                    now,
                ),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def get_aggregate(event_id: str) -> dict:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT profile_key, COUNT(*) AS cnt
            FROM submissions
            WHERE event_id = ?
            GROUP BY profile_key
            """,
            (event_id,),
        ).fetchall()
    counts = {k: 0 for k in ["fondamentalista", "pentito", "entusiasta", "pragmatico", "occulto"]}
    total = 0
    for row in rows:
        counts[row["profile_key"]] = row["cnt"]
        total += row["cnt"]
    return {"counts": counts, "total": total}


def get_source_totals(event_id: str) -> dict:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT source_id, COUNT(*) AS cnt
            FROM submissions
            WHERE event_id = ?
            GROUP BY source_id
            ORDER BY source_id
            """,
            (event_id,),
        ).fetchall()
    return {row["source_id"]: row["cnt"] for row in rows}


def reset_event(event_id: str) -> int:
    init_db()
    with _connect() as conn:
        cur = conn.execute(
            "DELETE FROM submissions WHERE event_id = ?",
            (event_id,),
        )
        conn.commit()
        return cur.rowcount


def has_submitted(participant_id: str, event_id: str) -> bool:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT 1 FROM submissions
            WHERE participant_id = ? AND event_id = ?
            """,
            (participant_id, event_id),
        ).fetchone()
    return row is not None
