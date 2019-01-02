# Copyright 2018 Noah Meltzer

__author__ = "Noah Meltzer"
__copyright__ = "Copyright 2018"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"


from MDataBase import MDataBase

from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QSemaphore
from MWeb import web
import Queue

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
        return self.db.getColumns(str(table_name))[2::2]

    def getUnits(self):
        cols = self.db.getColumns(str(self.device))[3::2]

    def openDb(self, log_path):
        self.db = MDataBase(log_path)
    def run(self):
        print "Starting SQLite thread:", self.log_path
        self.openDb(self.log_path)
        self.db_done_loading.emit()
        while(self.keep_going):

            request_type = self.request_queue.get()

            if(request_type == "insert"):
                self.__sql_insert(self.table, self.columns, self.rows)
            elif(request_type == "query"):
                print "processing", request_type
                self.query_return = self.__query(self.table, self.fields, *self.args)
                self.response_queue.put(self.query_return)
            self.request_type = None
        self.db.closeDataSet()

    def stop(self):
        self.keep_going = False
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
        self.request_type = "query"
        #self.request_processed.disconnect()
        #self.request_processed.connect(callback)
        self.request_queue.put("query")
        resp = self.response_queue.get()
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
        return self.db.getTables()

    def isOpen(self):
        '''
        Is there a database open
        :return: bool
        '''
        return self.db.isOpen()

    def configure_data_sets(self):
        pass



   # def __threadSafeClose(self):


