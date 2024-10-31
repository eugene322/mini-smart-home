from typing import List

from aiogram.types import BotCommand

START = BotCommand(command="start", description="Start and setup user")
GET_INFO = BotCommand(command="get_info", description="Get info about home")


COMMANDS: List[BotCommand] = [
    START,
    GET_INFO
]