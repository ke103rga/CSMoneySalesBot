from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import bot
from keyboards import choose_weapon_kb, do_continue_kb
from csmoney_parser import weapons, update_sales
import time
import os
import json
import asyncio
import aiofiles


class FSMClient(StatesGroup):
    first_request = State()
    continuation = State()


users = {}


async def start(message: types.Message):
    """
    The function for answer in first user's message
    :param message: massage which was gotten from user
    :return: None
    """
    text = "Какой вид оружия вас интересует?"
    await bot.send_message(message.from_user.id, text=text,
                           reply_markup=choose_weapon_kb)
    await FSMClient.first_request.set()


async def send_result(message: types.Message, batch_size=20):
    """
    The function that wraps batch of data into messages and sends it to user with a tiny delay
    :param message: massage which was gotten from user
    :param batch_size: the size of batch
    :return: None
    """
    weapon_name = message.text
    user_id = message.from_user.id

    for weapon in weapons:
        if weapon_name == weapons[weapon]["name"]:
            users[message.from_user.id] = {"iteration": 0, "weapon": weapon}
            sales_data = await get_sale_data(weapon, user_id, batch_size=batch_size)
            for weapon_info in sales_data:
                text = await create_text(weapon_info)
                await bot.send_message(user_id, text=text)
                time.sleep(0.1)
            await bot.send_message(user_id, text="Мы отправили лишь часть от скидок.\n"
                                                 "Желаете посмотреть еще?",
                                   reply_markup=do_continue_kb)
            await FSMClient.continuation.set()
            return
        await bot.send_message(user_id, tetx="На сайте не указаны товары в этой категории,\n"
                                             "Выберете одну из существующих",
                               reply_markup=choose_weapon_kb)

    await bot.send_message(message.from_user.id, text="Чтобы начать введиет команду '/start'",
                           reply_markup=choose_weapon_kb)


async def do_continue(message: types.Message):
    """
    The function that checks if user want's to continue dialog and sends to it only information that
    it hasn't already seen
    :param message: massage which was gotten from user
    :return: None
    """
    user_id = message.from_user.id
    answer = message.text
    if users.get(user_id)["iteration"] == "limit":
        await FSMClient.first_request.set()
        users[message.from_user.id] = {"iteration": 0, "weapon": ""}
        await bot.send_message(message.from_user.id,
                               text="На этом все.\nЧто посмотрите теперь?",
                               reply_markup=choose_weapon_kb)
        del users[user_id]
    else:
        if answer == "YES":
            sales_data = await get_sale_data(users.get(user_id)["weapon"], user_id)
            for weapon_info in sales_data:
                text = await create_text(weapon_info)
                await bot.send_message(user_id, text=text)
                await asyncio.sleep(0.5)
            await bot.send_message(user_id, text="Мы отправили лишь часть скидок.\n"
                                                 "Желаете увидеть еще?",
                                   reply_markup=do_continue_kb)
        else:
            await FSMClient.first_request.set()
            users[message.from_user.id] = {"iteration": 0, "weapon": ""}
            await bot.send_message(message.from_user.id,
                                   text="Что посмотрите теперь?",
                                   reply_markup=choose_weapon_kb)
            del users[user_id]


async def get_sale_data(weapon, user_id, dir_path=f"{os.getcwd()}\\weapons_data", batch_size=20):
    """
    The function that loads data about sales on particular type of weapon and
    logs the information that user has already seen
    :param weapon: str, type of weapon we need to send to user
    :param user_id: Id, user id
    :param dir_path: str, path to data with information about sales
    :param batch_size: int, the amount of products we need to send to user in one batch
    :return:
    """
    async with aiofiles.open(f"{dir_path}/items_{weapon}.json", encoding="utf-8") as json_file:
        sales_data = await json.load(json_file)
        iteration = users.get(user_id)["iteration"]
        if iteration + batch_size >= len(sales_data):
            users.get(user_id)["iteration"] = "limit"
            return sales_data[iteration:]
        else:
            users.get(user_id)["iteration"] = iteration + batch_size
            return sales_data[iteration:iteration + batch_size]


async def create_text(weapon_info):
    """
    The function that formats text to use it in message
    :param weapon_info: dict, information about particular product
    :return: str, formatted text
    """
    text = f"{weapon_info['name']}\n" \
           f"{weapon_info['price']}$\n" \
           f"{weapon_info['sale']}\n" \
           f"{weapon_info['url']}\n"
    return text


def register_handler_client(dp: Dispatcher):
    dp.register_message_handler(start)
    dp.register_message_handler(send_result, state=FSMClient.first_request)
    dp.register_message_handler(do_continue, state=FSMClient.continuation)
    dp.async_task(update_sales)
