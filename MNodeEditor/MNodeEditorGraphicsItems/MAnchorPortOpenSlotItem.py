from PyQt4 import QtCore, QtGui, Qt
from MCircleWidget import MCircleWidget


class MAnchorPortOpenSlotItem(MCircleWidget):
    def __init__(self, parent):
        MCircleWidget.__init__(self, parent)

        pass

    def enterEvent(self, event):
        self.pen.setStyle(QtCore.Qt.DotLine)
        self.update()

    def leaveEvent(self, event):
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.update()


