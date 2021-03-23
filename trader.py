





# ==== MODULES
from resources.message import Message






class Trader:
    def __init__(self, app_vars, d_conn, g_conn):
        self.data_connection = d_conn
        self.gui_connection = g_conn

        self.app_variables = app_vars


    # mainloop
    def start(self):

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
    def sendMessage(to, m='', d=''):
        message = Message(m, d)

        if (to == 'trader'):
            self.trader_connection.send(message)

        if (to == 'gui'):
            self.gui_connection.send(message)


    # handles incoming messages
    def handleMessage(self, m):

        pass
