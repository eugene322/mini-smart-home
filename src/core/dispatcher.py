from aiogram import Dispatcher

from routers.hello_world import hello_world

dp = Dispatcher()

dp.include_router(hello_world)


