# ================================================
#   FILE: main.py
#
#   Drives the execution of the entire application, creates the
#   other parts of the app. Uses pipes to send data back and forth
#


# ==== IMPORTS
from multiprocessing import Process, Pipe

from data import Data
from gui import GUI
from trader import Trader

import os



class MainApp:
    def __init__(self):

        # app variables
        app_variables = {
            'coins': ['btcusd', 'ethusd', 'ltcusd', 'filusd', 'linkusd', 'oxtusd', 'renusd'],
            'timeframe': '1m',
            'display_window': 60,
            'periods_long': 26,
            'periods_short': 12,
            'periods_signal': 9,
            'periods_rsi': 20,
            'ema_smoothing': 2,
            'rsi_crossover': 50,
            'rsi_oversold': 25,
            'rsi_overbought': 75,
            'stop_loss_percent': 0.01,
            'round_amounts': {
                'btcusd': 2,
                'ethusd': 2,
                'ltcusd': 2,
                'filusd': 4,
                'linkusd': 5,
                'oxtusd': 5,
                'renusd': 5
            }
        }

        # create Pipe connections
        dt_conn, td_conn = Pipe()
        dg_conn, gd_conn = Pipe()
        gt_conn, tg_conn = Pipe()

        # initialize client classes
        data_client = Data(app_variables, dt_conn, dg_conn)
        trader_client = Trader(app_variables, td_conn, tg_conn)
        gui_client = GUI(app_variables, gd_conn, gt_conn)

        self.data_process = Process(target=data_client.start, args=())
        self.trader_process = Process(target=trader_client.start, args=())
        self.gui_process = Process(target=gui_client.start, args=())



    def start(self):
        # start processes
        self.data_process.start()
        self.trader_process.start()
        self.gui_process.start()

        self.gui_process.join()



if __name__ == '__main__':
    os.system('clear')

    app = MainApp()
    app.start()
