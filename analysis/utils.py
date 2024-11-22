import json
import pandas as pd


def get_keys(indicator):
    if indicator=='rangefilt':
        return ['period', 'multiplier', 'factor', 'super_trend_period']
    if indicator=='aroon':
        return ['aroon_length_trend','aroon_length','aroon_smooth','aroon_sign_len','aroon_gain_limit','flag_aroon_main','flag_aroon_reverse','flag_aroon_aroon']

def get_matching_rows(df_filtered,row,indicator,coin=False):
    if indicator=='rangefilt':
        matching_rows = df_filtered[
            (df_filtered['period'] == row['period']) &
            (df_filtered['multiplier'] == row['multiplier']) &
            (df_filtered['factor'] == row['factor']) &
            (df_filtered['super_trend_period'] == row['super_trend_period']) &
            ((df_filtered['coin'] != row['coin']) if coin else True)
            ]
    elif indicator=='aroon':
        matching_rows = df_filtered[
            (df_filtered['aroon_length_trend'] == row['aroon_length_trend']) &
            (df_filtered['aroon_length'] == row['aroon_length']) &
            (df_filtered['aroon_smooth'] == row['aroon_smooth']) &
            (df_filtered['aroon_sign_len'] == row['aroon_sign_len']) &
            (df_filtered['aroon_gain_limit'] == row['aroon_gain_limit']) &
            (df_filtered['flag_aroon_main'] == row['flag_aroon_main']) &
            (df_filtered['flag_aroon_reverse'] == row['flag_aroon_reverse']) &
            (df_filtered['flag_aroon_aroon'] == row['flag_aroon_aroon']) &
            ((df_filtered['coin'] != row['coin']) if coin else True)
            ]

    return matching_rows
def profit_by_coin(df: pd.DataFrame,indicator):
    best_keys = df.loc[df.groupby('coin')['total_profit'].idxmax()]
    keys=get_keys(indicator)
    result = best_keys[keys].copy()
    result['profit'] = 0.0
    result['profit_trades'] = 0
    result['loss_trades'] = 0
    result['n'] = 0
    keys=['coin']+keys+['total_profit', 'profit_trades', 'loss_trades']
    df_filtered = df[keys]

    for idx, row in best_keys.iterrows():
        matching_rows =  get_matching_rows(df_filtered, row,indicator,coin=True)

        if not matching_rows.empty:
            # Суммируем профит и количество сделок
            result.loc[idx, 'profit'] = matching_rows['total_profit'].sum()
            result.loc[idx, 'profit_trades'] = matching_rows['profit_trades'].sum()
            result.loc[idx, 'loss_trades'] = matching_rows['loss_trades'].sum()
            result.loc[idx, 'n'] = matching_rows.shape[0]

    return result



def profit_by_coin_using_signals(df: pd.DataFrame, signals: list,indicator):
    result = pd.DataFrame(signals)
    result['profit'] = 0.0
    result['profit_trades'] = 0
    result['loss_trades'] = 0
    result['n'] = 0
    keys=get_keys(indicator)
    keys=['coin']+keys+['total_profit', 'profit_trades', 'loss_trades']
    df_filtered = df[keys]
    for idx, signal in enumerate(signals):
        matching_rows = get_matching_rows(df_filtered,signal,indicator)

        if not matching_rows.empty:
            # Суммируем профит и количество сделок для всех монет
            result.loc[idx, 'profit'] = matching_rows['total_profit'].sum()
            result.loc[idx, 'profit_trades'] = matching_rows['profit_trades'].sum()
            result.loc[idx, 'loss_trades'] = matching_rows['loss_trades'].sum()
            result.loc[idx, 'n'] = matching_rows.shape[0]

    return result



def analyze_parameters(df: pd.DataFrame, parameter: str,indicator):
    analysis_result = df.groupby(parameter).agg({
        'total_profit': 'mean',
        'profit_trades': 'mean',
        'loss_trades': 'mean'
    }).reset_index()

    analysis_result.columns = [parameter, 'avg_total_profit', 'avg_profit_trades', 'avg_loss_trades']

    return analysis_result


def select_top_percent_coins(df: pd.DataFrame, top:int):

    max_profit_by_coin = df.groupby('coin')['total_profit'].max().reset_index()

    q3 = max_profit_by_coin['total_profit'].quantile(1-(top/100))

    top_percent_coins = max_profit_by_coin[max_profit_by_coin['total_profit'] >= q3]

    return top_percent_coins['coin'].tolist()

