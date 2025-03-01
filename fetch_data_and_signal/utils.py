

def get_fieldnames(indicator):
    if indicator == 'rangefilt':
        fieldnames = ['coin', 'timeframe', 'period','multiplier','factor','super_trend_period','total_trades', 'profit_trades', 'loss_trades', 'total_profit']
    elif indicator == 'aroon':
        fieldnames = ['coin', 'timeframe', 'aroon_length_trend','aroon_length','aroon_smooth','aroon_sign_len','aroon_gain_limit','flag_aroon_main','flag_aroon_reverse','flag_aroon_aroon','total_trades', 'profit_trades', 'loss_trades', 'total_profit','profit_loss']
    return fieldnames


def get_data_signal(data,indicator):
    if indicator=='rangefilt':
        data_signal={
            'period': data.get(indicator,{}).get('by_coin').get('period'),
            'multiplier': data.get(indicator,{}).get('by_coin').get('multiplier'),
            'factor': data.get(indicator,{}).get('by_coin').get('factor'),
            'super_trend_period': data.get(indicator,{}).get('by_coin').get('super_trend_period')
        }
    elif indicator=='aroon':
        data_signal={'aroon_length_trend': data.get(indicator,{}).get('by_coin').get('aroon_length_trend'),
                     'aroon_length': data.get(indicator,{}).get('by_coin').get('aroon_length'),
                     'aroon_smooth': data.get(indicator,{}).get('by_coin').get('aroon_smooth'),
                     'aroon_sign_len': data.get(indicator,{}).get('by_coin').get('aroon_sign_len'),
                     'aroon_gain_limit': data.get(indicator,{}).get('by_coin').get('aroon_gain_limit'),
                     'flag_aroon_main': data.get(indicator,{}).get('by_coin').get('flag_aroon_main'),
                     'flag_aroon_reverse': data.get(indicator,{}).get('by_coin').get('flag_aroon_reverse'),
                     'flag_aroon_aroon': data.get(indicator,{}).get('by_coin').get('flag_aroon_aroon')
                     }
    return data_signal

def get_file_or_patch_name(data_signal,timeframe,indicator,stock=False):

    stock_text=''
    if stock:
        stock_text=f'{stock}_'
    if indicator=='rangefilt':
        if stock:
            file_name=(f'P_{data_signal["period"][0]}_{data_signal["period"][-1]}_M_{data_signal["multiplier"][0]}'
                       f'_{data_signal["multiplier"][-1]}_F_{data_signal["factor"][0]}_{data_signal["factor"][-1]}'
                       f'_S_{data_signal["super_trend_period"][0]}_{data_signal["super_trend_period"][-1]}'
                       f'_T_{timeframe}_{stock_text}_{indicator}')

        else:
            file_name = (f'P_{data_signal["period"]}_M_{data_signal["multiplier"]}_F_{data_signal["factor"]}'
                         f'_S_{data_signal["super_trend_period"]}_T_{timeframe}_{indicator}.csv')
    elif indicator=='aroon':
        if stock:
            print(data_signal)
            file_name =(f'LT_{data_signal["aroon_length_trend"][0]}_{data_signal["aroon_length_trend"][-1]}_L_{data_signal["aroon_length"][0]}'
                        f'_{data_signal["aroon_length"][-1]}_S_{data_signal["aroon_smooth"][0]}_{data_signal["aroon_smooth"][-1]}'
                        f'_SL_{data_signal["aroon_sign_len"][0]}_{data_signal["aroon_sign_len"][-1]}'
                        f'_GL{data_signal["aroon_gain_limit"][0]}_{data_signal["aroon_gain_limit"][-1]}'
                        f'_T_{timeframe}_{stock_text}_{indicator}'
                        f'_MRA_{data_signal["flag_aroon_main"][-1]}{data_signal["flag_aroon_reverse"][-1]}{data_signal["flag_aroon_aroon"][-1]}')
        else:
            file_name =(f'LT_{data_signal["aroon_length_trend"]}_L_{data_signal["aroon_length"]}_S_{data_signal["aroon_smooth"]}'
                        f'_SL_{data_signal["aroon_sign_len"]}_GL_{data_signal["aroon_gain_limit"]}_T_{timeframe}_{indicator}'
                        f'_MRA_{data_signal["flag_aroon_main"]}{data_signal["flag_aroon_reverse"]}{data_signal["flag_aroon_aroon"]}.csv')
    return file_name


def get_row(coin,timeframe,data_signal,res,indicator):
    if indicator=='rangefilt':
        row = {
            'coin': coin,
            'timeframe': timeframe,
            'period':data_signal['period'],
            'multiplier': data_signal['multiplier'],
            'factor':data_signal['factor'],
            'super_trend_period':data_signal['super_trend_period'],
            'total_trades': float(res.get('total',{}).get('total',0)),
            'profit_trades': float(res.get('won',{}).get('total',0)),
            'loss_trades': float(res.get('lost',{}).get('total',0)),
            'total_profit': res.get('pnl',{}).get('net',{}).get('total',0),
        }
    elif indicator=='aroon':
        row = {
            'coin': coin,
            'timeframe': timeframe,
            'aroon_length_trend':data_signal['aroon_length_trend'],
            'aroon_length': data_signal['aroon_length'],
            'aroon_smooth':data_signal['aroon_smooth'],
            'aroon_sign_len':data_signal['aroon_sign_len'],
            'aroon_gain_limit':data_signal['aroon_gain_limit'],
            'flag_aroon_main':data_signal['flag_aroon_main'],
            'flag_aroon_reverse':data_signal['flag_aroon_reverse'],
            'flag_aroon_aroon':data_signal['flag_aroon_aroon'],
            'total_trades': float(res.get('total',{}).get('total',0)),
            'profit_trades': float(res.get('won',{}).get('total',0)),
            'loss_trades': float(res.get('lost',{}).get('total',0)),
            'total_profit': res.get('pnl',{}).get('net',{}).get('total',0),
            'profit_loss':round(float(res.get('won',{}).get('total',0))/float(res.get('total',{}).get('total',1)),2)
        }
    return row