import itertools

def get_data_for_signal(data,only_params=False,indicator='rangefilt'):
    print(indicator)
    if indicator=='rangefilt':
        parameters = {
            'period': range(data[indicator]['params']['period']['min'], data[indicator]['params']['period']['max']+1),        # lenght: от 1 до 10
            'multiplier': range(data[indicator]['params']['multiplier']['min'],data[indicator]['params']['multiplier']['max']+1),     # len_signal: от 3 до 6 мб 3-6
            'factor': range(data[indicator]['params']['factor']['min'],data[indicator]['params']['factor']['max']+1),           # atr: думаю лучше 3
            'super_trend_period': range(data[indicator]['params']['super_trend_period']['min'],data[indicator]['params']['super_trend_period']['max']+1)
        }
    elif indicator=='aroon':
        parameters = {
            'aroon_length_trend': range(data[indicator]['params']['aroon_length_trend']['min'], data[indicator]['params']['aroon_length_trend']['max']+1),        # lenght: от 1 до 10
            'aroon_length': range(data[indicator]['params']['aroon_length']['min'],data[indicator]['params']['aroon_length']['max']+1),     # len_signal: от 3 до 6 мб 3-6
            'aroon_smooth': range(data[indicator]['params']['aroon_smooth']['min'],data[indicator]['params']['aroon_smooth']['max']+1),           # atr: думаю лучше 3
            'aroon_sign_len': range(data[indicator]['params']['aroon_sign_len']['min'],data[indicator]['params']['aroon_sign_len']['max']+1),
            'aroon_gain_limit': range(data[indicator]['params']['aroon_gain_limit']['min'],data[indicator]['params']['aroon_gain_limit']['max']+1),
            'flag_aroon_main': range(data[indicator]['params']['flag_aroon_main']['min'],data[indicator]['params']['flag_aroon_main']['max']+1),
            'flag_aroon_reverse': range(data[indicator]['params']['flag_aroon_reverse']['min'],data[indicator]['params']['flag_aroon_reverse']['max']+1),
            'flag_aroon_aroon': range(data[indicator]['params']['flag_aroon_aroon']['min'],data[indicator]['params']['flag_aroon_aroon']['max']+1),
        }
    if only_params: return parameters
    combinations = list(itertools.product(*parameters.values()))
    if indicator=='aroon':
        flag_keys = ['flag_aroon_main', 'flag_aroon_reverse', 'flag_aroon_aroon']
        filtered_combinations = [
            dict(zip(parameters.keys(), combination))
            for combination in combinations
            if sum(combination[i] for i, key in enumerate(parameters.keys()) if key in flag_keys) == 1
        ]

        return filtered_combinations
    data_for_signal_list = [dict(zip(parameters.keys(), combination)) for combination in combinations]
    return data_for_signal_list