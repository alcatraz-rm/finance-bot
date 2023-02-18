import json
import logging
import os

import requests
from aiogram import Bot, Dispatcher, executor, types
from web3 import Web3

API_TOKEN = os.getenv('TG_API_TOKEN')
ALCATRAZ_TG_ID = int(os.getenv('ALCATRAZ_TG_ID'))

ETH_ADDRESS = '0x800ecae9d3D3Bab811012D4b59bA162dcDa4A5B0'
USDT_ADDRESS = '0xdAC17F958D2ee523a2206206994597C13D831ec7'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

w3 = Web3(Web3.HTTPProvider('https://rpc.symbiosis.finance/1'))


def check_auth(user_id: int) -> bool:
    return user_id == ALCATRAZ_TG_ID


def get_exchange_rates():
    eth_rates = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=ETH').json()['data']['rates']
    usdt_rates = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=USDT').json()['data']['rates']

    return {'eth-usd': float(eth_rates['USD']), 'eth-rub': float(eth_rates['RUB']),
            'usdt-usd': float(usdt_rates['USD']),
            'usdt-rub': float(usdt_rates['RUB'])}


def get_erc20_balance(token_address: str, user_address: str) -> float:
    with open('configs/ERC20Mock.json', 'r', encoding='utf-8') as file:
        erc20_abi = json.load(file)['abi']

    token = w3.eth.contract(address=token_address, abi=erc20_abi)
    return token.functions.balanceOf(user_address).call()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    if check_auth(message.from_user.id):
        await message.reply("Hi!")


@dp.message_handler(commands=['get_balance'])
async def get_balance(message: types.Message):
    if not check_auth(message.from_user.id):
        return
    eth_balance = round(w3.eth.get_balance(ETH_ADDRESS) / 10 ** 18, 3)
    usdt_balance = round(get_erc20_balance(USDT_ADDRESS, ETH_ADDRESS) / 10 ** 6, 3)
    rates = get_exchange_rates()
    print(usdt_balance)
    await message.reply(
        f'ETH Balance:\n{eth_balance} ({round(rates["eth-usd"] * eth_balance, 3)}$, '
        f'{round(rates["eth-rub"] * eth_balance, 3)} RUB)\n\n'
        f'USDT Balance:\n{usdt_balance} ({round(rates["usdt-usd"] * usdt_balance, 3)}$, '
        f'{round(rates["usdt-rub"] * usdt_balance, 3)} RUB)'
    )


@dp.message_handler()
async def echo(message: types.Message):
    logging.info(message)
    if check_auth(message.from_user.id):
        await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
