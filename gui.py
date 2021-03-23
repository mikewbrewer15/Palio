





# ==== MODULES
from resources.message import Message


class GUI:
    def __init__(self, app_vars, d_conn, t_conn):
        self.data_connection = d_conn
        self.trader_connection = t_conn

        self.app_variables = app_vars




    def start(self):




        pass




    def sendMessage(to, m='', d=''):
        message = Message(m, d)

        if (to == 'trader'):
            self.trader_connection.send(message)

        if (to == 'gui'):
            self.gui_connection.send(message)



    def handleMessage(self, m):

        if (m.message == 'display-data'):
            print('displaying data')

        pass
