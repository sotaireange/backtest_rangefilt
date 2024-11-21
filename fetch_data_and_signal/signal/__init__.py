from .aroon_indicator import AroonOscillator
from .rangefilt import RangeFilterIndicator


def get_signal(df,data_signal,indicator='rangefilt'):
    if indicator=='rangefilt':
        Indicator=RangeFilterIndicator(data_signal)
        result=Indicator.signal(df)
    elif indicator=='aroon':
        Indicator=AroonOscillator(data_signal)
        result=Indicator.get_signal(df)
    return result