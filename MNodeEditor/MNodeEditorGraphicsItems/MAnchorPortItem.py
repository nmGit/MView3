from PyQt4 import QtCore, QtGui, Qt
from MNodeEditor.MPipe import MPipe
from MCircleWidget import MCircleWidget



class MAnchorPortItem(MCircleWidget):
    def __init__(self, parent, anchor):
        MCircleWidget.__init__(self, parent)
        self.parent = parent
        self.anchor = anchor
        pass

    def enterEvent(self, event):
        self.pen.setStyle(QtCore.Qt.DotLine)
        self.update()

    def leaveEvent(self, event):
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.update()

    def mousePressEvent(self, event):
        if self.anchor.isConnected():
            if self.anchor.getType() == 'input':
                self.anchor.disconnect()
                self.tree.deletePipe(self.anchor.pipe)
        else:
            #activePipe = self.parent.graphicsNode.getNodeEditor().getActivePipe()
            activeAnchor = self.parent.graphicsNode.getNodeEditor().getActiveAnchor()
            if activeAnchor is not None:
                #activePipe.connect(self.anchor)
               # self.anchor.connect(activePipe)
                self.parent.graphicsNode.node_editor.tree.connect(activeAnchor, self.anchor)
                self.parent.graphicsNode.getNodeEditor().setActiveAnchor(None)
            else:
                self.parent.graphicsNode.getNodeEditor().setActiveAnchor(self.anchor)
                #pipe = MPipe(self.anchor)
                #self.parent.graphicsNode.getNodeEditor().setActivePipe(pipe)