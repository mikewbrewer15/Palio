# ================================================
#   FILE: trader.py
#
#   Handles communication with the API and sends raw data
#   to the data process for computation. Receives buy and sell
#   signal info from the data process and the gui (manually) and
#   places orders through the API.
#


# ==== IMPORTS
from resources.message import Message
from playsound import playsound

import time
import requests, json
import pandas as pd





# ==== GLOBAL VARIABLES AND FUNCTIONS

COLORS = {
    'ERROR': '\u001b[31m',
    'RESET': '\u001b[0m',

    'GREEN': '\u001b[32m',
    'RED': '\u001b[31m',
    'YELLOW': '\u001b[33m',
    'CYAN': '\u001b[36m'
}




def PRINT_BUY_EVENT(coin, order, t):
    print(f"BUY_EVENT[{t}]::{coin.upper()} --> bid: {COLORS['YELLOW']}$ {order['bid']}{COLORS['RESET']}   stop_loss: {COLORS['RED']}$ {order['stop-loss']}{COLORS['RESET']}")




def PRINT_SELL_EVENT(coin, order, t):

    def calcPercent(bid, ask):
        return ((ask - bid) / bid)


    percent = round(calcPercent(order['bid'], order['ask']), 4)

    if (order['ask'] > order['bid']):
        print(f"SOLD[{t}]::{coin.upper()} --> bid: {COLORS['YELLOW']}$ {order['bid']}{COLORS['RESET']}   ask: {COLORS['GREEN']}$ {order['ask']}   {percent * 100} %{COLORS['RESET']}")
    else:
        print(f"SOLD[{t}]::{coin.upper()} --> bid: {COLORS['YELLOW']}$ {order['bid']}{COLORS['RESET']}   ask: {COLORS['RED']}$ {order['ask']}   {percent * 100} %{COLORS['RESET']}")





def DISPLAY_ORDERS(orders):
    print('- - - - - - - - - - - ACTIVE ORDERS - - - - - - - - - - -')
    for coin in orders:
        if (orders[coin]['stop-loss'] > orders[coin]['bid']):
            print(f"{coin.upper()} --> bid: {COLORS['YELLOW']}$ {orders[coin]['bid']}{COLORS['RESET']}   stop_loss: {COLORS['GREEN']}$ {orders[coin]['stop-loss']}{COLORS['RESET']}")
        else:
            print(f"{coin.upper()} --> bid: {COLORS['YELLOW']}$ {orders[coin]['bid']}{COLORS['RESET']}   stop_loss: {COLORS['RED']}$ {orders[coin]['stop-loss']}{COLORS['RESET']}")
    print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - -')







# ==== TRADER CLASS

class Trader:
    def __init__(self, app_vars, d_conn, g_conn):
        self.data_connection = d_conn   # communication with the data process
        self.gui_connection = g_conn    # communication with the gui process

        self.app_variables = app_vars
        self.active_coins = app_vars['coins']
        self.base_url = 'https://api.gemini.com/'

        self.active_orders = {}


    # mainloop
    def start(self):

        self.pullCandleData()

        # 60 second refresh time for pulling candle data
        refresh_rate = 60
        refresh_last = time.time()

        display_rate = 30
        display_last = time.time()

        # check for incoming messages
        def checkForMessages():

            if self.data_connection.poll():
                try:
                    msg = self.data_connection.recv()
                    self.handleMessage(msg)
                except:
                    pass

            if self.gui_connection.poll():
                try:
                    msg = self.gui_connection.recv()
                    self.handleMessage(msg)
                except:
                    pass



        # mainloop
        while True:
            # check for incoming messages
            checkForMessages()

            t = time.time()
            if ((t - refresh_last) > refresh_rate):
                self.pullCandleData()
                refresh_last = t



            # update and display active orders
            if (self.active_orders):
                t = time.time()
                if ((t - display_last) > display_rate):

                    temp = self.active_orders.copy()
                    for coin in temp:
                        endpoint = f'v2/ticker/{coin}'

                        try:
                            response = requests.get(self.base_url + endpoint)
                            ticker = response.json()
                            ask = float(ticker['ask'])

                        except:
                            pass

                        if (ask < self.active_orders[coin]['stop-loss']):
                            self.handleMessage(Message('sell-signal-stoploss', coin))
                            continue


                        new_stop = self.calculateStopLoss(ask)
                        if (new_stop > self.active_orders[coin]['stop-loss']):
                            self.active_orders[coin]['stop-loss'] = round(new_stop, self.app_variables['round_amounts'][coin])


                    DISPLAY_ORDERS(self.active_orders)
                    display_last = t





    # creates a Message object and sends it through the
    # corresponding pipe
    def sendMessage(self, to, m='', d=''):
        message = Message(m, d)

        if (to == 'data'):
            #print('MESSAGE: trader --> data')
            self.data_connection.send(message)

        if (to == 'gui'):
            #print('MESSAGE: trader --> gui')
            self.gui_connection.send(message)





    # handles incoming messages
    def handleMessage(self, m):

        # handle buy signal
        if ('buy-signal' in m.message):
            if not(m.data in self.active_orders):
                type = m.message.split('-')[2]
                bid = self.placeBuyOrder(m.data)

                if (bid):
                    self.active_orders[m.data] = {}
                    self.active_orders[m.data]['bid'] = bid
                    self.active_orders[m.data]['stop-loss'] = round(self.calculateStopLoss(bid), self.app_variables['round_amounts'][m.data])
                    self.active_orders[m.data]['buy-type'] = type
                    playsound('resources/sounds/notification.mp3')
                    PRINT_BUY_EVENT(m.data, self.active_orders[m.data], type)

            return


        # handle sell signal
        if ('sell-signal' in m.message):
            if (m.data in self.active_orders):
                type = m.message.split('-')[2]
                ask = self.placeSellOrder(m.data)

                if ((type == 'rsi') or (type == 'macd')) and (ask < self.active_orders[m.data]['bid']):
                    return

                self.active_orders[m.data]['ask'] = ask
                self.active_orders[m.data]['sell-type'] = type
                self.active_orders[m.data]['profit'] = (self.active_orders[m.data]['ask'] - self.active_orders[m.data]['bid'])
                playsound('resources/sounds/caching.mp3')
                PRINT_SELL_EVENT(m.data, self.active_orders[m.data], type)

                # create data frame for event --> append to events.csv
                d = {
                    'coin': m.data,
                    'buy-type': self.active_orders[m.data]['buy-type'],
                    'sell-type': self.active_orders[m.data]['sell-type'],
                    'buy-price': self.active_orders[m.data]['bid'],
                    'sell-price': self.active_orders[m.data]['ask'],
                    'timeframe': self.app_variables['timeframe'],
                    'sl-percent': self.app_variables['stop_loss_percent']
                }

                cols = ['coin', 'buy-type', 'sell-type', 'buy-price', 'sell-price', 'timeframe']

                df = pd.DataFrame(columns=cols)
                df = df.append(d, ignore_index=True)
                df.to_csv('database/events.csv', mode='a', header=False, index=False)


                self.active_orders.pop(m.data)

            return






    # pulls the raw candle data for each active coin and sends
    # the raw data to the data process
    def pullCandleData(self):
        #print('pulling candle data...')
        out_data = {}
        timeframe = self.app_variables['timeframe']

        for coin in self.active_coins:

            try:
                endpoint = f"v2/candles/{coin}/{timeframe}"
                time.sleep(1)   # wait one second
                response = requests.get(self.base_url + endpoint)
                candles = response.json()
                out_data[coin] = candles

            except Exception as e:
                print(e)
                pass

        if (out_data):
            self.sendMessage('data', 'calc-data', out_data)



    # get bid price from api
    def placeBuyOrder(self, coin):
        endpoint = f'v2/ticker/{coin}'

        try:
            response = requests.get(self.base_url + endpoint)
            ticker = response.json()
            bid = float(ticker['bid'])

            return bid
        except:
            pass

        return False




    # get ask price from api
    def placeSellOrder(self, coin):
        endpoint = f'v2/ticker/{coin}'

        try:
            response = requests.get(self.base_url + endpoint)
            ticker = response.json()
            ask = float(ticker['ask'])

            return ask
        except:
            pass

        return False



    # calculate stop loss price
    def calculateStopLoss(self, price):
        return (price - (price * self.app_variables['stop_loss_percent']))
