from PyQt4 import QtCore, QtGui

from MDataBase.MDataBaseWrapper2 import MDataBaseWrapper2 as dbr
from MGrapher.MGrapher3 import MGrapher
from MWeb import web
from pyqtgraph.dockarea import *

class MDataViewer(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MDataViewer, self).__init__(parent)
        #root = "C:\Users\Noah\Documents\scripts"
        root = ""
        self.setStyle(QtGui.QStyleFactory.create("plastique"))

        #self.splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter = QtGui.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)
        #self.main_layout = self.splitter
        #self.setLayout(self.main_layout)
        # self.setStyleSheet(".QFrame{\
        #                 background-color:rgb(70, 80, 88);\
        #                 color:rgb(189,195, 199);}")



        self.model = QtGui.QFileSystemModel()
        self.model.setRootPath(root)
        self.model.setFilter(QtCore.QDir.AllEntries | QtCore.QDir.NoDotAndDotDot)
        self.colView = QtGui.QColumnView()
        self.colView.setResizeGripsVisible(False)

        self.colView.setModel(self.model)
        self.colView.setRootIndex(self.model.index(root))
        self.colView.clicked.connect(self.item_selected)
        #self.colView.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        self.splitter.addWidget(self.colView)
        self.splitter.setStretchFactor(0,1)
        self.setWindowTitle("Data Viewer")
        self.resize(800, 400)

        self.db = None

        self.area = DockArea()
        self.splitter.addWidget(self.area)

       # self.main_frame = QtGui.QFrame(self)
        #self.main_frame.setLayout(self.main_layout)
        #self.main_frame.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)

        self.setCentralWidget(self.splitter)

#        self.area.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        self.colView.setMinimumHeight(0.1*self.size().height())
        self.colView.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

        self.splitter.setStretchFactor(1, 1000)
        self.splitter.setStretchFactor(2, 1)
        self.splitter.setStyleSheet("QSplitter::handle\
        {\
            border: 0.2em dotted rgb(150, 150, 180);\
            margin: 0.5em\
        };")



    def item_selected(self, index):

        print "Item selected"
        file_info = self.model.fileInfo(index)
        file_path = file_info.absoluteFilePath()
        print "\tSize: %d\n" \
              "\tAbsolute file path: %s bytes" % (file_info.size(), file_path)
        if(self.db):
            self.db.close()
            del self.db
        self.db = dbr(file_path)
        if not self.db.isOpen():
            print "\tNot a database"
            return
        dock = Dock(file_path, size=(500, 300), closable=True)
        self.area.addDock(dock, 'bottom')

        self.graph = MGrapher(self)
        self.graph.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        self.graph.resize(self.size().width(), 0.9*self.size().height())
        self.graph.setStyle(QtGui.QStyleFactory.create("plastique"))

        background_color = web.color_scheme["dark"]["2nd background"]
        self.setStyleSheet("border-color:rgb(%d,%d,%d);"%(background_color[0],background_color[1], background_color[2]))
        dock.addWidget(self.graph)


        tables = self.db.getTables()
        print tables
        data = []
        columns = []
        times = []
        for table in tables:
            columns.append(self.db.getVariables(table))
            times.append(self.db.query(table, ["capture_time"], "all"))
            for column in columns[-1]:
                data.append(self.db.query(table,[column],"all"))
                curve = self.graph.add_curve(column)
                curve.set_data(times[-1], data[-1])

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    clock = MDataViewer()
    clock.show()
    sys.exit(app.exec_())
