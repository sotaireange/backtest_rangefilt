import os
import csv
import logging
from pybit.unified_trading import HTTP
import asyncio
from binance.client import Client
import concurrent.futures
import json
import pandas as pd
import numpy as np
import time
logging.basicConfig(level=logging.INFO)


from .get_combinations_params import get_data_for_signal
from .get_coins import get_coins
from .get_df import get_df
from .signal import get_signal
from .backtest import backtest_coin
from .utils import *

def iter_coin_by_params(coins,bybit,client,timeframe,data_signals,data,file_path,fieldnames,indicator):
    try:
        time.sleep(np.random.randint(1,3))
        for i,coin in enumerate(coins):
            df=False
            k=0

            while (df is False) and k<10:

                df=get_df(bybit,client,coin,timeframe,data['limit'])

                if df is False:
                    logging.info(f"Не найдена монетка {coin}, повторно")
                    time.sleep(np.random.randint(1, 2))
                k+=1
            rows=[]
            for data_signal in data_signals:
                try:
                    signals=get_signal(df,data_signal,indicator)
                    res=backtest_coin(df,signals,data.get('tp',0.04),data.get('sl',0.016))

                    row = get_row(coin,timeframe,data_signal,res,indicator)
                    rows.append(row)
                except Exception as e:
                    logging.error(f'error {coin}\n{data_signal}\n{e}',exc_info=True)

            with open(file_path, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writerows(rows)

            logging.info(f'{coin} is finish {i+1}/{len(coins)}')
    except Exception as e:
        logging.error(f'Main error {e}')



async def backtest_coins_by_params(data):
    try:
        indicator=data['indicator']
        fieldnames=get_fieldnames(indicator)
        timeframe=data[indicator].get('params',{}).get('timeframe',30)

        bybit=data.get('bybit',1)
        stock_text='bybit' if bybit else 'binance'
        params=get_data_for_signal(data,only_params=True,indicator=indicator)
        folder_path=get_file_or_patch_name(params,timeframe,indicator,stock_text)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path,exist_ok=True)

        file_path = os.path.join(folder_path, 'results_coins.csv')


        file_exists = os.path.isfile(file_path)
        with open(file_path, 'a+', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()



        bybit=data.get('bybit',True)
        print(f'Сбор монеток')
        coins=await get_coins(bybit)
        print(f'Найдено монеток {len(coins)}')

        df=pd.read_csv(file_path,low_memory=False)

        if not df.empty:
            coins_already=df['coin'].unique().tolist()
            coins=list(set(coins)-set(coins_already))
        if bybit:
            client=HTTP()
        else:
            client=Client()
        df=None

        data_signals=get_data_for_signal(data,indicator=indicator)
        logging.info(msg=f'Начало сбора, параметры:\n{data[indicator].get('params',{})}\n'
                         f'Кол-во Монет {len(coins)}')

        num_processes = data.get('core',10)
        coin_chunks = np.array_split(coins, num_processes)
        try:
            with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
                futures = [
                    executor.submit(iter_coin_by_params, chunk, bybit, client, timeframe, data_signals, data, file_path, fieldnames,indicator)
                    for chunk in coin_chunks
                ]
        except Exception as e:
            logging.error(f"ERROR WHEN CREATE MULTIPROC {e}")
        logging.info(f'Конец сбора')
    except Exception as e:
        logging.error(f"ERROR FULL {e}",exc_info=True)


if __name__ == '__main__':
    with open('config.json', 'r') as f:
        data=json.load(f)
    asyncio.run(backtest_coins_by_params(data))
