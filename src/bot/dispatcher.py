from aiogram import Dispatcher

from bot.routers.start import start
from .routers.device_info import device_info

dp = Dispatcher()

dp.include_router(start)
dp.include_router(device_info)
