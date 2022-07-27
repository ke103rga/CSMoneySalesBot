from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import bot
from keyboards import choose_weapon_kb, do_continue_kb
from csmoney_parser import weapons
import time
import os
import json


class FSMClient(StatesGroup):
    first_request = State()
    continuation = State()


users = {} # It's necessary to wonder a new name for that dict


async def start(message: types.Message):
    text = "Какой вид оружия вас интересует?"
    await bot.send_message(message.from_user.id, text=text,
                           reply_markup=choose_weapon_kb)
    await FSMClient.first_request.set()


async def send_result(message: types.Message):
    weapon_name = message.text
    user_id = message.from_user.id
    for weapon in weapons:
        if weapon_name == weapons[weapon]["name"]:
            users[message.from_user.id] = {"iteration": 0, "weapon": weapon}
            sales_data = await get_sale_data(weapon, user_id)
            for weapon_info in sales_data:
                text = await create_text(weapon_info)
                await bot.send_message(user_id, text=text)
                time.sleep(0.1)
            await bot.send_message(user_id, text="Мы отправили лишь часть от скидок.\n"
                                                 "Желаете увидеть еще?",
                                   reply_markup=do_continue_kb)
            await FSMClient.continuation.set()
            return
    await bot.send_message(message.from_user.id, text="Чтобы начать введиет команду '/start'",
                           reply_markup=choose_weapon_kb)


async def do_continue(message: types.Message):
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
                time.sleep(0.1)
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



async def get_sale_data(weapon, user_id, dir_path=f"{os.getcwd()}\weapons_data"):
    with open(f"{dir_path}/sales_{weapon}.json",encoding="utf-8") as sales_file:
        sales_data = json.load(sales_file)
        iter = users.get(user_id)["iteration"]
        if iter + 50 >= len(sales_data):
            users.get(user_id)["iteration"] = "limit"
            return sales_data[iter:]
        else:
            users.get(user_id)["iteration"] = iter + 50
            return sales_data[iter:iter+50]


async def create_text(weapon_info):
    text = f"{weapon_info['name']}\n" \
           f"{weapon_info['price']}$\n" \
           f"{weapon_info['sale']}\n" \
           f"{weapon_info['url']}\n"
    return text


def register_handler_client(dp: Dispatcher):
    dp.register_message_handler(start)
    dp.register_message_handler(send_result, state=FSMClient.first_request)
    dp.register_message_handler(do_continue, state=FSMClient.continuation)