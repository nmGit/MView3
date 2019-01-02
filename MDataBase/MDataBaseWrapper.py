# Copyright 2018 Noah Meltzer

__author__ = "Noah Meltzer"
__copyright__ = "Copyright 2018"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"

from datetime import datetime
import time
from MDataBase import MDataBase
from PyQt4 import QtGui, QtCore
import traceback
from MWeb import web
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
class MDataBaseWrapper(QThread):
    db_params_updated_signal =pyqtSignal(str, name="db_params_updated_signal")
    db_close_signal = pyqtSignal(name = "db_close_signal")
    db_save_signal = pyqtSignal(name = "db_save_signal")
    def __init__(self, device):
        super(MDataBaseWrapper, self).__init__()

        #print "initializing MDataBase Wrapper",int(QThread.currentThreadId())
        #traceback.print_stack()

        self.device = device
        self.db = None

        self.db_params_updated_signal.connect(self.openDb)
        self.db_close_signal.connect(self.__close)
        self.db_save_signal.connect(self.__save)
        self.restore_state()

        log_location = self.device.getFrame().DataLoggingInfo()['location']
        # Make sure logging is enabled
        if log_location == None:
            self.device.log(False)
            print str(self.device), ": Datalogging not configured. This device's data logging will be turned off."
            return
        try:
            self.openDb()
        except:
            traceback.print_exc()



    def save(self):
        self.db_save_signal.emit()

    def __save(self):
        """This is the save internal to the MDataBaseWrapper. It is not outward facing. This save
        runs in the same thread as MDataBaseWrapper. This is very important. The outward facing save
        is given above, and it uses a signal to trigger this save."""

        try:
            # TODO:Optimize, doesn't need to be done everytime
            columns_with_units = ["capture_time"]
            for col in self.device.getParameters().keys():
                columns_with_units.append(col)
                columns_with_units.append("unit_"+str(col))

            columns = [c.replace(' ', '_') for c in columns_with_units]

            #columns.insert(0, "capture_time")
            #rows = [self.device.getReading(p) if self.device.isDataLoggingEnabled(p) else None for p in self.device.getParameters()]
            rows = []
            for param in self.device.getParameters():
                rows.append(self.device.getReading(param))
                rows.append(self.device.getUnit(param))

            #rows.insert(0,datetime.now().strftime("%m/%d/%Y_%H:%M:%S.%f"))
            rows.insert(0, time.time())

            t1 = time.time()
            #print "Rows:", rows
            if not self.db.save(str(self.device), columns, rows):
                if not self.db.does_table_exist(str(self.device)):
                    # The first column is the time accurate to milliseconds. Making
                    # these entries unique ensures that there can be no two measurements
                    # taken at the same time. More importantly, it speeds up indexing.
                    print "Database table not found. Creating one..."
                    column_types = ['REAL UNIQUE']
                    column_types.extend(['REAL','TEXT']*len(columns))
                    #print "column types",column_types
                    self.db.create_table(columns, column_types, str(self.device))
                elif self.db.findNonExistentColumn(str(self.device), columns) is not None:
                    col_to_add = self.db.findNonExistentColumn(str(self.device), columns)
                    #print "Adding column to database:", col_to_add
                    self.db.addColumn(str(self.device), col_to_add, 'REAL')
            t2 = time.time()
           # print self.device, "time to save:", t2 - t1
        except:

            if(self.db == None):
                self.openDb()
                #print "Opening database..."
                #self.device.configureDataLogging()
                #self.db_params_updated_signal.emit(self.device.getFrame().DataLoggingInfo()['name'])
                pass
            else:
                traceback.print_exc()


    def getVariables(self):
        return self.db.getColumns(str(self.device))[2::2]
    def getUnits(self):
        cols = self.db.getColumns(str(self.device))[3::2]
        return cols;

    def openDb(self):
        log_location = self.device.getFrame().DataLoggingInfo()['location']
        log_name = self.device.getFrame().DataLoggingInfo()['name']
        if(log_location != None):
            self.db = MDataBase(log_location + '\\' + log_name)

    def save_state(self):
        dataname = self.device.getFrame().DataLoggingInfo()['name']
        channels = self.device.getFrame().DataLoggingInfo()['channels']

        location = self.device.getFrame().DataLoggingInfo()['location']

        web.persistentData.persistentDataAccess(dataname, 'DataLoggingInfo', str(self.device), 'name')
        web.persistentData.persistentDataAccess(channels, 'DataLoggingInfo', str(self.device), 'channels')
        web.persistentData.persistentDataAccess(location, 'DataLoggingInfo', str(self.device), 'location')

    def restore_state(self):
        dataname = web.persistentData.persistentDataAccess(None, 'DataLoggingInfo', str(self.device), 'name')
        channels = web.persistentData.persistentDataAccess(None, 'DataLoggingInfo', str(self.device), 'channels')
        location = web.persistentData.persistentDataAccess(None, 'DataLoggingInfo', str(self.device),  'location')
        #Do a sanity check
       # print "device:", self.device
        print "restoring location of", self.device, location
        for nickname in self.device.getFrame().getNicknames():
            if channels == None or nickname not in channels.keys():
                channels = self.device.getFrame().DataLoggingInfo()['channels']
                print "Error when retreiving logged channels in config file, restoring to", channels
        if dataname is None:
            dataname = self.device.getFrame().getTitle()

        self.device.getFrame().DataLoggingInfo()['name'] = dataname
        if channels != None:
            self.device.getFrame().DataLoggingInfo()['channels'] = channels
        self.device.getFrame().DataLoggingInfo()['location'] = location
        pass

    def query(self, fields = '*', *args):
        #traceback.print_stack()
        #print "wrapper args:", args
        return self.db.query(str(self.device), fields, *args)
        
    def configure_data_sets(self):
        pass

    def close(self):
        print "Closing database..."
        self.save_state()
        self.db_close_signal.emit()
    def __close(self):
        if self.db:
            self.db.closeDataSet()
   # def __threadSafeClose(self):


