import os
import csv
import warnings
import logging
from pybit.unified_trading import HTTP
from binance.client import Client
import asyncio
from .get_coins import get_coins
from .get_df import get_df
from .signal import RangeFilterIndicator
from .backtest import backtest_coin



async def backtest_coin_with_param(data):
    fieldnames = ['coin', 'timeframe', 'period','multiplier','factor','super_trend_period','total_trades', 'profit_trades', 'loss_trades', 'total_profit']

    data_signal={
        'period': data.get('by_coin').get('period'),
        'multiplier': data.get('by_coin').get('multiplier'),
        'factor': data.get('by_coin').get('factor'),
        'super_trend_period': data.get('by_coin').get('super_trend_period')
    }
    timeframe=data.get('by_coin').get('timeframe')
    bybit=data.get('bybit',True)

    stock_text='bybit' if bybit else 'binance'

    folder_path=f'coins_{stock_text}'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path,exist_ok=True)

    file_name = f'P_{data_signal["period"]}_M_{data_signal["multiplier"]}_F_{data_signal["factor"]}_S_{data_signal["super_trend_period"]}_T_{timeframe}.csv'
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

    coins=await get_coins(bybit)

    if bybit:
        client=HTTP()
    else:
        client=Client()


    print(f'Начало сбора, параметры:\n{data['by_coin']}')
    rows=[]

    for i,coin in enumerate(coins):
        df=get_df(bybit,client,coin,timeframe)
        try:
            strategy=RangeFilterIndicator(data_signal)
            signals=strategy.signal(df)
            res=backtest_coin(df,signals,data['tp'],data['sl'])


            row = {
                'coin': coin,
                'timeframe': timeframe,
                'period':data_signal['period'],
                'multiplier': data_signal['multiplier'],
                'factor':data_signal['factor'],
                'super_trend_period':data_signal['super_trend_period'],
                'total_trades': float(res['total']['total']),
                'profit_trades': float(res['won']['total']),
                'loss_trades': float(res['lost']['total']),
                'total_profit': res['pnl']['net']['total'],
            }
            rows.append(row)
            await asyncio.sleep(1)
        except Exception as e:
            logging.error(f'Exception occurred {e}')


    with open(file_path, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerows(rows)