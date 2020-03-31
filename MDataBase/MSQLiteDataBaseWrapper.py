# Copyright 2018 Noah Meltzer

__author__ = "Noah Meltzer"
__copyright__ = "Copyright 2018"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"


from MDataBase import MDataBase

from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QSemaphore
import Queue
from datetime import datetime
import time

class MSQLiteDataBaseWrapper(QThread):
    db_request_sem = QSemaphore(1)
    db_task_ready_sem = QSemaphore(1)
    db_request_sem.acquire()
    #db_task_ready_sem.acquire()

    db_done_loading = pyqtSignal()
    request_processed = pyqtSignal(list)
    def __init__(self, log_path):
        super(MSQLiteDataBaseWrapper, self).__init__()

        self.db = None
        self.log_path = log_path

        self.table = None
        self.columns = None
        self.rows = None
        self.fields = None
        self.args = None
        self.query_return = None

        self.keep_going = True

        self.request_type = None

        self.response_queue = Queue.Queue()
        self.request_queue = Queue.Queue()
        self.start()


    def getVariables(self, table_name):
        self.table = table_name
        self.request_queue.put("variables")
        # Block with timeout of 1 second
        resp = self.response_queue.get(True, 1)
        return resp

    def getUnits(self):
        self.table = table_name
        self.request_queue.put("units")
        # Block with timeout of 1 second
        resp = self.response_queue.get(True, 1)
        return resp


    def openDb(self, log_path):
        self.db = MDataBase(log_path)
        if self.db.isOpen():
            return True
        else:
            return False


    def run(self):
        print "Starting SQLite thread:", self.log_path
        if self.openDb(self.log_path):
            pass
        else:
            raise TypeError("File could not be opened: %s" % self.log_path)
        self.db_done_loading.emit()
        last_request_time = time.time()
        while(self.keep_going):
            try:
                request_type = self.request_queue.get()

                #print datetime.utcfromtimestamp(float(time.time())).strftime("%x %X"), ": received %s request" %request_type
                #print "\t Last request was %f seconds ago" % (time.time()-last_request_time)
                last_request_time = time.time()
                if(request_type == "insert"):
                    self.__sql_insert(self.table, self.columns, self.rows)
                elif(request_type == "query"):
                    print "processing", request_type
                    self.query_return = self.__query(self.table, self.fields, *self.args)
                    self.response_queue.put(self.query_return)
                elif(request_type == "tables"):
                    self.query_return = self.db.getTables()
                    self.response_queue.put(self.query_return)
                elif(request_type == "variables"):
                    self.query_return = self.db.getColumns(str(self.table))[2::2]
                    self.response_queue.put(self.query_return)
                elif(request_type == "units"):
                    self.query_return = self.db.getColumns(str(self.table))[3::2]
                    self.response_queue.put(self.query_return)
                elif(request_type == "stop"):
                    break
                self.request_type = None
            except:
                print("ERROR: Something went wrong with the database!")
                return
                #raise RuntimeError("Something went wrong with the Database")
        self.db.closeDataSet()

    def stop(self):
        self.keep_going = False
        self.request_queue.put("stop")
        self.wait()

    def insert(self, table, columns, rows):
        '''
        Insert data into the database.
        :param table: Table to insert into
        :param columns: Columns
        :param rows: Rows corresponding to the columns
        :return:
        '''

        self.table = table
        self.columns = columns
        self.rows = rows
        self.request_type = "insert"
        self.request_queue.put("insert")

    def __sql_insert(self, table, columns, rows):
        columns = [col.replace(" ", "_") for col in columns]
        table = table.replace(" ", "_")
        #print table,"inserting", columns, rows
        if not self.db.save(table, columns, rows):
            if not self.db.does_table_exist(table):
                # The first column is the time accurate to milliseconds. Making
                # these entries unique ensures that there can be no two measurements
                # taken at the same time. More importantly, it speeds up indexing.
                print "Database table not found. Creating one..."
                column_types = ['REAL UNIQUE']
                column_types.extend(['REAL', 'TEXT'] * len(columns))
                print "column types", column_types
                self.db.create_table(columns, column_types, table)
            elif self.db.findNonExistentColumn(table, columns) is not None:
                col_to_add = self.db.findNonExistentColumn(table, columns)
                print "Adding column to database:", col_to_add
                self.db.addColumn(table, col_to_add, 'REAL')
            else:
                print "Log Failure:",str(table)
                self.exit(1)

                #raise IOError(str(table)+" Failed to log")

    def submit_query(self, table, fields, *args):
        '''
        Returns the result of a query
        :param table: The name of the table to query
        :param fields: The fields to query
        :param args:
        +------------+------------------------+------+------+-----------------------------------------------+
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

        self.table = table
        self.fields = fields
        self.args = args
        self.request_queue.put("query")
        resp = self.response_queue.get(True, 1)
        print "got query response"
        return resp

    def __query(self, table, fields, *args):
        return self.db.query(table, fields, *args)

    def __process_request(self):
        self.db_request_sem.release()

    def __block_until_done(self):
        self.db_task_ready_sem.acquire()

    def getTables(self):
        '''
        Get a list of all tables in the database
        :return: List of tables
        '''

        self.request_queue.put("tables")
        print "getting tables"
        resp = self.response_queue.get(True, 1)
        print "got tables", resp
        return resp
    def isOpen(self):
        '''
        Is there a database open
        :return: bool
        '''
        if(self.db is not None and self.db.isOpen()):
            return True
        else:
            return False

    def configure_data_sets(self):
        pass



   # def __threadSafeClose(self):


