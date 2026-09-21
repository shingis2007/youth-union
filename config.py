import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN topilmadi! Loyiha papkasida .env fayl yaratib, "
        "ichiga BOT_TOKEN=... qatorini yozing (.env.example ga qarang)."
    )

_admin_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in _admin_ids_raw.split(",") if x.strip().isdigit()]

if not ADMIN_IDS:
    raise RuntimeError(
        "ADMIN_IDS topilmadi yoki bo'sh! .env faylida ADMIN_IDS=123456789,987654321 "
        "ko'rinishida kamida bitta admin Telegram ID sini kiriting."
    )

DB_PATH = os.getenv("DB_PATH", "bot_database.db")
