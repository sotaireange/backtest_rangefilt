import os
import pandas as pd


from .utils import *
from fetch_data_and_signal.get_combinations_params import get_data_for_signal


def full_analysis(data):
    params=get_data_for_signal(data['params'],only_params=True)

    bybit=data.get('bybit',1)
    stock_text='bybit' if bybit else 'binance'
    timeframe=data['params']['timeframe']
    folder_path=f'P_{params["period"][0]}_{params["period"][-1]}_M_{params["multiplier"][0]}_{params["multiplier"][-1]}_F_{params["factor"][0]}_{params["factor"][-1]}_S_{params["super_trend_period"][0]}_{params["super_trend_period"][-1]}_T_{timeframe}_{stock_text}'
    file_path = os.path.join(folder_path, 'results_coins.csv')

    df=pd.read_csv(file_path,low_memory=False)
    top=data.get('top',[10,25,50])

    data_signal=get_data_for_signal(data['params'])

    result:pd.DataFrame=profit_by_coin_using_signals(df,data_signal)
    file_path_by_param=os.path.join(folder_path,f'by_signals.csv')
    result.to_csv(file_path_by_param,index=False,header=True, columns=result.columns)

    for param in ['period','multiplier','factor','super_trend_period']:
        result:pd.DataFrame=analyze_parameters(df,param)
        file_path=os.path.join(folder_path,f'{param}.csv')
        result.to_csv(file_path,index=False,header=True, columns=result.columns)

    result:pd.DataFrame=profit_by_coin(df)
    file_path_by_param=os.path.join(folder_path,f'By_best_coin.csv')
    result.to_csv(file_path_by_param,index=False,header=True, columns=result.columns)


    for top in top:
        top_coins=select_top_percent_coins(df,top)
        df_top=df[df['coin'].isin(top_coins)]
        for param in ['period','multiplier','factor','super_trend_period']:
            result:pd.DataFrame=analyze_parameters(df_top,param)
            file_path=os.path.join(folder_path,f'top_{top}_{param}.csv')
            result.to_csv(file_path,index=False,header=True, columns=result.columns)

        result:pd.DataFrame=profit_by_coin_using_signals(df_top,data_signal)
        file_path=os.path.join(folder_path,f'Signals_top_{top}.csv')
        result.to_csv(file_path,index=False,header=True, columns=result.columns)