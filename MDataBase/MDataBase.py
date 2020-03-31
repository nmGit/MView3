# Copyright 2018 Noah Meltzer

__author__ = "Noah Meltzer"
__copyright__ = "Copyright 2018"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"

import sqlite3
from datetime import date
import time
import traceback
import numpy as np

class MDataBase:
    def __init__(self, db_path):
        print "Connecting to database located at:", str(db_path)
        #traceback.print_stack()
        try:
            self.conn = sqlite3.connect(str(db_path))
            self.open = True
        except:
            self.open = False
            return
        self.cursor = self.conn.cursor()
        self.commit_rate = 10 # commit every 300 writes
        self.writes_since_last_commit = 0
    def isOpen(self):
        return self.open
    def save(self, table_name, column_names, value_names):
        table_name = table_name.replace("'", "")
        values = ["'"+str(v)+"'" if v != None else 'NULL' for v in value_names]
        values = ",".join(values)

        column_names = ["'" + c + "'" for c in column_names]
        columns = ",".join(column_names)
        table_name = "'" + table_name + "'"
        table_name = table_name.replace(" ", "_")

        #print "trying to save:\n\t", columns, "\n\t", values

        try:
            t1 = time.time()
            self.cursor.execute(
                "INSERT INTO {tn} ({cn})"
                "VALUES ({vals});".format(
                    tn = table_name,
                    cn = columns,
                    vals = values
                    )
                )


            #print self.cursor.fetchall()
            self.writes_since_last_commit += 1
           # print table_name, "writes since commit:", self.writes_since_last_commit
            if(self.writes_since_last_commit >= self.commit_rate):
                #print table_name, "committing!"
                t1_1 = time.time()
                self.conn.commit()
                t2_1 = time.time()
                #print table_name, "time to commit:", t2_1 - t1_1
                self.writes_since_last_commit = 0

            t2 = time.time()
            #print table_name, "time to execute sql", t2 - t1
            return True
        except:
            #traceback.print_exc()
            return False

    def commit_after_num_writes(self, rate):
        self.commit_rate = rate
    def create_table(self, column_names, column_qualifiers, table_name):
        table_name = table_name.replace("'", "")
        table_name = "'" + table_name + "'"
        table_name = table_name.replace(" ", "_")
        column_tup = []
        for i,c in enumerate(column_names):
            column_tup.append("'"+str(c)+"' "+str(column_qualifiers[i]))
        columns = ",".join(column_tup)
        print "Creating table:", table_name, "with columns:", columns
        self.cursor.execute(
             "CREATE TABLE {tn}("
             "   PK INTEGER PRIMARY KEY AUTOINCREMENT,"
             "   {cn}"
             ");".format(
                 tn = table_name,
                 cn = columns
             )
        )

    def does_table_exist(self, table_name):
        table_name = table_name.replace("'", "")
        table_name = "'" + table_name + "'"
        table_name = table_name.replace(" ","_")
        self.cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE TYPE='table' AND NAME={tn}".format(tn=table_name))
        return (1==self.cursor.fetchall()[0][0])

    def query(self, table_name, columns = '*', *args):
        #print "args:", args
        #TODO: See if you can speed this up, particularly return astype(float)
        try:
            if columns != "*":
                field = [str("'"+column.replace(' ','_')+"'") for column in columns]
            else:
                field = "*"
            table_name = table_name.replace(' ', '_')
            table_name = table_name.replace("'", "")
            #print "Table name before:", table_name
            if table_name != "*":
                table_name = "'" + table_name + "'"
            if args[0] == "last":
                if type(field) is not list and field != '*':
                    raise ValueError('MDataBase: If arg is "last" then field must be a list of columns.')

                self.cursor.execute(
                    "SELECT {cn}"
                    "   FROM {tn}"
                    "   WHERE PK = (SELECT MAX(PK) FROM {tn}".format(
                        cn=str(field).replace('[', '').replace(']', '').replace("'",''),
                        tn=table_name
                    )
                )
                return self.cursor.fetchall()

            elif args[0] == "all":
                if type(field) is not list and field != '*':
                    raise ValueError('MDataBase: If arg is "all" then field must be a list of columns.')
               # print "TABLE name:", table_name
                cmd =    "SELECT {cn} FROM {tn}".format(
                        cn=str(field).replace('[', '').replace(']', '').replace("'",''),
                        tn=table_name.replace(" ", "_")
                    )
                print cmd
                self.cursor.execute(
                    cmd
                )
                data = self.cursor.fetchall()
                #print data
                return [d[0] if d[0] != None else np.nan for d in data]

            elif args[0] == "range":
                if type(field) is not list and field != '*':
                    raise ValueError('MDataBase: If arg is "range" then field must be a list of columns.')

                self.cursor.execute(
                    "SELECT {cn}"
                    "   FROM {tn}"
                    "   WHERE {k} > '{t1}' and {k} < '{t2}'".format(
                        cn=str(field).replace('[', '').replace(']', '').replace("'",''),
                        tn=table_name,
                        k = args[1],
                        t1 = args[2],
                        t2 = args[3]
                    )
                )

                return self.cursor.fetchall()
                # print ("SELECT {cn}"
                #     "   FROM {tn}"
                #     "   WHERE {k} > '{t1}' and {k} < '{t2}'".format(
                #         cn=str(field).replace('[', '').replace(']', '').replace("'",''),
                #         tn=table_name,
                #         k=args[1],
                #         t1=args[2],
                #         t2=args[3]))

        except sqlite3.Error as e:
            print "An error occurred:", e.args[0]
    def getColumns(self, table_name):

        table_name = table_name.replace(" ", "_")
        table_name = table_name.replace("'", "")
        table_name = "'" + table_name + "'"
        t1 = time.time()
        cmd =  "PRAGMA"\
            "   table_info({tn});".format(
                tn = table_name
            )
        print "command:", cmd
        self.cursor.execute(cmd)
        t2 = time.time()
        r = [i[1].encode('ascii') for i in self.cursor.fetchall()]

       # print table_name, "time to get columns:", t2-t1
        return r
    def getTables(self):
        self.cursor.execute(
            "select name from sqlite_master where type = 'table';"
        )
        return [str(t[0]) for t in self.cursor.fetchall()]
    def findNonExistentColumn(self, table_name, columns):
        table_name = table_name.replace("'", "")
        table_name = "'" + table_name + "'"

        existing_columns = self.getColumns(table_name)
        for column in columns:
            if column in existing_columns:
                pass
            else:
                return column
        return None

    def addColumn(self, table_name, column, type):
        table_name = table_name.replace("'", "")
        table_name = table_name.replace(" ", "_")
        column = column.replace(" ", "_")
        cmd =  "ALTER TABLE '{tn}' ADD '{cn}' {ct}".format(tn = table_name,
                                                        cn = column,
                                                        ct = type)
        try:
            self.cursor.execute(cmd)
        except:
            raise IOError("SQL Command Fail: "+cmd)
        print self.cursor.fetchall()
    def saveState(self):
        pass
    def restoreState(self):
        pass
    def configureDataSets(self):
        pass
    def closeDataSet(self):
        self.conn.commit()
        self.conn.close()
    def __addColumn(self):
        pass