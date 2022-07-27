from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import requests
from bs4 import BeautifulSoup
import os
import json
import time


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
    driver = webdriver.Chrome(executable_path=executable_path)
    driver.get(url)

    cards = driver.find_element(By.CLASS_NAME, "list_list__2q3CF")
    last_card = cards.find_elements(By.CLASS_NAME, "actioncard_wrapper__3jY0N")[-1]

    while True:
        actions = ActionChains(driver)
        actions.move_to_element(last_card).perform()
        time.sleep(7)
        cards = driver.find_element(By.CLASS_NAME, "list_list__2q3CF")
        if cards.find_elements(By.CLASS_NAME, "actioncard_wrapper__3jY0N")[-1] == last_card:
            break
        else:
            last_card = cards.find_elements(By.CLASS_NAME, "actioncard_wrapper__3jY0N")[-1]

    with open("cs_money.html", "w", encoding="utf-8") as file:
        file.write(driver.page_source)

    soup = BeautifulSoup(driver.page_source, "lxml")
    return soup


async def get_data(weapon, dir_path=f"{os.getcwd()}\weapons_data"):
    items = []
    i = 60

    while True:
        try:
            resp = requests.get(f"https://inventories.cs.money/5.0/load_bots_inventory/730?buyBonus=35"
                                f"&isStore=true&limit=60&maxPrice=10000&minPrice=1&offset={i}"
                                f"&sort=botFirst&type={weapons[weapon]['type']}&withStack=true")
            items_list = resp.json().get("items")
            items.extend(items_list)
            if len(items_list) < 60:
                break
            i += 60
        except:
            break

    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    with open(f"{dir_path}/items_{weapon}.json", "w", encoding="utf-8") as json_file:
        json.dump(items, json_file, indent=4, ensure_ascii=False)


async def parse_weapon_type(weapon, dir_path=f"{os.getcwd()}\weapons_data"):
    with open(f"{dir_path}/items_{weapon}.json", encoding="utf-8") as json_file:
        data = json.load(json_file)

    sale_weapons = []

    for number, weapon_info in enumerate(data):
        if weapon_info["overprice"] is not None and weapon_info["overprice"] != "null":
            sale_weapon_info = {"name": weapon_info.get("fullName").strip(),
                                "price": weapon_info.get("price"),
                                "sale": f'{weapon_info.get("overprice")}%',
                                "url": weapon_info.get("3d")}
            sale_weapons.append(sale_weapon_info)
            if number == 100:
                break

    with open(f"{dir_path}/sales_{weapon}.json", "w", encoding="utf-8") as json_file:
        json.dump(sale_weapons, json_file, indent=4, ensure_ascii=False)














