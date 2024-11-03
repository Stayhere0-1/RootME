import mysql.connector
from mysql.connector  import errorcode

class database : 
    def __init__(self, config):
        self.config = config
    def get_con(self):

        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except mysql.connector.Error as error:
            if error.errno  == errorcode.ER_ACCESS_DENIED_ERROR:
                raise  Exception("Something is wrong with your user name or password")
            elif error.errno == errorcode.ER_BAD_DB_ERROR:
                raise Exception("Database does not exist")
            else:
                raise Exception(error)
            

