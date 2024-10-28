
import backtrader as bt




class BackTestStrategy(bt.Strategy):
    params= (
        ('stop_loss',0.016),
        ('take_profit',0.016),
        ('signal',None)
    )
    def __init__(self):
        self.signals=self.params.signal
        self.buy_price=None
        self.sell_price=None
        self.order = None

        self.total_profit = 0
        self.total_trades = 0
        self.profit_trades = 0
        self.loss_trades = 0


    def next(self):
        timestamp = self.data.datetime.datetime(0)
        # Проверяем наличие сигнала на покупку
        if timestamp in self.signals.index:
            signal_row = self.signals.shift(1).loc[timestamp]
            if self.position.size > 0:  # Лонг позиция
                if self.data.close[0] >= self.buy_price * (1 + self.params.take_profit) or \
                        self.data.close[0] <= self.buy_price * (1 - self.params.stop_loss):
                    self.close()
                    self.order = None
                    #print(f"CLOSE LONG at {self.data.close[0]}")

            elif self.position.size < 0:  # Шорт позиция
                if self.data.close[0] <= self.sell_price * (1 - self.params.take_profit) or \
                        self.data.close[0] >= self.sell_price * (1 + self.params.stop_loss):
                    self.close()
                    self.order = None
                    #print(f"CLOSE SHORT at {self.data.close[0]}")

            if signal_row['Buy'] == True and self.position.size <= 0:
                if self.position.size < 0:
                    self.close()
                self.buy_price = self.data.high[0]
                self.order = self.buy(size=(100/self.data.close[0]))

            elif signal_row['Sell'] == True and self.position.size >= 0:
                if self.position.size > 0:
                    self.close()
                self.sell_price = self.data.low[0]
                self.order = self.sell(size=(100/self.data.close[0]))


def backtest_coin(df,signals,tp,sl):
    cerebro = bt.Cerebro()
    data=bt.feeds.PandasData(dataname=df)
    cerebro.addstrategy(BackTestStrategy,signal=signals,take_profit=tp,stop_loss=sl)
    cerebro.adddata(data)
    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer,_name='tradeanalyzer')
    strats=cerebro.run()
    res= strats[0].analyzers.getbyname('tradeanalyzer').get_analysis()
    return res