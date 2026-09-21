"""
Ma'lumotlar bazasi qatlami (SQLite + aiosqlite).

Barcha funksiyalar async va WAL rejimida ishlaydi — bu bir nechta
foydalanuvchi bir vaqtda botdan foydalansa ham ma'lumotlar
buzilmasligini va bot bloklanib qolmasligini ta'minlaydi.
"""

import logging
from datetime import datetime
from typing import Optional

import aiosqlite

from config import DB_PATH

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Bazani va barcha jadvallarni (agar mavjud bo'lmasa) yaratadi."""
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("PRAGMA journal_mode=WAL;")
        await conn.execute("PRAGMA foreign_keys=ON;")

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                joined_at TEXT
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tadbirlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nomi TEXT NOT NULL,
                sana TEXT NOT NULL,
                joy TEXT NOT NULL,
                tavsif TEXT,
                created_at TEXT
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS qatnashuvchilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tadbir_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                full_name TEXT,
                username TEXT,
                telefon TEXT,
                created_at TEXT,
                UNIQUE(tadbir_id, user_id),
                FOREIGN KEY (tadbir_id) REFERENCES tadbirlar(id) ON DELETE CASCADE
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS murojaatlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                full_name TEXT,
                username TEXT,
                text TEXT NOT NULL,
                date TEXT,
                status TEXT DEFAULT 'kutilmoqda',
                javob_text TEXT
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS kengash_azolari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ism TEXT NOT NULL,
                lavozim TEXT NOT NULL,
                username TEXT,
                photo_id TEXT,
                created_at TEXT
            )
        """)

        await conn.commit()

    logger.info("Baza tayyor: %s", DB_PATH)


# ================= FOYDALANUVCHILAR =================

async def add_user(user_id: int, full_name: Optional[str], username: Optional[str]) -> None:
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            """
            INSERT INTO users (user_id, full_name, username, joined_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                full_name = excluded.full_name,
                username = excluded.username
            """,
            (user_id, full_name, username, now),
        )
        await conn.commit()


async def get_all_users() -> dict:
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("SELECT user_id, full_name, username FROM users")
        rows = await cursor.fetchall()
    return {row["user_id"]: {"full_name": row["full_name"], "username": row["username"]} for row in rows}


# ================= TADBIRLAR =================

async def add_tadbir(nomi: str, sana: str, joy: str, tavsif: str) -> int:
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "INSERT INTO tadbirlar (nomi, sana, joy, tavsif, created_at) VALUES (?, ?, ?, ?, ?)",
            (nomi, sana, joy, tavsif, now),
        )
        await conn.commit()
        return cursor.lastrowid


async def get_tadbirlar() -> list:
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("SELECT * FROM tadbirlar ORDER BY id")
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_tadbir_by_id(tadbir_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("SELECT * FROM tadbirlar WHERE id = ?", (tadbir_id,))
        row = await cursor.fetchone()
    return dict(row) if row else None


# ================= QATNASHUVCHILAR (RSVP) =================

async def is_already_registered(tadbir_id: int, user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT 1 FROM qatnashuvchilar WHERE tadbir_id = ? AND user_id = ?",
            (tadbir_id, user_id),
        )
        row = await cursor.fetchone()
    return row is not None


async def add_qatnashuvchi(
    tadbir_id: int, user_id: int, full_name: Optional[str], username: Optional[str], telefon: str
) -> bool:
    """Muvaffaqiyatli qo'shilsa True, allaqachon ro'yxatdan o'tgan bo'lsa False qaytaradi."""
    now = datetime.utcnow().isoformat()
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute(
                """
                INSERT INTO qatnashuvchilar (tadbir_id, user_id, full_name, username, telefon, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (tadbir_id, user_id, full_name, username, telefon, now),
            )
            await conn.commit()
        return True
    except aiosqlite.IntegrityError:
        return False


async def get_qatnashuvchilar() -> dict:
    """{ "<tadbir_id>": [qatnashuvchi_dict, ...] } ko'rinishida qaytaradi."""
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("SELECT * FROM qatnashuvchilar ORDER BY id")
        rows = await cursor.fetchall()

    result: dict = {}
    for row in rows:
        key = str(row["tadbir_id"])
        result.setdefault(key, []).append(dict(row))
    return result


# ================= MUROJAATLAR =================

async def add_murojaat(user_id: int, full_name: Optional[str], username: Optional[str], text: str) -> int:
    now = datetime.utcnow().strftime("%d.%m.%Y %H:%M")
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            """
            INSERT INTO murojaatlar (user_id, full_name, username, text, date, status)
            VALUES (?, ?, ?, ?, ?, 'kutilmoqda')
            """,
            (user_id, full_name, username, text, now),
        )
        await conn.commit()
        return cursor.lastrowid


async def get_murojaatlar() -> list:
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("SELECT * FROM murojaatlar ORDER BY id")
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def mark_murojaat_answered(user_id: int, javob_text: str) -> None:
    """Shu foydalanuvchining eng so'nggi kutilayotgan murojaatini 'javob berildi' deb belgilaydi."""
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            """
            UPDATE murojaatlar
            SET status = 'javob berildi', javob_text = ?
            WHERE id = (
                SELECT id FROM murojaatlar
                WHERE user_id = ? AND status = 'kutilmoqda'
                ORDER BY id DESC LIMIT 1
            )
            """,
            (javob_text, user_id),
        )
        await conn.commit()


# ================= KENGASH A'ZOLARI =================

async def add_kengash_azosi(ism: str, lavozim: str, username: Optional[str], photo_id: Optional[str]) -> int:
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "INSERT INTO kengash_azolari (ism, lavozim, username, photo_id, created_at) VALUES (?, ?, ?, ?, ?)",
            (ism, lavozim, username, photo_id, now),
        )
        await conn.commit()
        return cursor.lastrowid


async def get_kengash_azolari() -> list:
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("SELECT * FROM kengash_azolari ORDER BY id")
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def delete_kengash_azosi(azo_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute("DELETE FROM kengash_azolari WHERE id = ?", (azo_id,))
        await conn.commit()
        return cursor.rowcount > 0


# ================= STATISTIKA =================

async def get_stats() -> dict:
    tables = {
        "users": "users",
        "tadbirlar": "tadbirlar",
        "qatnashuvchilar": "qatnashuvchilar",
        "murojaatlar": "murojaatlar",
        "azolar": "kengash_azolari",
    }
    stats: dict = {}
    async with aiosqlite.connect(DB_PATH) as conn:
        for key, table in tables.items():
            cursor = await conn.execute(f"SELECT COUNT(*) FROM {table}")
            row = await cursor.fetchone()
            stats[key] = row[0] if row else 0
    return stats
