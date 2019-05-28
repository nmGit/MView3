# Copyright 2018 Noah Meltzer

__author__ = "Noah Meltzer"
__copyright__ = "Copyright 2018"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"


from MDataBase import MDataBase

from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
class MSQLiteDataBaseWrapper(QThread):
    db_params_updated_signal =pyqtSignal(str, name="db_params_updated_signal")
    db_close_signal = pyqtSignal(name = "db_close_signal")
    db_insert_signal = pyqtSignal(str, list, list, name = "db_insert_signal")
    def __init__(self, log_path):
        super(MDataBaseWrapper2, self).__init__()

        self.db = None

        self.db_params_updated_signal.connect(self.openDb)
        self.db_close_signal.connect(self.__close)
        self.db_insert_signal.connect(self.__insert)
        self.openDb(log_path)

    def getVariables(self, table_name):
        return self.db.getColumns(str(table_name))[2::2]

    def getUnits(self):
        cols = self.db.getColumns(str(self.device))[3::2]

    def openDb(self, log_path):
        self.db = MDataBase(log_path)

    def insert(self, table, columns, rows):
        self.db_insert_signal.emit(table, columns, rows)

    def __insert(self, table, columns, rows):
        self.sql_insert(table, columns, rows)

    def __sql_insert(self, table, columns, rows):
        if not self.db.dave(table, columns, rows):
            if not self.db.does_table_exist(table):


    def query(self, table, fields, *args):
        '''
        Returns the result of a query
        :param table: The name of the table to query
        :param fields: The fields to query
        :param args:
        +------------+------------+-----------+-------------+-----------------------------------------------+
        | arg[0]     | arg[1]                 |arg[2]|arg[3]| Description                                   |
        +============+========================+=====+=======+===============================================+
        | "all"      |            -                         | Grab all data in specified columns            |
        +------------+------------------------+-----+-------+-----------------------------------------------+
        | "last"     |            -                         | Grab last committed data in specified columns |
        +------------+------------------------+-----+-------+-----------------------------------------------+
        | "range"    | Field over which       |     |       |                                               |
        |            | the range is specified | Min | Max   | Return everything within the specified range  |
        +------------+------------+-----------+-------------+-----------------------------------------------+
        :return: The query response
        '''
        return self.db.query(table, fields, *args)

    def getTables(self):
        return self.db.getTables()

    def isOpen(self):
        return self.db.isOpen()

    def configure_data_sets(self):
        pass

    def close(self):
        print "Closing database..."
        self.db_close_signal.emit()

    def __close(self):
        if self.db and self.db.isOpen():
            self.db.closeDataSet()
   # def __threadSafeClose(self):


