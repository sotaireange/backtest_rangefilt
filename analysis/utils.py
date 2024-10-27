import json
import pandas as pd



def profit_by_coin(df: pd.DataFrame):
    # Найдем лучший результат для каждой монеты
    best_keys = df.loc[df.groupby('coin')['total_profit'].idxmax()]

    # Создаем пустой результат с нужными столбцами
    result = best_keys[['period', 'multiplier', 'factor', 'super_trend_period']].copy()
    result['profit'] = 0.0
    result['profit_trades'] = 0
    result['loss_trades'] = 0
    result['n'] = 0

    # Оставляем только нужные столбцы для работы
    df_filtered = df[['coin', 'period', 'multiplier', 'factor', 'super_trend_period', 'total_profit', 'profit_trades', 'loss_trades']]

    # Выполняем объединение по общим условиям
    for idx, row in best_keys.iterrows():
        matching_rows = df_filtered[
            (df_filtered['period'] == row['period']) &
            (df_filtered['multiplier'] == row['multiplier']) &
            (df_filtered['factor'] == row['factor']) &
            (df_filtered['super_trend_period'] == row['super_trend_period']) &
            (df_filtered['coin'] != row['coin'])  # Исключаем ту же монету
            ]

        if not matching_rows.empty:
            # Суммируем профит и количество сделок
            result.loc[idx, 'profit'] = matching_rows['total_profit'].sum()
            result.loc[idx, 'profit_trades'] = matching_rows['profit_trades'].sum()
            result.loc[idx, 'loss_trades'] = matching_rows['loss_trades'].sum()
            result.loc[idx, 'n'] = matching_rows.shape[0]

    return result



def profit_by_coin_using_signals(df: pd.DataFrame, signals: list):
    # Создаем пустой DataFrame для результата
    result = pd.DataFrame(signals)
    result['profit'] = 0.0
    result['profit_trades'] = 0
    result['loss_trades'] = 0
    result['n'] = 0

    # Оставляем только нужные столбцы для фильтрации
    df_filtered = df[['coin', 'period', 'multiplier', 'factor', 'super_trend_period', 'total_profit', 'profit_trades', 'loss_trades']]

    # Итерируем по каждому сигналу
    for idx, signal in enumerate(signals):
        matching_rows = df_filtered[
            (df_filtered['period'] == signal['period']) &
            (df_filtered['multiplier'] == signal['multiplier']) &
            (df_filtered['factor'] == signal['factor']) &
            (df_filtered['super_trend_period'] == signal['super_trend_period'])
            ]

        if not matching_rows.empty:
            # Суммируем профит и количество сделок для всех монет
            result.loc[idx, 'profit'] = matching_rows['total_profit'].sum()
            result.loc[idx, 'profit_trades'] = matching_rows['profit_trades'].sum()
            result.loc[idx, 'loss_trades'] = matching_rows['loss_trades'].sum()
            result.loc[idx, 'n'] = matching_rows.shape[0]

    return result



def analyze_parameters(df: pd.DataFrame, parameter: str):
    analysis_result = df.groupby(parameter).agg({
        'total_profit': 'mean',
        'profit_trades': 'mean',
        'loss_trades': 'mean'
    }).reset_index()

    analysis_result.columns = [parameter, 'avg_total_profit', 'avg_profit_trades', 'avg_loss_trades']

    return analysis_result


def select_top_percent_coins(df: pd.DataFrame, top:int):
    """
    Функция для отбора монет, максимальный профит которых находится в топ 25%.
    """
    max_profit_by_coin = df.groupby('coin')['total_profit'].max().reset_index()

    q3 = max_profit_by_coin['total_profit'].quantile(1-(top/100))

    top_percent_coins = max_profit_by_coin[max_profit_by_coin['total_profit'] >= q3]

    return top_percent_coins['coin'].tolist()


