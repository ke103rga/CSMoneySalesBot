from aiogram.utils import executor
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Process
from create_bot import dp
from message_handler import register_handler_client


async def on_startup(_):
    print("Bot online")


def start_bot():
    """
    The functions that starts bot's work
    :return: None
    """
    register_handler_client(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


start_bot()
