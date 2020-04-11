from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import os
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

class MCheckableComboBox(QtWidgets.QComboBox):
    itemChecked = pyqtSignal(str)
    itemUnChecked = pyqtSignal(str)
    def __init__(self, **kwargs):
        super(MCheckableComboBox, self).__init__()
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))
        color_scheme = kwargs.get("color_scheme", "dark")
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        self.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents )
        if(color_scheme == "dark"):
            self.setStyleSheet("\
                        background-color:rgb(70, 80, 88);\
                        color:rgb(189,195, 199);")

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
            self.itemUnChecked.emit(item.text())
        else:
            item.setCheckState(QtCore.Qt.Checked)
            self.itemChecked.emit(item.text())

    def isChecked(self, index):
        item = self.model().item(index)
        if item.checkState() == QtCore.Qt.Checked:
            #item.setCheckState(True)
            return True
        #item.setCheckState(False)
        return False

    def setChecked(self, index, checked):
        item = self.model().item(index)
        item.setCheckState(
            QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)
    def addItem(self, text, checked = False):

        QtGui.QComboBox.addItem(self,text)
        item = self.model().item(self.findText(text))
        if checked:
            checkstate = 2
        else:
            checkstate = 0
        item.setCheckState(checkstate)
    def removeItem(self, text):
        index = self.findText(text)
        item = self.model().item(index)
        item.setCheckState(False)
        QtGui.QComboBox.removeItem(self, index)