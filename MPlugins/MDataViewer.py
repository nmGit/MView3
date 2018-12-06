from PyQt4 import QtCore, QtGui, Qt
from MGrapher2 import MGrapher2
class MDataViewer(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MDataViewer, self).__init__(parent)
        root = ""
        self.graph = MGrapher2(self)

        self.splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)
        #self.splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.main_layout = QtGui.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.splitter)
        self.model = QtGui.QFileSystemModel()
        self.model.setRootPath(root)

        self.colView = QtGui.QColumnView()
        self.colView.setModel(self.model)
        self.colView.setRootIndex(self.model.index(root))
        self.colView.clicked.connect(self.item_selected)

        self.splitter.addWidget(self.colView)
        self.splitter.addWidget(self.graph)
        self.setWindowTitle("Data Viewer")
        self.resize(800, 400)

    def item_selected(self, index):
        print "Item selected"
        file_info = self.model.fileInfo(index)
        print "\tSize: %d\n" \
              "\tAbsolute file path: %s bytes" % (file_info.size(), file_info.absoluteFilePath())



if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    clock = MDataViewer()
    clock.show()
    sys.exit(app.exec_())
