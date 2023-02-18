import logging
import os

from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = os.getenv('TG_API_TOKEN')
ALCATRAZ_TG_ID = int(os.getenv('ALCATRAZ_TG_ID'))
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def check_auth(user_id: int) -> bool:
    return user_id == ALCATRAZ_TG_ID


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    if check_auth(message.from_user.id):
        await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message_handler()
async def echo(message: types.Message):
    logging.info(message)
    if check_auth(message.from_user.id):
        await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
