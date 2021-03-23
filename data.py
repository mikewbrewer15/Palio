# ================================================
#   FILE: data.py
#
#   Drives the computation part of the application, waits until the
#   trader process sends a message to update
#


# ==== MODULES
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




    # creates a Message object and sends it through the corresponding
    # pipe
    def sendMessage(self, to, m='', d=''):
        message = Message(m, d)

        if (to == 'trader'):
            self.trader_connection.send(message)

        if (to == 'gui'):
            self.gui_connection.send(message)



    # handles incoming messages
    def handleMessage(self, m):


        pass
