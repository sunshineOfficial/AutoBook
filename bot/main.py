import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ErrorEvent

from bot.config import BOT_TOKEN
from bot.db import init_db
from bot.handlers import admin, user

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    @dp.errors()
    async def error_handler(event: ErrorEvent) -> bool:
        exc = event.exception
        if isinstance(exc, TelegramBadRequest) and (
            "query is too old" in str(exc)
            or "message is not modified" in str(exc)
        ):
            return True  # Suppress silently
        logger.exception("Unhandled error: %s", exc)
        return True

    dp.include_router(admin.router)
    dp.include_router(user.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
