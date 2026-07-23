from __future__ import annotations

import json
import aiosqlite
from contextlib import asynccontextmanager
from dataclasses import dataclass, field, asdict, fields
from enum import Enum
from typing import Any, TypeVar

from src.config import DB_PATH

# ---------- models ----------

class GreetingType(str, Enum):
    TEXT = "text"
    IMAGE = "image"


@dataclass
class ChatSettings:
    greeting_enabled: bool = False
    greeting_type: GreetingType = GreetingType.TEXT
    greeting_text: str = ""

    farewell_enabled: bool = False
    farewell_text: str = ""

    commands_enabled: bool = True


@dataclass
class CommunitySettings:
    welcome_enabled: bool = False
    welcome_text: str = ""


T = TypeVar("T")


def _from_dict(cls: type[T], data: dict[str, Any]) -> T:
    """Build a dataclass from a dict, ignoring unknown keys and filling defaults."""
    known = {f.name: f.type for f in fields(cls)}
    kwargs = {k: v for k, v in data.items() if k in known}

    for f in fields(cls):
        if isinstance(f.type, type) and issubclass(f.type, Enum) and f.name in kwargs:
            kwargs[f.name] = f.type(kwargs[f.name])
        elif f.name in kwargs and f.name == "greeting_type":
            kwargs[f.name] = GreetingType(kwargs[f.name])

    return cls(**kwargs)


def _to_json(obj) -> str:
    def default(o):
        if isinstance(o, Enum):
            return o.value
        raise TypeError(o)
    return json.dumps(asdict(obj), default=default, ensure_ascii=False)



@asynccontextmanager
async def get_db():
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    try:
        yield conn
        await conn.commit()
    finally:
        await conn.close()


async def init_db() -> None:
    async with get_db() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_settings (
                com_id   INTEGER NOT NULL,
                chat_id  TEXT    NOT NULL,
                data     TEXT    NOT NULL,
                PRIMARY KEY (com_id, chat_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS community_settings (
                com_id  INTEGER PRIMARY KEY,
                data    TEXT NOT NULL
            )
        """)
        await db.execute("PRAGMA journal_mode=WAL")


async def get_chat_settings(com_id: int, chat_id: str) -> ChatSettings:
    async with get_db() as db:
        async with db.execute(
            "SELECT data FROM chat_settings WHERE com_id = ? AND chat_id = ?",
            (com_id, chat_id),
        ) as cur:
            row = await cur.fetchone()

    if row is None:
        return ChatSettings()
    return _from_dict(ChatSettings, json.loads(row["data"]))


async def save_chat_settings(com_id: int, chat_id: str, settings: ChatSettings) -> None:
    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO chat_settings (com_id, chat_id, data)
            VALUES (?, ?, ?)
            ON CONFLICT(com_id, chat_id) DO UPDATE SET data = excluded.data
            """,
            (com_id, chat_id, _to_json(settings)),
        )


async def update_chat_settings(com_id: int, chat_id: str, **kwargs) -> ChatSettings:
    settings = await get_chat_settings(com_id, chat_id)
    for k, v in kwargs.items():
        if hasattr(settings, k):
            setattr(settings, k, v)
    await save_chat_settings(com_id, chat_id, settings)
    return settings


async def get_community_settings(com_id: int) -> CommunitySettings:
    async with get_db() as db:
        async with db.execute(
            "SELECT data FROM community_settings WHERE com_id = ?", (com_id,)
        ) as cur:
            row = await cur.fetchone()

    if row is None:
        return CommunitySettings()
    return _from_dict(CommunitySettings, json.loads(row["data"]))


async def save_community_settings(com_id: int, settings: CommunitySettings) -> None:
    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO community_settings (com_id, data)
            VALUES (?, ?)
            ON CONFLICT(com_id) DO UPDATE SET data = excluded.data
            """,
            (com_id, _to_json(settings)),
        )


async def update_community_settings(com_id: int, **kwargs) -> CommunitySettings:
    settings = await get_community_settings(com_id)
    for k, v in kwargs.items():
        if hasattr(settings, k):
            setattr(settings, k, v)
    await save_community_settings(com_id, settings)
    return settings
