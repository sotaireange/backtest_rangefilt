import os
import csv
import logging
from pybit.unified_trading import HTTP
from binance.client import Client
from .get_coins import get_coins
from .get_df import get_df
from fetch_data_and_signal.signal import get_signal
from .backtest import backtest_coin
from .utils import *


async def backtest_coin_with_param(data):
    indicator=data.get('indicator','rangefilt')
    fieldnames=get_fieldnames(indicator)
    data_signal=get_data_signal(data,indicator)
    timeframe=data[indicator].get('by_coin').get('timeframe')
    bybit=data.get('bybit',True)

    stock_text='bybit' if bybit else 'binance'

    folder_path=f'coins_{stock_text}'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path,exist_ok=True)

    file_name=get_file_or_patch_name(data_signal,timeframe,indicator)
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

    coins=await get_coins(bybit)

    if bybit:
        client=HTTP()
    else:
        client=Client()


    print(f'Начало сбора, параметры:\n{data[indicator]['by_coin']}')
    rows=[]

    for i,coin in enumerate(coins):
        df=get_df(bybit,client,coin,timeframe,data['limit'])
        try:
            signals=get_signal(df,data_signal,indicator)
            res=backtest_coin(df,signals,data['tp'],data['sl'])


            row = get_row(coin,timeframe,data_signal,res,indicator)
            rows.append(row)
        except Exception as e:
            logging.error(f'Exception occurred {e}')


    with open(file_path, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerows(rows)