from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup


but_knife = KeyboardButton(f"Нож")
but_gloves = KeyboardButton(f"Перчатки")
but_pistol = KeyboardButton(f"Пистолеты")
but_submachine_gun = KeyboardButton(f"Пистолеты-пулеметы")
but_auto_rifle = KeyboardButton(f"Винтовки")
but_snaper_rifle = KeyboardButton(f"Снайперские винтовки")
but_shotgun = KeyboardButton(f"Дробовики")
but_mashine_gun = KeyboardButton(f"Пулеметы")
but_key = KeyboardButton(f"Ключи")

choose_weapon_kb = ReplyKeyboardMarkup(resize_keyboard=True,
                                       keyboard=[[but_knife, but_snaper_rifle],
                                                 [but_gloves, but_key],
                                                 [but_auto_rifle, but_pistol],
                                                 [but_mashine_gun], [but_shotgun],
                                                 [but_shotgun]],
                                       one_time_keyboard=True)

but_yes = KeyboardButton("YES")
but_no = KeyboardButton("NO")

do_continue_kb = ReplyKeyboardMarkup(resize_keyboard=True,
                                     keyboard=[[but_yes, but_no]],
                                     one_time_keyboard=True)

but_start = KeyboardButton("/start")
start_kb = ReplyKeyboardMarkup(resize_keyboard=True,
                               keyboard=[[but_start]],
                               one_time_keyboard=True)