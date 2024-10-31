import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.commands import COMMANDS
from bot.dispatcher import dp
from core.settings import Settings



async def main() -> None:
    settings = Settings()

    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot_instance = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Setup commands
    await bot_instance.set_my_commands(COMMANDS)

    # And the run events dispatching
    await dp.start_polling(bot_instance)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())