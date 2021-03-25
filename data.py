# ================================================
#   FILE: data.py
#
#   Drives the computation part of the application, receives raw data from the
#   trader process and performes comoputations. Sends finalized data to
#   the gui process and sends any buy or sell signals to the trader process
#


# ==== IMPORTS
from resources.message import Message



class Data:
    def __init__(self, app_vars, t_conn, g_conn):
        self.trader_connection = t_conn
        self.gui_connection = g_conn

        self.app_variables = app_vars



    # mainloop
    def start(self):

        # check for incoming messages
        def checkForMessages():
            if self.gui_connection.poll():
                try:
                    msg = self.gui_connection.recv()
                    self.handleMessage(msg)
                except:
                    pass


            if self.trader_connection.poll():
                try:
                    msg = self.trader_connection.recv()
                    self.handleMessage(msg)
                except:
                    pass


        # mainloop
        while True:
            # check for incoming messages
            checkForMessages()




    # creates a Message object and sends it through the
    # corresponding pipe
    def sendMessage(self, to, m='', d=''):
        message = Message(m, d)

        if (to == 'trader'):
            #print('MESSAGE: data --> trader')
            self.trader_connection.send(message)

        if (to == 'gui'):
            #print('MESSAGE: data --> gui')
            self.gui_connection.send(message)



    # handles incoming messages
    def handleMessage(self, m):

        if (m.message == 'calc-data'):
            #print('DATA: calculating data...')
            self.calculateData(m.data)      # m.data is a dict {'coin': [candles]}

        pass


    # loop through active coins and calculate all data
    # send the data to ui to display
    # check for buy and sell signals --> send message back to trader if signals
    def calculateData(self, d):

        out_data = {}

        for coin in d:
            out_data[coin] = {}

            close_prices_all = []
            for candle in d[coin]:
                close_prices_all.append(candle[4])


            close_prices = close_prices_all[:(self.app_variables['display_window'])]
            close_prices.reverse()
            out_data[coin]['close_prices'] = close_prices

            out_data[coin]['emas_long'] = self.calculateFullEMAs(close_prices_all, self.app_variables['periods_long'])
            out_data[coin]['emas_short'] = self.calculateFullEMAs(close_prices_all, self.app_variables['periods_short'])
            out_data[coin]['macds'] = self.calculateFullMACDs(out_data[coin]['emas_long'], out_data[coin]['emas_short'])
            out_data[coin]['macds_signal'] = self.calculateFullMACDSignals(out_data[coin]['macds'], self.app_variables['periods_signal'])
            out_data[coin]['rsis'] = self.calculateFullRSIs(d[coin], self.app_variables['periods_rsi'])

            self.evaluateMarketConditions(coin, out_data[coin])


        self.sendMessage('gui', m='display-data', d=out_data)



    # calculate exponential moving average for the given periods
    def calculateFullEMAs(self, prices, periods):
        window = self.app_variables['display_window']

        def calcEMA(p, e_last, d):
            smoothing = self.app_variables['ema_smoothing']
            return ((p * (smoothing / (1 + d))) + (e_last * (1 - (smoothing / (1 + d)))))

        p = prices[:(window + periods)]
        p.reverse()

        ema_last = (sum(p[:periods]) / periods)
        out_data = []

        for price in p[periods:]:
            ema = calcEMA(price, ema_last, periods)
            out_data.append(ema)
            ema_last = ema

        return out_data





    # calculate moving average convergence divergence values
    def calculateFullMACDs(self, longs, shorts):
        macds = []

        for i in range(0, len(longs)):
            macds.append(shorts[i] - longs[i])

        return macds





    # calculate macd signal line --> moving average of macd
    def calculateFullMACDSignals(self, macds, periods):
        window = self.app_variables['display_window']

        def calcEMA(p, e_last, d):
            smoothing = self.app_variables['ema_smoothing']
            return ((p * (smoothing / (1 + d))) + (e_last * (1 - (smoothing / (1 + d)))))

        macd_last = macds[0]
        out_data = []

        for macd in macds[1:]:
            avg_macd = calcEMA(macd, macd_last, periods)
            out_data.append(avg_macd)
            macd_last = avg_macd

        n = window - len(out_data)
        temp = [out_data[0] for i in range(0, n)]
        return (temp + out_data)




    # calculate relative strength index for the given periods
    def calculateFullRSIs(self, candles, periods):
        window = self.app_variables['display_window']
        p = candles[:(window + periods)]
        p.reverse()

        out_data = []

        def calcRS(c):
            up = []
            down = []

            for candle in c:
                chng = candle[1] - candle[4]

                if chng > 0:
                    down.append(chng)
                else:
                    up.append(-chng)

            avgUp = (sum(up) / periods)
            avgDown = (sum(down) / periods)
            return (avgUp / (1 if avgDown == 0 else avgDown))



        for i in range(periods, (window + periods)):
            rs = calcRS(candles[i - periods:(i)])
            rsi = 100 - (100 / (1 + rs))
            out_data = [rsi] + out_data

        return out_data



    def evaluateMarketConditions(self, coin, d):

        # check if price > ema_short > ema_long
        def checkPriceEMA(_d):
            if ((_d['close_prices'][-1] > _d['emas_short'][-1]) and (_d['emas_short'][-1] > _d['emas_long'][-1])):
                return True
            return False

        # check if macd line is above the macd signal line
        def checkMACD(_d):
            if (_d['macds'][-1] > _d['macds_signal'][-1]):
                return True
            return False

        # check if rsi is above the crossover value --> indicatind a positive trend
        def checkRSI(_d):
            if (_d['rsis'][-1] > self.app_variables['rsi_crossover']):
                return True
            return False

        # check if macd line crosses from below to above the macd signal line
        def checkMACDCrossoverBuy(_d):
            if (_d['macds'][-1] > _d['macds_signal'][-1]) and (_d['macds'][-2] < _d['macds_signal'][-2]):
                return True
            return False

        # check if macd line crosses from above to below the macd signal line
        def checkMACDCrossoverSell(_d):
            if (_d['macds'][-1] < _d['macds_signal'][-1]) and (_d['macds'][-2] > _d['macds_signal'][-2]):
                return True
            return False

        # check if rsi crosses from below to above the crossover value --> indicating shift to positive trend
        def checkRSICrossoverBuy(_d):
            if (_d['rsis'][-1] > self.app_variables['rsi_crossover']) and (_d['rsis'][-2] < self.app_variables['rsi_crossover']):
                return True
            return False

        # check if rsi crosses from above to below the crossover value --> indicating shift to negative trend
        def checkRSICrossoverSell(_d):
            if (_d['rsis'][-1] < self.app_variables['rsi_crossover']) and (_d['rsis'][-2] > self.app_variables['rsi_crossover']):
                return True
            return False


        def checkPriceEMACrossoverBuy(_d):
            if not((_d['close_prices'][-2] > _d['emas_short'][-2]) and (_d['emas_short'][-2] > _d['emas_long'][-2])):
                return True
            return False




        # evaluate buy conditions
        if checkPriceEMA(d):
            if checkMACDCrossoverBuy(d) and checkRSI(d):
                self.sendMessage('trader', 'buy-signal-macd', coin)
                return

            if checkRSICrossoverBuy(d) and checkMACD(d):
                self.sendMessage('trader', 'buy-signal-rsi', coin)
                return

            if checkPriceEMACrossoverBuy(d) and checkMACD(d) and checkRSI(d):
                self.sendMessage('trader', 'buy-signal-ema', coin)
                return



        if checkMACDCrossoverSell(d):
            self.sendMessage('trader', 'sell-signal-macd', coin)
            return

        if checkRSICrossoverSell(d):
            self.sendMessage('trader', 'sell-signal-rsi', coin)
            return
