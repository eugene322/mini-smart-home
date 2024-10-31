from aiogram import html
from aiogram.filters import Command

from aiogram import Router
from aiogram.types import Message

from bot.commands import  START

start = Router(name=__name__)


@start.message(Command(START))
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")
