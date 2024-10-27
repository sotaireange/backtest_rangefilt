import itertools

def get_data_for_signal(data={},only_params=False):
    parameters = {
        'period': range(data.get('period',{}).get('min',15), data.get('period',{}).get('max',30)+1),        # lenght: от 1 до 10
        'multiplier': range(data.get('multiplier',{}).get('min',1),data.get('multiplier',{}).get('max',7)+1),     # len_signal: от 3 до 6 мб 3-6
        'factor': range(data.get('factor',{}).get('min',3),data.get('factor',{}).get('max',3)+1),           # atr: думаю лучше 3
        'super_trend_period': range(data.get('super_trend_period',{}).get('min',1),data.get('super_trend_period',{}).get('max',7)+1)
    }
    if only_params: return parameters
    combinations = list(itertools.product(*parameters.values()))

    data_for_signal_list = [dict(zip(parameters.keys(), combination)) for combination in combinations]
    return data_for_signal_list