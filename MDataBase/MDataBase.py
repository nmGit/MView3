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

class MDataBase:
    def __init__(self, db_path):
        print "Connecting to database located at:", str(db_path)
        #traceback.print_stack()
        self.conn = sqlite3.connect(str(db_path))
        self.cursor = self.conn.cursor()

    def save(self, table_name, column_names, value_names):

        values = [str(v) for v in value_names]
        values = "'"+"','".join(values)+"'"

        columns = ",".join(column_names)
        table_name = table_name.replace(" ", "_")

        #print "trying to save:\n\t", columns, "\n\t", values
        try:
            self.cursor.execute(
                "INSERT INTO {tn} ({cn})"
                "VALUES ({vals});".format(
                    tn = table_name,
                    cn = columns,
                    vals = values
                    )
                )
            #print self.cursor.fetchall()
            self.conn.commit()
            return True
        except:
            traceback.print_exc()
            return False


    def create_table(self, column_names, column_qualifiers, table_name):
        table_name = table_name.replace(" ", "_")
        column_tup = []
        for i,c in enumerate(column_names):
            column_tup.append(str(c)+" "+str(column_qualifiers[i]))
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
        table_name = table_name.replace(" ","_")
        self.cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE TYPE='table' AND NAME='{tn}'".format(tn=table_name))
        return (1==self.cursor.fetchall()[0][0])

    def query(self, table_name, columns = '*', *args):
        #print "args:", args

        try:

            field = [column.replace(' ','_') for column in columns]
            table_name = table_name.replace(' ', '_')
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

                self.cursor.execute(
                    "SELECT {cn} FROM {tn}".format(
                        cn=str(fields).replace('[', '').replace(']', '').replace("'",''),
                        tn=table_name.replace(" ", "_")
                    )
                )
                return self.cursor.fetchall()

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
        self.cursor.execute(
            "PRAGMA"
            "   table_info({tn})".format(
                tn = table_name
            )
        )
        return [i[1].encode('ascii') for i in self.cursor.fetchall()]

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