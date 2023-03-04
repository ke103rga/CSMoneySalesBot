from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from timeloop import Timeloop
from datetime import timedelta
from bs4 import BeautifulSoup
import os
import json
import time
import aiohttp
import aiofiles


executable_path = "C:\\Users\\Виктория\\PycharmProjects\\UniversitiesParser\\chromedriver_win32\\chromedriver.exe"
test_url = "https://cs.money/ru/csgo/store/knives/"

weapons = {"knife": {"type": 2, "name": "Нож"},
           "gloves": {"type": 13, "name": "Перчатки"},
           "pistol": {"type": 5, "name": "Пистолеты"},
           "submachine_gun": {"type": 6, "name": "Пистолеты-пулеметы"},
           "auto_rifle": {"type": 3, "name": "Винтовки"},
           "snaper_rifle": {"type": 4, "name": "Снайперские винтовки"},
           "shotgun": {"type": 7, "name": "Дробовики"},
           "mashine_gun": {"type": 8, "name": "Пулеметы"},
           "key": {"type": 1, "name": "Ключи"},}


def get_whole_page(url):
    """
    Function that gets information from dynamic web-site using test-specialist tools,
    exactly selenium.
    :param url: address of page we need to parse
    :return: BeautifulSoup file, which contains the source of parsed page
    """
    driver = webdriver.Chrome(executable_path=executable_path)
    driver.get(url)

    # Finding the collections of downloaded on web page and the last of them
    cards = driver.find_element(By.CLASS_NAME, "list_list__2q3CF")
    last_card = cards.find_elements(By.CLASS_NAME, "actioncard_wrapper__3jY0N")[-1]

    while True:
        actions = ActionChains(driver)
        # Moving to the last card and waiting for load new web items by ajax
        actions.move_to_element(last_card).perform()
        time.sleep(7)
        # Selecting all new cards
        cards = driver.find_element(By.CLASS_NAME, "list_list__2q3CF")
        # Checking if new cards appeared
        if cards.find_elements(By.CLASS_NAME, "actioncard_wrapper__3jY0N")[-1] == last_card:
            break
        else:
            last_card = cards.find_elements(By.CLASS_NAME, "actioncard_wrapper__3jY0N")[-1]

    # Dumping the data
    with open("cs_money.html", "w", encoding="utf-8") as file:
        file.write(driver.page_source)

    soup = BeautifulSoup(driver.page_source, "lxml")
    return soup


async def get_data(weapon, dir_path=f"{os.getcwd()}\\weapons_data"):
    """
    Function that gets information about particular weapon type on web-site and loads it.
    :param weapon: str, type of weapon we need to find information about
    :param dir_path: str, path to file where information from web-site will be saved
    :return: None
    """
    print("Data mining process started")
    items = []
    i = 60

    while True:
        try:
            # Sending async requests for batches of web page
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://inventories.cs.money/5.0/load_bots_inventory/730?buyBonus=35"
                                       f"&isStore=true&limit=60&maxPrice=10000&minPrice=1&offset={i}"
                                       f"&sort=botFirst&type={weapons[weapon]['type']}&withStack=true") as resp:
                    # Checking if response was received and collecting data
                    if resp.status == 200:
                        items_list = await resp.json()
                        items_list = items_list.get("items")
                        items.extend(items_list)
                        if len(items_list) < 60:
                            break
                        i += 60
        except Exception:
            break

    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    # Loading the information about particular weapon type
    async with aiofiles.open(f"{dir_path}/items_{weapon}.json", mode='w') as json_file:
        json.dump(items, json_file, indent=4, ensure_ascii=False)


async def parse_weapon_type(weapon, dir_path=f"{os.getcwd()}\\weapons_data"):
    """
    Function that selected only products with sales and format them to necessary format.
    :param weapon: str, type of weapon which you need to get in necessary format
    :param dir_path: str, path with data which contains information about that type of data
    :return: None
    """
    # Taking unprocessed data of that type of weapon
    async with aiofiles.open(f"{dir_path}/items_{weapon}.json", encoding="utf-8") as json_file:
        data = await json.load(json_file)

    sale_weapons = []

    # Checking if weapon sailed and if it's true adding it to list of sales
    for number, weapon_info in enumerate(data):
        if weapon_info["overprice"] is not None and weapon_info["overprice"] != "null":
            sale_weapon_info = {"name": weapon_info.get("fullName").strip(),
                                "price": weapon_info.get("price"),
                                "sale": f'{weapon_info.get("overprice")}%',
                                "url": weapon_info.get("3d")}
            sale_weapons.append(sale_weapon_info)
            if number == 100:
                break

    # Loading information about sales products in necessary format
    async with aiofiles.open(f"{dir_path}/items_{weapon}.json", mode='w', encoding="utf-8") as json_file:
        json.dump(sale_weapons, json_file, indent=4, ensure_ascii=False)


tl = Timeloop()


@tl.job(interval=timedelta(hours=5))
async def update_sales(dir_path=f"{os.getcwd()}\\weapons_data"):
    """
    A function that was appended to bot.dispatcher event loop and executes one time in 5 hours
    :param dir_path: str, file path for updated information about sales
    :return: None
    """
    for weapon in weapons.keys():
        await get_data(weapon, dir_path)
        await parse_weapon_type(weapon, dir_path)


