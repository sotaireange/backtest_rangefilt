from ta import volatility
from ta import trend
import pandas as pd
import numpy as np


class RangeFilterIndicator:
    def __init__(self, data={}):
        self.period = int(data.get('period',25))
        self.multiplier = int(data.get('multiplier',2))
        self.factor = int(data.get('factor',3))
        self.super_trend_period = int(data.get('super_trend_period',3))
        self.atr_multiplier= float(data.get('atr_multiplier',3.3))

    def true_range(self, high, low, close):
        tr1 = high - low
        tr2 = np.abs(high - close.shift(1))
        tr3 = np.abs(low - close.shift(1))
        return np.maximum(tr1, np.maximum(tr2, tr3))

    def atr(self, high, low, close, period):
        tr = self.true_range(high, low, close)
        atr = tr.rolling(window=period).mean()
        return atr

    def smooth_rng(self, data):
        wper = max(1, int(np.floor(self.period / 3) - 1))
        price_diff = abs(data['Close'] - data['Close'].shift(1))
        avrng=trend.SMAIndicator(price_diff, window=self.period).sma_indicator()
        smooth_rng=trend.SMAIndicator(avrng, window=wper).sma_indicator()*self.multiplier

        return smooth_rng


    def rng_filter(self,data, smooth_rng):
        rngfilt = data['Close'].copy()
        x = data['Close'].values
        r = smooth_rng.values
        rngfilt_values = rngfilt.values

        rngfilt_values[0] = x[0]

        for i in range(1, len(data)):
            prev_rngfilt = rngfilt_values[i - 1]
            if x[i] > prev_rngfilt:
                rngfilt_values[i] = prev_rngfilt if (x[i] - r[i]) < prev_rngfilt else (x[i] - r[i])
            else:
                rngfilt_values[i] = prev_rngfilt if (x[i] + r[i]) > prev_rngfilt else (x[i] + r[i])

        rngfilt[:] = rngfilt_values
        return rngfilt


    def super_trend(self, data):
        hl2 = (data['High'] + data['Low']) / 2
        atr = volatility.average_true_range(data['High'], data['Low'], data['Close'], window=self.super_trend_period)
        up = hl2 - self.factor * atr
        down = hl2 + self.factor * atr

        trend_up = pd.Series(np.zeros(len(data)), index=data.index)
        trend_down = pd.Series(np.zeros(len(data)), index=data.index)
        trend = pd.Series(np.zeros(len(data)), index=data.index)
        tsl = pd.Series(np.zeros(len(data)), index=data.index)

        trend_up.iloc[0] = up.iloc[0]
        trend_down.iloc[0] = down.iloc[0]
        tsl.iloc[0] = trend_up.iloc[0]
        for i in range(1, len(data)):
            trend_up.iloc[i] = max(up.iloc[i], trend_up.iloc[i - 1]) if data['Close'].iloc[i - 1] > trend_up.iloc[i - 1] else up.iloc[i]
            trend_down.iloc[i] = min(down.iloc[i], trend_down.iloc[i - 1]) if data['Close'].iloc[i - 1] < trend_down.iloc[i - 1] else down.iloc[i]
            trend.iloc[i] = 1 if data['Close'].iloc[i] > trend_down.iloc[i - 1] else -1 if data['Close'].iloc[i] < trend_up.iloc[i - 1] else trend.iloc[i - 1]
            tsl.iloc[i] = trend_up.iloc[i] if trend.iloc[i] == 1 else trend_down.iloc[i]


        return tsl




    def generate_signals(self, data):
        smooth_rng_values = self.smooth_rng(data)
        filt = self.rng_filter(data, smooth_rng_values)
        tsl = self.super_trend(data)
        long_condition = self.crossunder(tsl,filt)
        short_condition = self.crossover(tsl,filt)

        return long_condition, short_condition



    def crossover(self, series: pd.Series, level=0):
        return (series.shift(1) <= level.shift(1)) & (series >= level) & (series.shift(1) < level)

    def crossunder(self, series, level=0):
        return (series.shift(1) >= level.shift(1)) & (series <= level) & (series.shift(1) > level)

    def signal(self, df):
        long_condition, short_condition = self.generate_signals(df)
        return pd.DataFrame({
            'Buy': long_condition,
            'Sell': short_condition
        }, index=df.index)