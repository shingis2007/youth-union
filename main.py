import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent

from config import BOT_TOKEN
from database import init_db
from handlers import admin, user

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


async def main() -> None:
    await init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Admin router birinchi ro'yxatdan o'tadi — u faqat ADMIN_IDS
    # ichidagilarga javob beradi, boshqa foydalanuvchilarga tegmaydi.
    dp.include_router(admin.router)
    dp.include_router(user.router)

    @dp.errors()
    async def global_error_handler(event: ErrorEvent) -> bool:
        """
        Har qanday kutilmagan xatolik shu yerda ushlanadi va log qilinadi —
        bitta xabar ustida yuz bergan xatolik butun botni to'xtatib qo'ymaydi.
        """
        logger.exception(
            "Update ishlov berishda xatolik: %s | update_id=%s",
            event.exception,
            getattr(event.update, "update_id", "?"),
        )
        return True

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot ishga tushdi...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
