from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime
import sqlite3
from src.config import DB_PATH


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                user_id       INTEGER PRIMARY KEY,
                username      TEXT,
                altamino_id   TEXT,
                language      TEXT,
                added_by      INTEGER NOT NULL,
                added_at      TEXT    NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                username    TEXT,
                text        TEXT,
                status      TEXT    NOT NULL DEFAULT 'open',
                created_at  TEXT    NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS report_photos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id   INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
                file_id     TEXT    NOT NULL
            )
        """)


init_db()


# ---------------------------------------------------------------------------
# Admins
# ---------------------------------------------------------------------------

def admin_exists(user_id: int) -> bool:
    with get_db() as db:
        return db.execute(
            "SELECT 1 FROM admins WHERE user_id = ?", (user_id,)
        ).fetchone() is not None


def add_admin(user_id: int, added_by: int, username: str | None = None) -> None:
    with get_db() as db:
        db.execute(
            """
            INSERT INTO admins (user_id, username, altamino_id, language, added_by, added_at)
            VALUES (?, ?, NULL, ?, ?, ?)
            """,
            (user_id, username, "en", added_by, datetime.utcnow().isoformat()),
        )


def remove_admin(user_id: int) -> None:
    with get_db() as db:
        db.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))


def set_altamino_id(user_id: int, altamino_id: str) -> bool:
    with get_db() as db:
        cur = db.execute(
            "UPDATE admins SET altamino_id = ? WHERE user_id = ?",
            (altamino_id, user_id),
        )
        return cur.rowcount > 0


def unset_altamino_id(user_id: int) -> bool:
    with get_db() as db:
        cur = db.execute(
            "UPDATE admins SET altamino_id = NULL WHERE user_id = ?",
            (user_id,),
        )
        return cur.rowcount > 0


def get_all_admins() -> list[sqlite3.Row]:
    with get_db() as db:
        return db.execute(
            "SELECT user_id, username, altamino_id, added_by, added_at, language FROM admins ORDER BY added_at"
        ).fetchall()


def get_admin(user_id: int) -> sqlite3.Row | None:
    with get_db() as db:
        return db.execute(
            "SELECT user_id, username, altamino_id, added_by, added_at, language FROM admins WHERE user_id = ?",
            (user_id,),
        ).fetchone()


def set_admin_language(user_id: int, language: str) -> None:
    with get_db() as db:
        db.execute(
            "UPDATE admins SET language = ? WHERE user_id = ?",
            (language, user_id),
        )


def get_language(user_id: int, isChat: bool = False) -> str:
    if isChat:
        return "en"
    inf = get_admin(user_id)
    if inf is None:
        return "en"
    return dict(inf).get("language", "en")


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def create_report(user_id: int, username: str | None, text: str | None) -> int:
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO reports (user_id, username, text, status, created_at) VALUES (?, ?, ?, 'open', ?)",
            (user_id, username, text, datetime.utcnow().isoformat()),
        )
        return cur.lastrowid


def add_report_photo(report_id: int, file_id: str) -> None:
    with get_db() as db:
        db.execute(
            "INSERT INTO report_photos (report_id, file_id) VALUES (?, ?)",
            (report_id, file_id),
        )


def get_report(report_id: int) -> sqlite3.Row | None:
    with get_db() as db:
        return db.execute(
            "SELECT * FROM reports WHERE id = ?", (report_id,)
        ).fetchone()


def get_report_photos(report_id: int) -> list[str]:
    with get_db() as db:
        rows = db.execute(
            "SELECT file_id FROM report_photos WHERE report_id = ?", (report_id,)
        ).fetchall()
        return [r["file_id"] for r in rows]


def get_open_reports(limit: int = 20, offset: int = 0) -> list[sqlite3.Row]:
    with get_db() as db:
        return db.execute(
            "SELECT * FROM reports WHERE status = 'open' ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()


def count_open_reports() -> int:
    with get_db() as db:
        return db.execute(
            "SELECT COUNT(*) FROM reports WHERE status = 'open'"
        ).fetchone()[0]


def close_report(report_id: int) -> None:
    with get_db() as db:
        db.execute(
            "UPDATE reports SET status = 'closed' WHERE id = ?", (report_id,)
        )