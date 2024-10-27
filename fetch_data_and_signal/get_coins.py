import sys
from pybit.unified_trading import HTTP
import ccxt.async_support as ccxt
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from binance.client import Client
import numpy as np

async def get_futures_symbols_below_price(exchange_name='bybit',coins=[], max_price=150):
    # Инициализируем биржу через ccxt
    exchange = getattr(ccxt, exchange_name)({
        'enableRateLimit': True
    })


    symbols_below_max_price = []

    # Функция для асинхронного получения данных о символе
    async def fetch_symbol_price(symbol):
        try:
            await asyncio.sleep(np.random.choice(np.linspace(0, 5, 20)))
            ticker = await exchange.fetch_ticker(symbol)
            last_price = ticker['last']
            if last_price < max_price:
                symbols_below_max_price.append(symbol)
        except Exception as e:
            print(f"Ошибка при обработке {symbol}: {str(e)}")

    # Создаем задачи для всех фьючерсных символов
    tasks = [fetch_symbol_price(symbol) for symbol in coins]

    await asyncio.gather(*tasks)

    # Закрываем соединение с биржей
    await exchange.close()

    return symbols_below_max_price



async def get_coins_bybit():
    session=HTTP()
    info = (session.get_instruments_info(category='linear'))['result']['list']
    list_tokens=[coin['symbol'] for coin in info]

    symbols_under_150 = await (get_futures_symbols_below_price('bybit',list_tokens, 150))
    return symbols_under_150

async def get_coins_binance():
    client=Client()
    res=client.futures_exchange_info()
    symbols = [symbol['symbol'] for symbol in res['symbols'] if symbol['symbol'].endswith('USDT')]

    symbols_under_150 = await (get_futures_symbols_below_price('binance',symbols, 150))
    return symbols_under_150


async def get_coins(bybit):
    if bybit:
        coins=await get_coins_bybit()
    else:
        coins=await get_coins_binance()
    return coins


