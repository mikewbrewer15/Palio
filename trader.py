





# ==== MODULES
from resources.message import Message
import time
import requests, json




class Trader:
    def __init__(self, app_vars, d_conn, g_conn):
        self.data_connection = d_conn
        self.gui_connection = g_conn

        self.app_variables = app_vars
        self.active_coins = app_vars['coins']
        self.base_url = 'https://api.gemini.com/'


    # mainloop
    def start(self):

        self.pullCandleData()

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





    # creates a Message object and sends it through the
    # corresponding pipe
    def sendMessage(self, to, m='', d=''):
        message = Message(m, d)

        if (to == 'data'):
            print('MESSAGE: trader --> data')
            self.data_connection.send(message)

        if (to == 'gui'):
            print('MESSAGE: trader --> gui')
            self.gui_connection.send(message)


    # handles incoming messages
    def handleMessage(self, m):

        pass


    def pullCandleData(self):
        print('pulling candle data...')
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
