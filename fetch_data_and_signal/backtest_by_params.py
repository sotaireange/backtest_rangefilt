import os
import csv
import logging
from pybit.unified_trading import HTTP
import asyncio
from binance.client import Client

import pandas as pd

from .get_combinations_params import get_data_for_signal
from .get_coins import get_coins
from .get_df import get_df
from .signal import RangeFilterIndicator
from .backtest import backtest_coin


async def backtest_coins_by_params(data):
    fieldnames = ['coin', 'timeframe', 'period','multiplier','factor','super_trend_period','total_trades', 'profit_trades', 'loss_trades', 'total_profit']
    timeframe=data.get('params',{}).get('timeframe',30)

    bybit=data.get('bybit',1)
    stock_text='bybit' if bybit else 'binance'

    params=get_data_for_signal(data.get('params',{}),only_params=True)
    folder_path=f'P_{params["period"][0]}_{params["period"][-1]}_M_{params["multiplier"][0]}_{params["multiplier"][-1]}_F_{params["factor"][0]}_{params["factor"][-1]}_S_{params["super_trend_period"][0]}_{params["super_trend_period"][-1]}_T_{timeframe}_{stock_text}'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path,exist_ok=True)

    file_path = os.path.join(folder_path, 'results_coins.csv')

    with open(file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()



    bybit=data.get('bybit',True)
    print(f'Сбор монеток')
    coins=await get_coins(bybit)
    print(f'Найдено монеток {len(coins)}')
    df=pd.read_csv(file_path)
    if not df.empty:
        coins_already=df['coin'].unique().tolist()
        coins=list(set(coins)-set(coins_already))

    if bybit:
        client=HTTP()
    else:
        client=Client()


    data_signals=get_data_for_signal(data['params'])
    print(f'Начало сбора, параметры:\n{data['params']}')

    for i,coin in enumerate(coins):
        df=get_df(bybit,client,coin,timeframe)
        rows=[]

        for data_signal in data_signals:
            try:
                strategy=RangeFilterIndicator(data_signal)
                signals=strategy.signal(df)
                res=backtest_coin(df,signals,data.get('tp',0.04),data.get('sl',0.016))

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
            except Exception as e:
                pass

        with open(file_path, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writerows(rows)
        print(f'{i+1}/{len(coins)} - {coin}')



