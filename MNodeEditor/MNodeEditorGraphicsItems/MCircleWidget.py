from PyQt4 import QtCore,QtGui

class MCircleWidget(QtGui.QWidget):


    def __init__(self, parent = 0):
        QtGui.QWidget.__init__(self, parent)

        self.floatBased = False
        self.antialiased = False
        self.frameNo = 0
        self.setContentsMargins(10,10,10,10)

        self.setBackgroundRole(QtGui.QPalette.Base)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        self.lineWeight = 2
        self.pen = QtGui.QPen(QtGui.QColor(189, 195, 199), self.lineWeight)
        self.update()

    def setFloatBased(self, floatBased):
        self.floatBased = floatBased
        pass

    def setAntialiased(self, antialiased):
        self.antialiased = antialiased
        pass

    def minumumSizeHint(self):
        return QtCore.QSize(50,50)

    def sizeHint(self):
        return QtCore.QSize(30,30)

    def nextAnimationFrame(self):
        self.frameNo += 1
        self.update()
        pass

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, self.antialiased)

        painter.setPen(self.pen)
        painter.drawEllipse(
            self.lineWeight,
            self.lineWeight,
            self.width()-self.lineWeight*2,
            self.height()-self.lineWeight*2)
       # painter.drawRect(QtCore.QRect(0,0,self.width(), self.height()))
        pass

