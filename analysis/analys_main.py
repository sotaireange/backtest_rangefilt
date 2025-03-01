import os
import pandas as pd


from analysis.utils import *
from fetch_data_and_signal.get_combinations_params import get_data_for_signal
from fetch_data_and_signal.utils import get_file_or_patch_name




def full_analysis(data):
    indicator=data['indicator']
    params=get_data_for_signal(data,only_params=True,indicator=indicator)
    bybit=data.get('bybit',1)
    stock_text='bybit' if bybit else 'binance'
    timeframe=data[indicator]['params']['timeframe']
    folder_path=get_file_or_patch_name(params,timeframe,indicator,stock_text)
    file_path = os.path.join(folder_path, 'results_coins.csv')
    print(file_path)
    df=pd.read_csv(file_path,low_memory=False)
    top=data.get('top',[10,25,50])

    data_signal=get_data_for_signal(data,indicator=indicator)

    result:pd.DataFrame=profit_by_coin_using_signals(df,data_signal,indicator)
    file_path_by_param=os.path.join(folder_path,f'by_signals.csv')
    result.to_csv(file_path_by_param,index=False,header=True, columns=result.columns)
    #keys=get_keys(indicator)
    """for param in keys:
        result:pd.DataFrame=analyze_parameters(df,param,indicator)
        file_path=os.path.join(folder_path,f'{param}.csv')
        result.to_csv(file_path,index=False,header=True, columns=result.columns)
    """
    """    result:pd.DataFrame=profit_by_coin(df,indicator)
    file_path_by_param=os.path.join(folder_path,f'By_best_coin.csv')
    result.to_csv(file_path_by_param,index=False,header=True, columns=result.columns)"""
    file_path_by_coin=os.path.join(folder_path,f'By_best_coin.csv')
    best_keys:pd.DataFrame = df.loc[df.groupby('coin')['total_profit'].idxmax()]
    best_keys.to_csv(file_path_by_coin,header=True,index=False,columns=best_keys.columns)

    file_path_by_coin=os.path.join(folder_path,f'By_best_coin_profit.csv')
    best_keys:pd.DataFrame = df.loc[df.groupby('coin')['profit_loss'].idxmax()]
    best_keys.to_csv(file_path_by_coin,header=True,index=False,columns=best_keys.columns)

    """    for top in top:
        top_coins=select_top_percent_coins(df,top)
        df_top=df[df['coin'].isin(top_coins)]
        for param in keys:
            result:pd.DataFrame=analyze_parameters(df_top,param,indicator)
            file_path=os.path.join(folder_path,f'top_{top}_{param}.csv')
            result.to_csv(file_path,index=False,header=True, columns=result.columns)

        result:pd.DataFrame=profit_by_coin_using_signals(df_top,data_signal,indicator)
        file_path=os.path.join(folder_path,f'Signals_top_{top}.csv')
        result.to_csv(file_path,index=False,header=True, columns=result.columns)"""