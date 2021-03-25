# ================================================
#   FILE: gui.py
#
#   Handles displaying data in a graphical format, easier to digest quickly
#   and also allows for manual button input for buying and selling coins
#





# ==== MODULES
from resources.message import Message

import tkinter as tk
from tkinter.ttk import *
import matplotlib
matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg






class GUI(tk.Frame):
    def __init__(self, app_vars, d_conn, t_conn):
        self.data_connection = d_conn
        self.trader_connection = t_conn

        self.app_variables = app_vars

        self.refresh_rate = 5000    # 5 seconds

        # signal line data used to display in the graphs
        self.zero_list = [0 for i in range(0, app_vars['display_window'])]
        self.rsi_crossover_list = [app_vars['rsi_crossover'] for i in range(0, app_vars['display_window'])]
        self.rsi_oversold_list = [app_vars['rsi_oversold'] for i in range(0, app_vars['display_window'])]
        self.rsi_overbought_list = [app_vars['rsi_overbought'] for i in range(0, app_vars['display_window'])]






    # creates the main TK window, done here instead of __init__ so that it is part
    # of its own process and therefor allows for proper Pipe communication. Tk can
    # throw an error when using multiprocessing if not done this way.
    def start(self):
        self.root = tk.Tk(className="Palio")
        tk.Frame.__init__(self, self.root)

        # set interval for checking for messages
        self.root.after(1000, self.checkForMessages)

        # initialize the windows
        self.initializeWindows()

        # start the mainloop
        self.root.mainloop()




    # checks for incoming messages from the data and trader processes
    def checkForMessages(self):

        if self.data_connection.poll():
            try:
                msg = self.data_connection.recv()
                self.handleMessage(msg)
            except:
                pass


        if self.trader_connection.poll():
            try:
                msg = self.trader_connection.recv()
                self.handleMessage(msg)
            except:
                pass

        self.root.after(self.refresh_rate, self.checkForMessages)




    # creates a message object and routes that through the correct
    # Pipe
    def sendMessage(self, to, m='', d=''):
        message = Message(m, d)

        if (to == 'trader'):
            #print('MESSAGE: gui --> trader')
            self.trader_connection.send(message)

        if (to == 'data'):
            #print('MESSAGE: gui --> data')
            self.data_connection.send(message)



    # handles incoming messages
    def handleMessage(self, m):

        if (m.message == 'display-data'):
            self.displayData(m.data)





    # creates all the labels and buttons for the main window
    # creates Toplevel windows for each active coin
    def initializeWindows(self):
        main_label = tk.Label(self.root, text='Palio - Crypto Trading Bot', fg='black').grid(row=0, column=0, columnspan=3)

        r = 1
        btc_label = tk.Label(self.root, text='BTCUSD', fg='black').grid(row=r, column=0)
        btc_buy_btn = tk.Button(self.root, text='BUY', fg='black', command= lambda: self.sendMessage('trader', 'buy-signal-manual', 'btcusd')).grid(row=r, column=1)
        btc_sell_btn = tk.Button(self.root, text='SELL', fg='black', command= lambda: self.sendMessage('trader', 'sell-signal-manual', 'btcusd')).grid(row=r, column=2)

        r += 1
        eth_label = tk.Label(self.root, text='ETHUSD', fg='black').grid(row=r, column=0)
        eth_buy_btn = tk.Button(self.root, text='BUY', fg='black', command= lambda: self.sendMessage('trader', 'buy-signal-manual', 'ethusd')).grid(row=r, column=1)
        eth_sell_btn = tk.Button(self.root, text='SELL', fg='black', command= lambda: self.sendMessage('trader', 'sell-signal-manual', 'ethusd')).grid(row=r, column=2)

        r += 1
        ltc_label = tk.Label(self.root, text='LTCUSD', fg='black').grid(row=r, column=0)
        ltc_buy_btn = tk.Button(self.root, text='BUY', fg='black', command= lambda: self.sendMessage('trader', 'buy-signal-manual', 'ltcusd')).grid(row=r, column=1)
        ltc_sell_btn = tk.Button(self.root, text='SELL', fg='black', command= lambda: self.sendMessage('trader', 'sell-signal-manual', 'ltcusd')).grid(row=r, column=2)

        r += 1
        fil_label = tk.Label(self.root, text='FILUSD', fg='black').grid(row=r, column=0)
        fil_buy_btn = tk.Button(self.root, text='BUY', fg='black', command= lambda: self.sendMessage('trader', 'buy-signal-manual', 'filusd')).grid(row=r, column=1)
        fil_sell_btn = tk.Button(self.root, text='SELL', fg='black', command= lambda: self.sendMessage('trader', 'sell-signal-manual', 'filusd')).grid(row=r, column=2)

        r += 1
        link_label = tk.Label(self.root, text='LINKUSD', fg='black').grid(row=r, column=0)
        link_buy_btn = tk.Button(self.root, text='BUY', fg='black', command= lambda: self.sendMessage('trader', 'buy-signal-manual', 'linkusd')).grid(row=r, column=1)
        link_sell_btn = tk.Button(self.root, text='SELL', fg='black', command= lambda: self.sendMessage('trader', 'sell-signal-manual', 'linkusd')).grid(row=r, column=2)

        r += 1
        oxt_label = tk.Label(self.root, text='OXTUSD', fg='black').grid(row=r, column=0)
        oxt_buy_btn = tk.Button(self.root, text='BUY', fg='black', command= lambda: self.sendMessage('trader', 'buy-signal-manual', 'oxtusd')).grid(row=r, column=1)
        oxt_sell_btn = tk.Button(self.root, text='SELL', fg='black', command= lambda: self.sendMessage('trader', 'sell-signal-manual', 'oxtusd')).grid(row=r, column=2)

        r += 1
        ren_label = tk.Label(self.root, text='RENUSD', fg='black').grid(row=r, column=0)
        ren_buy_btn = tk.Button(self.root, text='BUY', fg='black', command= lambda: self.sendMessage('trader', 'buy-signal-manual', 'renusd')).grid(row=r, column=1)
        ren_sell_btn = tk.Button(self.root, text='SELL', fg='black', command= lambda: self.sendMessage('trader', 'sell-signal-manual', 'renusd')).grid(row=r, column=2)



        # create Toplevel windows for each active coin
        self.coin_windows = {}

        for coin in self.app_variables['coins']:
            d = {
                'WINDOW': tk.Toplevel(self.master),
                'FIGURE': Figure(figsize=(6,8), dpi=100),
                'X_VALS': [i for i in range(-self.app_variables['display_window'], 0)]
            }

            spec = matplotlib.gridspec.GridSpec(
                ncols = 1,
                nrows = 3,
                height_ratios = [2,1,1],
                hspace=0.3
            )

            d['PLOT_A'] = d['FIGURE'].add_subplot(spec[0])
            d['PLOT_B'] = d['FIGURE'].add_subplot(spec[1])
            d['PLOT_C'] = d['FIGURE'].add_subplot(spec[2])
            d['PLOT_A'].set_title('PRICES')
            d['PLOT_B'].set_title('MACD')
            d['PLOT_C'].set_title('OSCILLATORS')
            d['PLOT_C'].set_ylim([0, 100])

            d['CANVAS'] = FigureCanvasTkAgg(d['FIGURE'], d['WINDOW'])
            d['CANVAS'].get_tk_widget().grid(row=0, column=0)
            d['WINDOW'].title(coin.upper())
            self.coin_windows[coin] = d





    # displays data to the corresponding plots and windows
    # computation is done in the data process and sent here via Pipe
    def displayData(self, d):
        for coin in d:
            self.coin_windows[coin]['PLOT_A'].clear()
            self.coin_windows[coin]['PLOT_B'].clear()
            self.coin_windows[coin]['PLOT_C'].clear()

            self.coin_windows[coin]['PLOT_A'].set_title('PRICES')
            self.coin_windows[coin]['PLOT_B'].set_title('MACD')
            self.coin_windows[coin]['PLOT_C'].set_title('OSCILLATORS')
            self.coin_windows[coin]['PLOT_C'].set_ylim([0, 100])

            self.coin_windows[coin]['PLOT_A'].plot(self.coin_windows[coin]['X_VALS'], d[coin]['close_prices'], color='blue', linewidth=0.5, label='close')
            self.coin_windows[coin]['PLOT_A'].plot(self.coin_windows[coin]['X_VALS'], d[coin]['emas_long'], color='red', linewidth=0.5, label='ema long')
            self.coin_windows[coin]['PLOT_A'].plot(self.coin_windows[coin]['X_VALS'], d[coin]['emas_short'], color='green', linewidth=0.5, label='ema short')

            self.coin_windows[coin]['PLOT_B'].plot(self.coin_windows[coin]['X_VALS'], self.zero_list, color='blue', linestyle=':', linewidth=0.5)
            self.coin_windows[coin]['PLOT_B'].plot(self.coin_windows[coin]['X_VALS'], d[coin]['macds'], color='green', linewidth=0.5, label='macd')
            self.coin_windows[coin]['PLOT_B'].plot(self.coin_windows[coin]['X_VALS'], d[coin]['macds_signal'], color='red', linewidth=0.5, label='signal')

            self.coin_windows[coin]['PLOT_C'].plot(self.coin_windows[coin]['X_VALS'], self.rsi_crossover_list, color='orange', linestyle=':', linewidth=0.5)
            self.coin_windows[coin]['PLOT_C'].plot(self.coin_windows[coin]['X_VALS'], self.rsi_oversold_list, color='blue', linestyle=':', linewidth=0.5)
            self.coin_windows[coin]['PLOT_C'].plot(self.coin_windows[coin]['X_VALS'], self.rsi_overbought_list, color='blue', linestyle=':', linewidth=0.5)
            self.coin_windows[coin]['PLOT_C'].plot(self.coin_windows[coin]['X_VALS'], d[coin]['rsis'], color='green', linewidth=0.5, label='rsi')

            self.coin_windows[coin]['PLOT_A'].legend(loc='upper left')
            self.coin_windows[coin]['PLOT_B'].legend(loc='upper left')
            self.coin_windows[coin]['PLOT_C'].legend(loc='upper left')

            self.coin_windows[coin]['CANVAS'].draw()
