# Copyright 2018 Noah Meltzer

__author__ = "Noah Meltzer"
__copyright__ = "Copyright 2018"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"


from MDataBase import MDataBase

from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
class MDataBaseWrapper2(QThread):
    db_params_updated_signal =pyqtSignal(str, name="db_params_updated_signal")
    db_close_signal = pyqtSignal(name = "db_close_signal")
    db_save_signal = pyqtSignal(name = "db_save_signal")
    def __init__(self, log_path):
        super(MDataBaseWrapper2, self).__init__()

        #print "initializing MDataBase Wrapper",int(QThread.currentThreadId())
        #traceback.print_stack()


        self.db = None

        self.db_params_updated_signal.connect(self.openDb)
        self.db_close_signal.connect(self.__close)


        # Make sure logging is enabled

        self.openDb(log_path)

    def getVariables(self, table_name):
        return self.db.getColumns(str(table_name))[2::2]

    def getUnits(self):
        cols = self.db.getColumns(str(self.device))[3::2]

    def openDb(self, log_path):
        self.db = MDataBase(log_path)

    def query(self, table, fields, *args):
        return self.db.query(table, fields, *args)
    def getTables(self):
        return self.db.getTables()
    def configure_data_sets(self):
        pass

    def close(self):
        print "Closing database..."
        self.db_close_signal.emit()
    def __close(self):
        if self.db:
            self.db.closeDataSet()
   # def __threadSafeClose(self):


