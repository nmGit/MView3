from PyQt5 import QtCore
from .MCircleWidget import MCircleWidget
from .MPipeItem import MPipeGraphicsItem



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
                self.parent.directInput.show()
                self.parent.okDirectInput.show()
                self.parent.lcd.hide()
        else:
            self.parent.directInput.hide()
            self.parent.okDirectInput.hide()
            self.parent.lcd.show()

            #activePipe = self.parent.graphicsNode.getNodeEditor().getActivePipe()
            activeAnchor = self.parent.graphicsNode.getNodeEditor().getActiveAnchor()
            if activeAnchor[0] is not None:
                #activePipe.connect(self.anchor)
               # self.anchor.connect(activePipe)
                self.parent.graphicsNode.node_editor.tree.connect(activeAnchor[0], self.anchor)
                MPipeGraphicsItem(self.parent.anchor.getPipes()[-1], self.parent, activeAnchor[1], self.parent.scene)
                self.parent.graphicsNode.getNodeEditor().setActiveAnchor(None, None)
            else:
                self.parent.graphicsNode.getNodeEditor().setActiveAnchor(self.anchor, self.parent)
                #pipe = MPipe(self.anchor)
                #self.parent.graphicsNode.getNodeEditor().setActivePipe(pipe)