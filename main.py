from aiogram.utils import executor
from create_bot import dp
from message_handler import register_handler_client
import csmoney_parser
from discord.ext import tasks


async def on_startup(_):
    print("Bot online")


# @tasks.loop(hours=3)
# async def parser():
#     for weapon in csmoney_parser.weapons.keys():
#         await csmoney_parser.get_data(weapon)
#         await csmoney_parser.parse_weapon_type(weapon)
#
#
# parser.start()

register_handler_client(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
