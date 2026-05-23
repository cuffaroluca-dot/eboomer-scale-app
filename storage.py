"""Persistenza risposte E-Boomer Scale con Google Sheets e fallback SQLite."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

from eboomer_core import AXIS_KEYS, PROFILE_LABELS


DB_PATH = Path(__file__).parent / "congress_data.db"
QUESTION_KEYS = [f"Q{i}" for i in range(1, 15)]
EXPECTED_COLUMNS = [
    "timestamp",
    "session_id",
    "group",
    "participant_id",
    "display_name",
    *QUESTION_KEYS,
    *AXIS_KEYS,
    "profile_id",
    "profile_name",
]
RESPONSE_COLUMNS = EXPECTED_COLUMNS
GSHEET_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Crea automaticamente la tabella responses se non esiste."""
    question_columns = ",\n                ".join(f"{key} TEXT" for key in QUESTION_KEYS)
    score_columns = ",\n                ".join(f"{axis} INTEGER NOT NULL DEFAULT 0" for axis in AXIS_KEYS)

    with _connect() as conn:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                "group" TEXT NOT NULL,
                participant_id TEXT NOT NULL,
                display_name TEXT,
                {question_columns},
                {score_columns},
                profile_id TEXT NOT NULL,
                profile_name TEXT NOT NULL
            )
            """
        )
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(responses)").fetchall()
        }
        if "display_name" not in columns:
            conn.execute("ALTER TABLE responses ADD COLUMN display_name TEXT")
        conn.commit()


def is_gsheet_configured() -> bool:
    """Ritorna True se Streamlit secrets contiene la config Google Sheets."""
    try:
        return "google_sheets" in st.secrets and "gcp_service_account" in st.secrets
    except Exception:
        return False


def get_gsheet_client():
    service_account_info = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(
        service_account_info,
        scopes=GSHEET_SCOPES,
    )
    return gspread.authorize(credentials)


def get_worksheet():
    sheets_config = st.secrets["google_sheets"]
    spreadsheet_name = sheets_config["spreadsheet_name"]
    worksheet_name = sheets_config["worksheet_name"]
    client = get_gsheet_client()
    spreadsheet = client.open(spreadsheet_name)
    return spreadsheet.worksheet(worksheet_name)


def ensure_header(ws) -> None:
    values = ws.get_all_values()
    header = values[0] if values else []
    if not header or any(column not in header for column in EXPECTED_COLUMNS):
        ws.update("A1", [EXPECTED_COLUMNS])


def column_letter(column_number: int) -> str:
    letters = ""
    while column_number:
        column_number, remainder = divmod(column_number - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def _clean_response(response_dict: dict) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    profile_id = str(response_dict.get("profile_id", "") or "")
    profile_name = response_dict.get("profile_name") or PROFILE_LABELS.get(profile_id, profile_id)

    row = {
        "timestamp": response_dict.get("timestamp") or now,
        "session_id": response_dict.get("session_id") or response_dict.get("event_id") or "congresso",
        "group": response_dict.get("group") or response_dict.get("source_id") or "audience",
        "participant_id": response_dict.get("participant_id") or "",
        "display_name": response_dict.get("display_name") or response_dict.get("participant_id") or "",
        "profile_id": profile_id,
        "profile_name": profile_name,
    }

    for question_id in QUESTION_KEYS:
        value = response_dict.get(question_id)
        row[question_id] = str(value).upper().strip() if value else ""

    for axis in AXIS_KEYS:
        numeric_value = pd.to_numeric(response_dict.get(axis, 0), errors="coerce")
        row[axis] = 0 if pd.isna(numeric_value) else numeric_value

    return row


def _normalize_numeric_axes(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    for axis in AXIS_KEYS:
        if axis not in normalized.columns:
            normalized[axis] = 0
        normalized[axis] = pd.to_numeric(normalized[axis], errors="coerce").fillna(0)
    return normalized


def _sqlite_save_response(response_dict: dict) -> None:
    init_db()
    row = _clean_response(response_dict)
    columns = RESPONSE_COLUMNS
    placeholders = ", ".join("?" for _ in columns)
    quoted_columns = ", ".join(f'"{col}"' if col == "group" else col for col in columns)

    with _connect() as conn:
        conn.execute(
            f"""
            INSERT INTO responses ({quoted_columns})
            VALUES ({placeholders})
            """,
            [row[col] for col in columns],
        )
        conn.commit()


def save_response(response_dict: dict) -> None:
    """Salva una risposta su Google Sheets, con fallback SQLite."""
    if is_gsheet_configured():
        try:
            ws = get_worksheet()
            ensure_header(ws)
            row = _clean_response(response_dict)
            values = [row.get(column, "") for column in EXPECTED_COLUMNS]
            if row["group"] == "faculty" and row["participant_id"]:
                participant_ids = ws.col_values(EXPECTED_COLUMNS.index("participant_id") + 1)
                try:
                    existing_row = participant_ids.index(row["participant_id"]) + 1
                except ValueError:
                    existing_row = None

                if existing_row and existing_row > 1:
                    last_column = column_letter(len(EXPECTED_COLUMNS))
                    ws.update(
                        f"A{existing_row}:{last_column}{existing_row}",
                        [values],
                        value_input_option="USER_ENTERED",
                    )
                    return

            ws.append_row(values, value_input_option="USER_ENTERED")
            return
        except Exception:
            pass

    _sqlite_save_response(response_dict)


def _sqlite_get_responses_df() -> pd.DataFrame:
    init_db()
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT
                timestamp,
                session_id,
                "group",
                participant_id,
                display_name,
                Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12, Q13, Q14,
                DT, IR, CEO, HOR, RCO, GS,
                profile_id,
                profile_name
            FROM responses
            ORDER BY timestamp
            """,
            conn,
        )
    return _normalize_numeric_axes(df)


def get_responses_df() -> pd.DataFrame:
    """Restituisce le risposte come DataFrame, usando Google Sheets se possibile."""
    if is_gsheet_configured():
        try:
            ws = get_worksheet()
            ensure_header(ws)
            records = ws.get_all_records()
            if not records:
                return _normalize_numeric_axes(pd.DataFrame(columns=EXPECTED_COLUMNS))
            df = pd.DataFrame(records)
            for column in EXPECTED_COLUMNS:
                if column not in df.columns:
                    df[column] = ""
            df = df[EXPECTED_COLUMNS]
            return _normalize_numeric_axes(df)
        except Exception:
            pass

    return _sqlite_get_responses_df()


def _sqlite_reset_responses() -> int:
    init_db()
    with _connect() as conn:
        cur = conn.execute("DELETE FROM responses")
        conn.commit()
        return cur.rowcount


def reset_responses() -> int:
    """Cancella tutte le risposte, mantenendo header Sheets se configurato."""
    if is_gsheet_configured():
        try:
            ws = get_worksheet()
            ensure_header(ws)
            values = ws.get_all_values()
            row_count = len(values)
            if row_count > 1:
                ws.delete_rows(2, row_count)
            ensure_header(ws)
            return max(row_count - 1, 0)
        except Exception:
            pass

    return _sqlite_reset_responses()


def save_submission(
    participant_id: str,
    event_id: str,
    source_id: str,
    profile_key: str,
    scores: dict,
    answers: dict | None = None,
) -> bool:
    """Compatibilita con la UI esistente. Ritorna False se gia inviato."""
    init_db()
    if has_submitted(participant_id, event_id):
        return False

    response = {
        "session_id": event_id,
        "group": source_id,
        "participant_id": participant_id,
        "display_name": participant_id,
        "profile_id": profile_key,
        "profile_name": PROFILE_LABELS.get(profile_key, profile_key),
        **{axis: scores.get(axis, 0) for axis in AXIS_KEYS},
    }
    if answers:
        response.update(answers)

    save_response(response)
    return True


def get_aggregate(event_id: str) -> dict:
    init_db()
    counts = {key: 0 for key in PROFILE_LABELS}
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT profile_id, COUNT(*) AS cnt
            FROM responses
            WHERE session_id = ?
            GROUP BY profile_id
            """,
            (event_id,),
        ).fetchall()

    total = 0
    for row in rows:
        profile_id = "cyber_occulto" if row["profile_id"] == "occulto" else row["profile_id"]
        counts[profile_id] = row["cnt"]
        total += row["cnt"]
    return {"counts": counts, "total": total}


def get_source_totals(event_id: str) -> dict:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT "group" AS source_id, COUNT(*) AS cnt
            FROM responses
            WHERE session_id = ?
            GROUP BY "group"
            ORDER BY "group"
            """,
            (event_id,),
        ).fetchall()
    return {row["source_id"]: row["cnt"] for row in rows}


def reset_event(event_id: str) -> int:
    init_db()
    with _connect() as conn:
        cur = conn.execute("DELETE FROM responses WHERE session_id = ?", (event_id,))
        conn.commit()
        return cur.rowcount


def has_submitted(participant_id: str, event_id: str) -> bool:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT 1
            FROM responses
            WHERE participant_id = ? AND session_id = ?
            """,
            (participant_id, event_id),
        ).fetchone()
    return row is not None
