# Copyright (C) 2016 Noah Meltzer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

__author__ = "Noah Meltzer"
__copyright__ = "Copyright 2016, McDermott Group"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"

from PyQt5 import QtGui, QtCore, QtWidgets
from .MAnchorItem import MAnchorItem

class MNodeGraphicsItem(QtWidgets.QGraphicsObject):
    parent = None
    node_editor = None
    title = None
    def __init__(self, node_editor, parent=None, *args, **kwargs):
        super(MNodeGraphicsItem, self).__init__(None)
        #QtGui.QGraphicsObject.__init__(self)
        self.parent = parent
        self.node = parent
        self.node_editor = node_editor
        # default color'
        self.color = (50, 50, 50)
        self.nodeFrame = QtGui.QFrame()
        self.anchors = []
     #   self.node.device.addParameterSignal.connect(self.addParameter)
        self.node.connectAnchorAddedSignal(self.addAnchorExistingAnchorFromName)
        self.begin(**kwargs)

    def begin(self,   **kwargs):
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, True)
        self.setAcceptHoverEvents(True)

        self.node_editor.scene.addItem(self)
        self.setScene(self.node_editor.scene)
        self.anchorLayout = QtGui.QVBoxLayout()
        self.nodeLayout = QtGui.QVBoxLayout()
        self.nodeGraphicsLayout = QtGui.QGraphicsGridLayout()
        self.font = QtGui.QFont()
        self.font.setPointSize(15)
        self.label = QtGui.QLabel(self.parent.getTitle())
        self.label.setFont(self.font)
        self.label.setStyleSheet("color:rgb(189,195,199)")
        #self.labelProxy = QtGui.QGraphicsProxyWidget(self)
        #self.labelProxy.setWidget(self.label)
        #self.labelProxy.setParentItem(self);
        self.nodeLayout.addWidget(self.label)
        self.nodeFrame.setLayout(self.nodeLayout)
        self.nodeLayout.addLayout(self.anchorLayout)
        self.nodeFrame.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.MinimumExpanding)
        #self.nodeLayout.addWidget(self.label)
        pProxy = QtGui.QGraphicsProxyWidget(self)
        pProxy.setWidget(self.nodeFrame)
       # self.node_editor.scene.addItem(pProxy)
        print("parent's anchors",self.parent.getAnchors())
        for anchor in self.parent.getAnchors():
            pass
            self.addAnchor(anchor)

        self.openSlotLayout = QtGui.QHBoxLayout()

        #self.addNodeLabel = QtGui.QLabel(str("Add..."))
       # self.addNodeLabel.setStyleSheet("color:rgb(139, 250, 149)")

       # self.openSlot = MAnchorPortOpenSlotItem(self.nodeFrame)
        self.addAnchorButton = QtGui.QPushButton("Add")
        self.openSlotLayout.addWidget(self.addAnchorButton)
        self.openSlotLayout.addStretch(0)
        self.addAnchorButton.clicked.connect(self.addNewParameterEvent)
        self.nodeLayout.addWidget(self.addAnchorButton)

        # Tell the gui that the item is moveable, slectable, and focusable and that
        # it accepts hover events.

        # Bounding rectangle
        self.rect = QtCore.QRectF(
            0, 0, self.nodeFrame.width(), self.nodeFrame.height())
        # Tell the gui that the item is moveable, slectable, and focusable and that
        # it accepts hover events.
        self.setColor(*self.color)
        self.textPen = QtGui.QPen()
        self.textPen.setWidth(2)
        self.textPen.setColor(QtGui.QColor(255, 100, 0))
        #self.textPen.setColor(QtGui.QColor(189, 195, 199))

        self.nodeBrush = QtGui.QBrush(QtGui.QColor(*self.color))

        #self.node_editor.getScene().addItem(self)

    def getNodeWidget(self):
        return self.nodeFrame

    def getNodeLayout(self):
        return self.nodeLayout
    def addAnchorExistingAnchorFromName(self, anchorName, anchorType):
        self.addAnchor(self.node.getAnchorByName(anchorName))

    def addAnchor(self, anchor, **kwargs):
        self.anchors.append(anchor)
        num_anchors = len(self.anchors)
        self.anchorLayout.addWidget(MAnchorItem(self, anchor))
        self.rect = QtCore.QRectF(
            0, 0, self.nodeFrame.width(), self.nodeFrame.height())

        pass

    def setColor(self, r, g, b):
        self.color = (r, g, b)
        self.nodeFrame.setStyleSheet(
            ".QFrame{"
            "background:rgba(" + str(r) + ',' + str(g) + ',' + str(b) + ", 80);"
            "border-style: solid;"
            "border-color: rgb(189, 195, 199);"
            "border-width: 0.1em;"
            "}")

    def getColor(self):
        return self.color

    def setScene(self, scene):
        self.scene = scene

    def setTitle(self, title):
        self.label.setText(title)

    def hoverEnterEvent(self, event):
        r = self.color[0]
        g = self.color[1]
        b = self.color[2]
        self.nodeFrame.setStyleSheet(
            ".QFrame{"
            "background:rgba(" + str(r) + ',' + str(g) + ',' + str(b) + ", 255);"
            "border-style: dashed;"
            "border-color: rgb(189, 195, 199);"
            "border-width: 0.1em;"
            "}")

        self.prepareGeometryChange()
        self.textPen.setStyle(QtCore.Qt.DotLine)
        QtGui.QGraphicsItem.hoverEnterEvent(self, event)

    def hoverLeaveEvent(self, event):
        r = self.color[0]
        g = self.color[1]
        b = self.color[2]
        self.nodeFrame.setStyleSheet(
            ".QFrame{"
            "background:rgba(" + str(r) + ',' + str(g) + ',' + str(b) + ", 80);"
            "border-style: solid;"
            "border-color: rgb(189, 195, 199);"
            "border-width: 2px;"
            "}")
        self.prepareGeometryChange()
        self.textPen.setStyle(QtCore.Qt.SolidLine)
        QtGui.QGraphicsItem.hoverLeaveEvent(self, event)

    def mouseMoveEvent(self, event):
        self.prepareGeometryChange()
        QtGui.QGraphicsItem.mouseMoveEvent(self, event)

    def mousePressEvent(self, event):
        self.prepareGeometryChange()
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def addNewParameterEvent(self, event):
        text, ok = QtGui.QInputDialog.getText(self.node_editor, "New Parameter", "Enter a name for the new parameter:")
        self.node.addAnchor(name = text, type = 'input')

    def getNodeEditor(self):
        return self.node_editor

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        pass
 #       self.rect.setHeight(self.nodeFrame.height())
 #       self.rect.setWidth(self.nodeFrame.width())

#        painter.setBrush(self.nodeBrush)
#        painter.setPen(self.textPen)
#        painter.setFont(self.font)

