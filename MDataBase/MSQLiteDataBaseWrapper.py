# Copyright 2018 Noah Meltzer

__author__ = "Noah Meltzer"
__copyright__ = "Copyright 2018"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"


from .MDataBase import MDataBase

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QSemaphore
import queue
from datetime import datetime
import time
import traceback

class MSQLiteDataBaseWrapper(QThread):
    db_request_sem = QSemaphore(1)
    db_task_ready_sem = QSemaphore(1)
    db_request_sem.acquire()
    #db_task_ready_sem.acquire()

    db_done_loading = pyqtSignal()
    request_processed = pyqtSignal(list)

    class RequestDescriptor():
        def __init__(self, command, **kwargs):
            self.result_sem = QSemaphore(0)
            self.command = command
            self.kwargs = kwargs
            self.result = None

            self.timeout = kwargs.get("timeout", 1000)

        def get_command(self):
            return self.command

        def get_kwargs(self):
            return self.kwargs

        def _release_result(self):
            self.result_sem.release()

        def set_result(self, result):
            self.result = result
            self._release_result()

        def get_result(self):
            if(not self.result_sem.tryAcquire(1, self.timeout)):
                raise TimeoutError("Database timeout")
            return self.result

    def __init__(self, log_path):
        super(MSQLiteDataBaseWrapper, self).__init__()

        self.db = None
        self.log_path = log_path


        #self.columns = None
        #self.rows = None
        #self.fields = None
        #self.args = None
        #self.query_return = None

        #self.request_type = None

        #self.response_queue = queue.Queue()
        self.request_queue = queue.Queue()
        self.start()

    def isOpen(self):
        '''
        Is there a database open
        :return: bool
        '''
        if(self.db is not None and self.db.isOpen()):
            return True
        else:
            return False

    def openDb(self, log_path):
        self.db = MDataBase(log_path)
        if self.db.isOpen():
            return True
        else:
            return False

    def configure_data_sets(self):
        pass


    def getVariables(self, table_name):
        return self._request_helper("variables", table = table_name)

    def getUnits(self, table_name):
        return self._request_helper("units", table = table_name)

    def getTables(self):
        '''
        Get a list of all tables in the database
        :return: List of tables
        '''
        return self._request_helper("tables")


    def stop(self):
        self._request_helper("stop")
        self.wait()

    def insert(self, table, columns, rows):
        '''
        Insert data into the database.
        :param table: Table to insert into
        :param columns: Columns
        :param rows: Rows corresponding to the columns
        :return:
        '''

        self._request_helper("insert", table = table, columns = columns, rows = rows)

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

        return self._request_helper("query", table = table, fields = fields, args = args)

    def run(self):
        print("Starting SQLite thread:", self.log_path)
        if self.openDb(self.log_path):
            pass
        else:
            raise TypeError("File could not be opened: %s" % self.log_path)
        self.db_done_loading.emit()
        last_request_time = time.time()
        while(True):
            try:
                req_desc = self.request_queue.get()
                request_type = req_desc.get_command()
                kwargs = req_desc.get_kwargs()
                #print datetime.utcfromtimestamp(float(time.time())).strftime("%x %X"), ": received %s request" %request_type
                #print "\t Last request was %f seconds ago" % (time.time()-last_request_time)
                last_request_time = time.time()
                query_return = None
                if(request_type == "insert"):
                    self.__sql_insert(kwargs["table"], kwargs["columns"], kwargs["rows"])
                elif(request_type == "query"):
                    print("processing", request_type, kwargs)
                    query_return = self.__query(kwargs["table"], kwargs["fields"], *kwargs["args"])
                    #print("Returned", query_return)
                elif(request_type == "tables"):
                    query_return = self.db.getTables()
                elif(request_type == "variables"):
                    query_return = self.db.getColumns(str(kwargs["table"]))[2::2]
                elif(request_type == "units"):
                    query_return = self.db.getColumns(str(kwargs["table"]))[3::2]
                elif(request_type == "stop"):
                    req_desc.set_result(query_return)
                    break

            except:
                traceback.print_exc()
                print("ERROR: Something went wrong with the database!")
                return

            req_desc.set_result(query_return)
        self.db.closeDataSet()
        return

    def __sql_insert(self, table, columns, rows):
        columns = [col.replace(" ", "_") for col in columns]
        table = table.replace(" ", "_")
        #print table,"inserting", columns, rows
        if not self.db.save(table, columns, rows):
            if not self.db.does_table_exist(table):
                # The first column is the time accurate to milliseconds. Making
                # these entries unique ensures that there can be no two measurements
                # taken at the same time. More importantly, it speeds up indexing.
                print("Database table not found. Creating one...")
                column_types = ['REAL UNIQUE']
                column_types.extend(['REAL', 'TEXT'] * len(columns))
                print("column types", column_types)
                self.db.create_table(columns, column_types, table)
            elif self.db.findNonExistentColumn(table, columns) is not None:
                col_to_add = self.db.findNonExistentColumn(table, columns)
                print("Adding column to database:", col_to_add)
                self.db.addColumn(table, col_to_add, 'REAL')
            else:
                print("Log Failure:",str(table))
                self.exit(1)

                #raise IOError(str(table)+" Failed to log")

    def __query(self, table, fields, *args):
        return self.db.query(table, fields, *args)

    def __process_request(self):
        self.db_request_sem.release()

    def __block_until_done(self):
        self.db_task_ready_sem.acquire()

    def _request_helper(self, request, **kwargs):
        desc = self.RequestDescriptor(request, **kwargs)
        self.request_queue.put(desc)
        resp = desc.get_result()
        del desc
        return resp


