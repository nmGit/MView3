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
from MNodeEditor.MNodeEditorGraphicsItems.MCircleWidget import MCircleWidget

__author__ = "Noah Meltzer"
__copyright__ = "Copyright 2016, McDermott Group"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"

from PyQt4 import QtGui, QtCore, Qt
from MWeb import web
from MReadout import MReadout
import MAnchorPortItem
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

class MAnchorItem(QtGui.QFrame):
    def __init__(self, graphicsNode, anchor, parent=None, *args, **kwargs):
        QtGui.QFrame.__init__(self, parent)
        #print "Adding anchor"

        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.MinimumExpanding)

        self.anchorLayout = QtGui.QHBoxLayout()
        self.setLayout(self.anchorLayout)

        self.graphicsNode = graphicsNode

        self.anchor = anchor

        self.anchor.node.MNodeUpdatedSignal.connect(self.refresh)
        self.scene = graphicsNode.scene

        self.directInput = None
        self.okDirectInput = None
        self.directInputLayout = None
        self.directInputData = 0
        self.nodeBrush = QtGui.QBrush(QtGui.QColor(*graphicsNode.getColor()))

        self.anchorSize = int(8 * web.ratio)
        # bounding rect
        self.rect = QtCore.QRectF(
            0, 0, self.anchorSize,  self.anchorSize)

        # The QPen
        self.textPen = QtGui.QPen()
        self.textPen.setStyle(2)
        self.textPen.setWidth(2)
        self.textPen.setColor(QtGui.QColor(189, 195, 199))
        self.pipe = None

        self.labelWidget = QtGui.QLabel(str(anchor))
        self.labelWidget.setStyleSheet("color:rgb(189, 195, 199)")
        self.anchorLayout.addWidget(self.labelWidget)

        self.lcd = MReadout(self)
        self.lcd.setStyleSheet("color:rgb(189, 195, 199);\n")
        self.anchorLayout.addWidget(self.lcd)

        label = QtCore.QString(str(anchor))
        self.font = QtGui.QFont()
        self.font.setPointSize(10)

   #     if self.suggestedDataType == 'float':

        self.directInput = QtGui.QLineEdit(
            str(self.directInputData), self)

        self.directInputLayout = QtGui.QHBoxLayout()

        self.okDirectInput = QtGui.QPushButton("Set", self)

        width = self.okDirectInput.fontMetrics().boundingRect("Set").width()
        height = self.okDirectInput.fontMetrics().boundingRect("Set").height()
        self.okDirectInput.setMaximumWidth(width + 10)
        self.okDirectInput.setMaximumHeight(height + 5)

        self.lcd.show()
        self.directInput.hide()
        self.okDirectInput.hide()

        self.anchorLayout.insertStretch(2)

        self.port = MAnchorPortItem.MAnchorPortItem(self, anchor)
        if(anchor.getType() == 'input'):
            self.anchorLayout.insertWidget(0, self.port)
        else:
            self.anchorLayout.addWidget(self.port)
        self.port.show()

        if self.directInput != None:
            self.directInputLayout.addWidget(self.directInput)
            self.directInputLayout.addWidget(self.okDirectInput)
            self.anchorLayout.addLayout(self.directInputLayout)

#        self.prepareGeometryChange()
    def setParentNode(self, node):
        '''Set the parent node.'''
        self.setParentItem(node)
        # Repaint the scene
        self.update()

    def delete(self):
        # print "deleting anchor"

        self.nodeLayout.removeWidget(self.lcd)
        self.nodeLayout.removeWidget(self.labelWidget)

        self.labelWidget.deleteLater()
        self.lcd.deleteLater()

        self.setParentItem(None)
        self.scene.removeItem(self)

    def getLabel(self):
        return str(self.label)

    def setLabel(self, text):
        self.label = text
    def validate(self, type, val):
        '''Make sure value is ov certain type'''
        if type == 'float':
                value = float(str(val))
                return value
        return None
    def directInputHandler(self, type,  callback):
        pass
        # # print "type:", type
        # try:
        #     value = self.validate(type, callback())
        # except:
        #      self.directInput.setStyleSheet( "background:rgb(255,0,0);")
        #      traceback.print_exc()
        #      return
        # # print "value:", value
        # self.directInput.setStyleSheet( "background:rgb(255,255,255);")
        #
        # if self.pipe != None and self.type == 'output':
        #     self.pipe.setData(value)
        # else:
        #     self.directInputData = value
        # self.data = directInputData
        # self.parentNode().refreshData()
    def getLcd(self):
        return self.lcd
    def refresh(self):
        self.getLcd().display(self.anchor.getData())

    def setColor(self, color):
        self.nodeBrush = QtGui.QBrush(color)

    def getGlobalLocation(self):

      #  loc =  QtCore.QPoint(self.graphicsNode.scenePos().x()
      #                       ,self.graphicsNode.scenePos().y())
        loc =  self.pos() + self.graphicsNode.scenePos() + self.port.pos() + QtCore.QPoint(self.port.size().width()/2, self.port.size().height()/2)
        return loc
    def getLocalLocation(self):
        return QtCore.QPoint(self.port.posX,self.port.posY)
    def paint(self, painter, option, widget):
       # print "painting..."
        if self.type == 'output':
            # Bounding rectangle of the anchor
            self.posX = self.nodeFrame.width()

        elif self.type == 'input':
            self.posX = -20
        # print "pipe:", self.pipe
        if self.pipe != None:
            self.nodeBrush = QtGui.QBrush(QtGui.QColor(200,0,0))
        else:
            self.nodeBrush = QtGui.QBrush(QtGui.QColor(*self.graphicsNode.getColor()))

        painter.setBrush(self.nodeBrush)
        painter.setPen(self.textPen)
        painter.setFont(self.font)

        painter.drawRect(self.rect)

        painter.drawEllipse(0,  0, self.anchorSize,  self.anchorSize)
    def boundingRect(self):
        return self.rect

    def mousePressEvent(self, event):
       # print "Anchor clicked!"
       #  if self.isConnected():
       #      self.tree.deletePipe(self.pipe)
       #      if self.directInput != None:
       #          self.directInput.show()
       #          self.okDirectInput.show()
       #          self.lcd.hide()
       #  else:
       #      self.tree.connect(self.anchor)
       #      if self.directInput != None:
       #          self.directInput.hide()
       #          self.okDirectInput.hide()
       #          self.lcd.show()

        self.update()
        self.setSelected(True)
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        QtGui.QFrame.mouseMoveEvent(self, event)

        # def hoverEnterEvent(self, event):
    #     self.textPen.setStyle(QtCore.Qt.DotLine)
    #     QtGui.QGraphicsItem.hoverEnterEvent(self, event)
    #
    # def hoverLeaveEvent(self, event):
    #     self.textPen.setStyle(QtCore.Qt.SolidLine)
    #     QtGui.QGraphicsItem.hoverLeaveEvent(self, event)

