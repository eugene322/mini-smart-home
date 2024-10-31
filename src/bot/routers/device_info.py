from pprint import pprint

from aiogram.filters import Command

from aiogram import Router, Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.utils.callback_answer import CallbackAnswer
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.commands import GET_INFO

device_info = Router(name=__name__)

class DeviceInfoCD(CallbackData, prefix="di"):
    name: str
    state: str


@device_info.message(Command(GET_INFO))
async def command_get_info_handler(message: Message) -> None:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Home 1",
        callback_data=DeviceInfoCD(name="name1", state="state1").pack(),
    )
    builder.button(
        text="Home 2",
        callback_data=DeviceInfoCD(name="name2", state="state2").pack(),
    )

    await message.answer(
        "Select device in the home",
        reply_markup=builder.as_markup()
    )

@device_info.callback_query(DeviceInfoCD.filter())
async def callback_get_info_handler(query: CallbackQuery, callback_data: DeviceInfoCD):
    pprint(callback_data)