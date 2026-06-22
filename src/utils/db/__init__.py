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


init_db()


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

def get_language(user_id: str) -> str:
    inf = get_admin(user_id)
    if inf is None: return "en"
    row = dict(inf)
    return row.get("language", "en")