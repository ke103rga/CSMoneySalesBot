from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

token = "5499901174:AAGc3PXxTDvUIT4fCv2Ryj6iGqjpUPcL_Ak"

storage = MemoryStorage()

bot = Bot(token=token)
dp = Dispatcher(bot, storage=storage)