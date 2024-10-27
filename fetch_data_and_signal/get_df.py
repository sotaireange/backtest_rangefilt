
import logging

import pandas as pd
from datetime import datetime




def get_df_bybit(session,coin,timeframe,limit=1000):
    try:
        klines = session.get_kline(category='linear', symbol=coin, interval=timeframe, limit=limit)['result']['list']
        date_ = []
        open_ = []
        close_ = []
        high_ = []
        low_ = []
        volume_ = []
        for kln in klines:
            date_.append(datetime.fromtimestamp(int(kln[0]) / 1000))
            open_.append(float(kln[1]))
            high_.append(float(kln[2]))
            low_.append(float(kln[3]))
            close_.append(float(kln[4]))
            volume_.append(float(kln[5]))
        data = pd.DataFrame({'Open': open_, 'High': high_, 'Low': low_, 'Close': close_, 'volume': volume_})
        data.index.name = 'Date'
        data.index = date_
        return data[::-1]
    except Exception as e:
        logging.error(msg=f'{e}\nline 123')
        return False


def get_df_binance(client,coin,timeframe,limit=200):
    try:
        if int(timeframe)>=60:
            timeframe=int(timeframe)//60
            arc='h'
        else:
            arc='m'
        klines = client.futures_klines(symbol=coin, interval=f'{timeframe}{arc}', limit=limit)
        data = pd.DataFrame(klines, columns=[
            'Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
            'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
            'Taker buy quote asset volume', 'Ignore'
        ])

        data['Open time'] = pd.to_datetime(data['Open time'], unit='ms')

        data.set_index('Open time', inplace=True)

        data = data.astype({
            'Open': 'float64',
            'High': 'float64',
            'Low': 'float64',
            'Close': 'float64',
            'Volume': 'float64'
        })

        data.rename(columns={
            'Volume': 'volume'
        }, inplace=True)

        data = data[['Open', 'High', 'Low', 'Close', 'volume']]

        return data
    except Exception as e:
        logging.error(msg=f'{e}\nline 123')
        return


def get_df(bybit,client,coin,timeframe):
    if bybit:
        df= get_df_bybit(client,coin,timeframe)
    else:
        df= get_df_binance(client,coin,timeframe)
    return df