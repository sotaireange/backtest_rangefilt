import pandas as pd
import numpy as np
from ta import trend

class AroonOscillator:
    def __init__(self, data={}):
        self.length_trend = int(data.get('aroon_length_trend',15))
        self.length = int(data.get('aroon_length',29))
        self.smooth = int(data.get('aroon_smooth',25))
        self.sign_len = int(data.get('aroon_sign_len',10))
        self.gain_limit = int(data.get('aroon_gain_limit',10))


    def zero_lag(self,src, length, gain_limit):
        alpha = 2 / (length + 1)
        ema = pd.Series(np.nan, index=src.index)
        ec = pd.Series(np.nan, index=src.index)

        ema.iloc[0] = src.iloc[0]  # Set the first value to src[0]
        ec.iloc[0]=src.iloc[0]
        for i in range(1, len(src)):
            ema.iloc[i] = alpha * src.iloc[i] + (1 - alpha) * ema.iloc[i - 1]
            ec.iloc[i] = alpha * (ema.iloc[i] + (gain_limit/10) * (src.iloc[i] - ec.iloc[i - 1])) + (1 - alpha) * ec.iloc[i - 1]
        return ec

    def aroon_up_down(self,data,length):
        aroon_up = []
        aroon_down = []
        for i in range(len(data)):
            if i < length - 1:
                # Недостаточно данных для расчёта
                aroon_up.append(np.nan)
                aroon_down.append(np.nan)
            else:
                highest_bars = np.argmax(data['High'].iloc[i - length + 1:i + 1])
                lowest_bars = np.argmin(data['Low'].iloc[i - length + 1:i + 1])

                aroon_up.append(100 * (highest_bars+1) / length)
                aroon_down.append(100 * (lowest_bars + 1) / length)
        df=pd.DataFrame({'aroon_up':aroon_up,'aroon_down': aroon_down},index=data.index)
        src=df['aroon_up'].ffill().replace(np.nan,0)-df['aroon_down'].ffill().replace(np.nan,0)
        return src

    def aroon_oscillator(self, data):
        src=self.aroon_up_down(data,self.length)
        return self.zero_lag(src, self.smooth, self.gain_limit)

    def crossover(self,series1, series2):
        return (series1 > series2) & (series1.shift(1) <= series2)

    def crossunder(self,series1, series2):
        return (series1 < series2) & (series1.shift(1) >= series2)


    def calculate(self, data):
        data['EMA'] = trend.ema_indicator(data['Close'], self.length_trend)
        correction = data['Close'] + (data['Close'] - data['EMA'])
        data['ZLMA'] = trend.ema_indicator(correction, self.length_trend)

        data['signal_up'] = (data['ZLMA'] > data['EMA']).astype(int)
        data['signal_down'] = (data['ZLMA'] < data['EMA']).astype(int)


        data['aroon_osc'] = self.aroon_oscillator(data)
        data['sig_line'] = trend.sma_indicator(data['aroon_osc'],window=self.sign_len)

        # Trend Signals
        data['bullish_trend'] = (data['aroon_osc'] > 0) & (data['aroon_osc'] > data['sig_line'])
        data['bearish_trend'] = (data['aroon_osc'] < 0) & (data['aroon_osc'] < data['sig_line'])

        data['zlma_side'] = np.where(data['ZLMA'] > data['ZLMA'].shift(3), True,
                                     np.where(data['ZLMA'] < data['ZLMA'].shift(3), False, False))
        data['ema_side'] = np.where(data['EMA'] < data['ZLMA'], True, False)

        return data


    def get_signal(self,df):
        data=df.copy()
        data=self.calculate(data)
        crossover_signal = self.crossover(data['aroon_osc'], 0)
        crossunder_signal = self.crossunder(data['aroon_osc'], 0)
        data['Buy'] = (crossover_signal & data['zlma_side'] & data['ema_side'])
        data['Sell'] = (crossunder_signal & (~data['zlma_side']) & (~data['ema_side']))
        return data[['Buy','Sell']]