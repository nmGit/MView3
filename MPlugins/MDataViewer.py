from PyQt4 import QtCore, QtGui

from MDataBase.MSQLiteDataBaseWrapper import MSQLiteDataBaseWrapper as dbr
from MGrapher.MGrapher3 import MGrapher
from MWeb import web
from pyqtgraph.dockarea import *
import os

class MDataViewer(QtGui.QWidget):
    def __init__(self, parent=None, **kwargs):
        super(MDataViewer, self).__init__(parent)
        #root = "C:\Users\Noah\Documents\scripts"
        root = ""
        self.setStyle(QtGui.QStyleFactory.create("plastique"))
        self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        #self.splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter = QtGui.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)
       # self.setCentralWidget(self.splitter)
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
        #self.splitter.setStretchFactor(0,1)
        self.setWindowTitle("Data Viewer")
        

        self.db = None

        self.area = DockArea()
        self.area.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        self.splitter.addWidget(self.area)
        self.splitter.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        self.main_layout = QtGui.QVBoxLayout()

        #self.main_frame = QtGui.QFrame(self)
        #self.main_frame.setLayout(self.main_layout)
        bckgrnd = web.color_scheme["dark"]["4th background"]
        self.setStyleSheet("QFrame{"
                           "margin:0px; "
                           "border:2px solid rgb(0, 0, 0); "
                           "background-color:rgb(%d,%d,%d)}" % (bckgrnd[0], bckgrnd[1], bckgrnd[2]))
        self.main_layout.addWidget(self.splitter)
        self.setLayout(self.main_layout)
        #self.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)

#        self.setCentralWidget(self.splitter)

     
        self.colView.setMinimumHeight(0.1*self.size().height())
        self.colView.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        bckgrnd = web.color_scheme["dark"]["2nd background"]
        self.colView.setStyleSheet("QFrame{"
                           "margin:0.4em; "
                           "border:0.1em solid rgb(0, 0, 0); "
                           "background-color:rgb(%d,%d,%d)}" % (bckgrnd[0], bckgrnd[1], bckgrnd[2]))
        #self.splitter.setStretchFactor(1, 2)
        #self.splitter.setStretchFactor(2, 1)
        self.splitter.setStyleSheet("QSplitter::handle\
        {\
            border: 0.2em dotted rgb(150, 150, 180);\
            margin: 0.5em\
        };")
      #  self.resize(500, 500)
       # self.area.resize(500,500)
       # self.splitter.resize(500,500)
        max_height = kwargs.get("max_height",None)
        if max_height != None:
            self.setMaximumHeight(max_height)

    def item_selected(self, index):

        print "Item selected"
        file_info = self.model.fileInfo(index)
        file_path = file_info.absoluteFilePath()
        print "\tSize: %d\n" \
              "\tAbsolute file path: %s bytes" % (file_info.size(), file_path)
        if(self.db):
            self.db.stop()
            del self.db
        if os.path.isfile(file_path):
            self.db = dbr(file_path)
        else:
            return

        dock = Dock(file_path, closable=True)
        

        self.graph = MGrapher(self, live_mode=False)
        self.graph.show_plot()
        
        
        #self.area.resize(0.5*self.size().width(), 0.5*self.size().height())
       
        self.graph.setStyle(QtGui.QStyleFactory.create("plastique"))
      
        
        dock.addWidget(self.graph)
        #self.graph.resi
        #self.graph.resize(self.graph.width(), self.graph.width())
        #dock.setSizePolicy( QtGui.QSizePolicy.Maximum,  QtGui.QSizePolicy.Maximum)
        #dock.setStretch(self.graph.width(), self.graph.width())
        #dock.resize(500,300)
        self.area.addDock(dock, 'bottom')
        tables = self.db.getTables()
        print "Tables are:", tables
        data = []
        columns = []
        times = []
        for table in tables:
            columns.append(self.db.getVariables(table))
            times.append(self.db.submit_query(table, ["capture_time"], "all"))
            for column in columns[-1]:
                data.append(self.db.submit_query(table,[column],"all"))
                curve = self.graph.add_curve(column)
                curve.set_data(times[-1], data[-1])
                #print "Adding", times[-1], data[-1]
        #self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        #self.setFixedHeight(50)
if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    clock = MDataViewer()
    clock.show()
    sys.exit(app.exec_())
