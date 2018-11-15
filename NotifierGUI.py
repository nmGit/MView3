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

# Utilities libraries.
__author__ = "Noah Meltzer"
__copyright__ = "Copyright 2016, McDermott Group"
__license__ = "GPL"
__version__ = "2.0.0"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"

"""
# description = Allows user to configure notifications
"""
import sys

from PyQt4 import QtCore, QtGui
from MWeb import web
import inspect
import cPickle as pickle
import os
import inspect
import traceback
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from MCheckableComboBoxes import MCheckableComboBox
sys.dont_write_bytecode = True


class NotifierGUI(QtGui.QDialog):

    def __init__(self, loader, parent=None):
        '''Initialize the Notifier Gui'''
        super(NotifierGUI, self).__init__(parent)
        # Create a new tab
        tabWidget = QtGui.QTabWidget()

        # The name of the main MView program
        self.loader = loader
        # The the config data should be stored with the the main class
        self.location = os.path.dirname(traceback.extract_stack()[0][0])
        # Dictionary that will store all data
        self.allDataDict = {}
        # print "Looking for config file in: ", self.location
        # New widget
        self.alert = AlertConfig(self.location, loader)
        # AlDatatxt holds the text contents of all data entered in table
        self.allDatatxt = [[], [], [], []]
        # The settings window has a tab
        tabWidget.addTab(self.alert, "Alert Configuration")
        # Create email list in a new tab
        print self.alert.allDataDict

        self.email_lists = MMailingLists()
        tabWidget.addTab(self.email_lists, "Mailing List")
        self.email_lists.mailing_list_added_sig.connect(self.list_added)
        self.email_lists.mailing_list_removed_sig.connect(self.list_removed)
        # Configure layouts
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(tabWidget)
        self.setLayout(mainLayout)
        buttonLayout = QtGui.QHBoxLayout()
        mainLayout.addLayout(buttonLayout)
        # Configure buttons
        okButton = QtGui.QPushButton(self)
        okButton.setText("Ok")
        cancelButton = QtGui.QPushButton(self)
        cancelButton.setText("Cancel")
        # Add buttons
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)
        # Configure buttons
        okButton.clicked.connect(self.saveData)
        cancelButton.clicked.connect(self.close)
        self.setWindowTitle("Notifier Settings")
        # Store all data
        self.saveData()
    def list_added(self, name):
        self.alert.add_mailing_list(name)

    def list_removed(self, name):
        self.alert.remove_mailing_list(name)

    def saveData(self):
        '''Save the data upon exit'''
        try:
            # For each device
            for device in web.devices:
                # Get the title
                title = device.getFrame().getTitle()
                # For each nickname (parameter)
                for nickname in device.getFrame().getNicknames():
                    # If the nickname is not none, then we can store the data
                    if(nickname is not None):
                        # The key is in the format device:paramName
                        key = title + ":" + nickname
                        # Temporary array used for assembling the data on each
                        # line
                        deviceDataArray = []
                        # Store the state of the checkbox
                        deviceDataArray.append(self.alert
                                               .allWidgetDict[key][0].isChecked())
                        if len(self.alert.allWidgetDict[key][1].text()) is not 0:
                            # Store the text if there is any
                            deviceDataArray.append(float(self.alert
                                                         .allWidgetDict[key][1].text()))
                        else:
                            # Otherwise store a blank string
                            deviceDataArray.append('')
                        if len(self.alert.allWidgetDict[key][2].text()) is not 0:
                            deviceDataArray.append(float(self.alert
                                                         .allWidgetDict[key][2].text()))
                        else:
                            deviceDataArray.append('')
                        deviceDataArray.append(self.email_list.get_items())
                        if(deviceDataArray[1] > deviceDataArray[2]
                                and deviceDataArray[1] is not None
                                and deviceDataArray[2] is not None):
                            raise
                        self.allDataDict[title + ":" +
                                         nickname] = deviceDataArray
                # Pickle the arrays and store them
            pickle.dump(self.allDataDict, open(
                os.path.join(self.location, str(self.loader)+'_NotifierSettings.config'), 'wb'))
            self.alert.allDataDict = self.allDataDict
            web.limitDict = self.allDataDict
        except ValueError:
            print("Enter only numbers into 'Minimum' and 'Maximum' fields.")
            print("Data Not Saved")
        except IOError as e:
            print "Unable to save notifier config data:"
            print e
        except:
            print("Minimum values cannot be greater than maximum values.")
            print("Data Not Saved")
        self.close()

    def getDict(self):
        return self.alert.allDataDict


class AlertConfig(QtGui.QWidget):

    def __init__(self, location, loader, parent=None):
        super(AlertConfig, self).__init__(parent)
        # Configure the layout
        layout = QtGui.QGridLayout()
        # where to find the notifier data
        self.location = location
        # Set the layout
        self.setLayout(layout)
        self.loader = loader
        self.mins = {}
        self.maxs = {}
        self.contacts = {}
        self.checkBoxes = {}
        self.allWidgetDict = {}
        # Retreive the previous settings
        self.openData()
        # Set up font
        font = QtGui.QFont()
        font.setPointSize(14)
        # Labels for the columns
        enablelbl = QtGui.QLabel()
        enablelbl.setText("Enable")
        layout.addWidget(enablelbl, 1, 2)

        minlbl = QtGui.QLabel()
        minlbl.setText("Minimum")
        layout.addWidget(minlbl, 1, 3)

        maxlbl = QtGui.QLabel()
        maxlbl.setText("Maximum")
        layout.addWidget(maxlbl, 1, 5)

        mailing_list_lbl = QtGui.QLabel()
        mailing_list_lbl.setText("Mailing Lists")
        layout.addWidget(mailing_list_lbl, 1, 7)
        # These are indexing variables
        z = 1
        x = 0
        # Go through and add all of the devices and their parameters to the
        # gui.
        for i in range(1, len(web.devices) + 1):
            # j is also used for indexing
            j = i - 1
            # Create the labels for all parameters
            label = QtGui.QLabel()
            label.setText(web.devices[j].getFrame().getTitle())
            label.setFont(font)
            layout.addWidget(label, z, 1)
            z = z + 1
            # Create all of the information fields and put the saved data in
            # them.
            for y in range(1, len(web.devices[j].getFrame().getNicknames()) + 1):
                paramName = web.devices[j].getFrame().getNicknames()[y - 1]
                u = y - 1
                if(paramName is not None):
                    title = web.devices[j].getFrame().getTitle()
                    nickname = web.devices[j].getFrame().getNicknames()[u]
                    key = (title + ":" + nickname)
                    if(key in self.allDataDict):
                        for data in self.allDataDict[key]:
                            # All widget dict holds the Qt objects
                            self.allWidgetDict[key] = [QtGui.QCheckBox(),
                                                       QtGui.QLineEdit(),
                                                       QtGui.QLineEdit(),
                                                       MCheckableComboBox(color_scheme="light")]
                            self.allWidgetDict[key][0].setChecked(
                                self.allDataDict[key][0])
                            self.allWidgetDict[key][1].setText(
                                str(self.allDataDict[key][1]))
                            self.allWidgetDict[key][2].setText(
                                str(self.allDataDict[key][2]))
                         #   self.allWidgetDict[key][3].setText(
                         #       str(self.allDataDict[key][3]))
                    else:
                        self.allWidgetDict[key] = [QtGui.QCheckBox(),
                                                   QtGui.QLineEdit(),
                                                   QtGui.QLineEdit(),
                                                   QtGui.QLineEdit()]
                    label = QtGui.QLabel()
                    # Add the new widgets
                    label.setText(paramName)
                    layout.addWidget(label, z, 1)
                    layout.addWidget(self.allWidgetDict[key][1], z, 3)
                    layout.addWidget(self.allWidgetDict[key][2], z, 5)
                    layout.addWidget(self.allWidgetDict[key][3], z, 7)
                    layout.addWidget(self.allWidgetDict[key][0], z, 2)

                    unitLabel = QtGui.QLabel()
                    if web.devices[j].getFrame().getUnit(paramName) is not None:
                        unitLabel.setText(str(web.devices[j].getFrame()
                                              .getUnit(paramName)))
                        layout.addWidget(unitLabel, z, 4)

                    layout.addWidget(unitLabel, z, 6)
                    # These are used for indexing
                    z = z + 1
                    x = x + 1
    def add_mailing_list(self, str):
        for key in self.allWidgetDict.keys():
            #print self.allWidgetDict
            self.allWidgetDict[key][3].addItem(str)
    def remove_mailing_list(self, str):
        for key in self.allWidgetDict.keys():
            #print self.allWidgetDict
            print key, str

            self.allWidgetDict[key][3].removeItem(str)
    def openData(self):
        '''Retreive a user's previous settings.'''
        try:
            print "Starting notifier, looking for config file: ",str(self.loader)+'_NotifierSettings.config'
            self.allDataDict = pickle.load(open(os.path.join(
                self.location, str(self.loader)+'_NotifierSettings.config'), 'rb'))
            NotifierGUI.allDataDict = self.allDataDict
            print "Config Data Opened"

        except:
            #traceback.print_exc()
            self.allDataDict = {}
            print("No notifier config file found")
        return self.allDataDict

class MMailingLists(QtGui.QWidget):
        mailing_list_added_sig = pyqtSignal(str)
        mailing_list_removed_sig = pyqtSignal(str)
        def __init__(self, parent=None):
            '''Initialize the Notifier Gui'''
            super(MMailingLists, self).__init__(parent)
            self.main_v_box = QtGui.QVBoxLayout()
            self.setLayout(self.main_v_box)

            self.mailing_lists = {}
            self.mailing_list_widgets = {}
           # self.mailing_lists["list1"] = ["email1", "email2"]
            #self.mailing_list_widgets["list1"] = MEditableList(self.mailing_lists["list1"])
            # Create a new tab
            self.tabWidget = QtGui.QTabWidget()
            self.main_v_box.addWidget(self.tabWidget)
            # Add list button
            self.add_list_button_layout = QtGui.QHBoxLayout()
            self.main_v_box.addLayout(self.add_list_button_layout)
            self.add_list_button = QtGui.QPushButton("Add Mailing List...")
            self.delete_list_button = QtGui.QPushButton("Delete Mailing List...")
            self.add_list_button.clicked.connect(self.addList_gui)
            self.delete_list_button.clicked.connect(self.deleteList_gui)
            self.add_list_button_layout.addWidget(self.add_list_button)
            self.add_list_button_layout.addWidget(self.delete_list_button)
            self.add_list_button_layout.addStretch(0)

            for list in self.mailing_lists.keys():
                self.tabWidget.addTab(self.mailing_list_widgets[list], list)
        def addList_gui(self):
            text, accept = QtGui.QInputDialog.getText(self, "Add Mailing List", "List name:")
            if accept:
                self.addList(text, [])
        def addList(self, listName, entries):
            self.mailing_lists[listName] = []
            self.mailing_list_widgets[listName] = MEditableList(self.mailing_lists[listName])
            self.tabWidget.addTab(self.mailing_list_widgets[listName], listName)
            self.mailing_list_added_sig.emit(listName)

        def deleteList_gui(self):
            text, accept = QtGui.QInputDialog.getItem(self, "Add Mailing List", "Select the list to delete", self.mailing_lists.keys())
            if accept:
                self.deleteList(text)
        def deleteList(self, listName):
            # find the correct tab
            num_tabs = self.tabWidget.count()
            for tab_index in range(num_tabs):
                if(self.tabWidget.tabText(tab_index) == listName):
                    print "removing tab", listName
                    #self.tabWidget.widget(tab_index).setParent(None)  # Delete widget
                    self.tabWidget.removeTab(tab_index)
                    del self.mailing_lists[listName]
                    self.mailing_list_removed_sig.emit(listName)
                    break



class MEditableList(QtGui.QWidget):
    updateSignal = pyqtSignal(str)
    removeSignal = pyqtSignal(str)
    def __init__(self, elems, parent = None):
        super(MEditableList, self).__init__(parent)
        self.item_list = QtGui.QListWidget()
        self.item_list.setStyleSheet(  "QListWidget::item {"
                                     "border-style: solid  ;" 
                                     "border-width:0.2px;" 
                                     "border-color:black;" 
                                     "background-color: rgb(255, 255, 255);"
                                  "}"
                                  "QListWidget::item:selected {"
                                     "background-color: rgb(52, 73, 94);"
                                     "border-style: none ;" 
                                     "border-width:0.8px;" 
                                  "}")
        #item_list.setFlags(QtCore.Qt.ItemIsEditable)

        main_v_box = QtGui.QVBoxLayout()
        #main_v_box.addWidget(QtGui.QLabel("Mailing List:"))

        main_v_box.addWidget(self.item_list)

        list_item_layout = QtGui.QHBoxLayout()
        #list_item_layout.addWidget(QtGui.QLabel("Test item"))

        self.item_widget_labels = []
        self.item_widget_edit_pbs = []
        self.item_widget_remove_pbs = []
        for elem in elems:
            self.add_item(elem)

        add_item_layout = QtGui.QHBoxLayout()
        add_item_button = QtGui.QPushButton("Add...")
        add_item_button.clicked.connect(self.__add_item)
        add_item_layout.addWidget(add_item_button)

        add_item_widget = QtGui.QWidget()
        add_item_widget.setLayout(add_item_layout)

        add_item_layout.addStretch(0)
        #add_item_item = QtGui.QListWidgetItem()
        #add_item_item.setSizeHint(add_item_widget.sizeHint())

        #self.item_list.addItem(add_item_item)
        #self.item_list.setItemWidget(add_item_item, add_item_widget)
        main_v_box.addWidget(add_item_widget)

        self.setLayout(main_v_box)
    def get_items(self):
        text = []
        for label in self.item_widget_label:
            text.append(label.text())
        print "Editable list text:", text
        return text
    def __add_item(self):
        text, accept = QtGui.QInputDialog.getText(self, "Add Entry...", "Email:")
        if(accept):
            self.add_item(text)

    def add_item(self, text):

        item_widget_label = QtGui.QLabel(text)

        #item_widget_edit_pb = QtGui.QPushButton("Edit")
        item_widget_remove_pb = QtGui.QPushButton("Remove")

        #item_widget_edit_pb.clicked.connect(lambda x:self.edit_item(text))
        item_widget_remove_pb.clicked.connect(lambda x: self.remove_item(text))

        item_widget_label.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)
        #item_widget_edit_pb.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)
        item_widget_remove_pb.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)

        self.item_widget_labels.append(item_widget_label)
        #self.item_widget_edit_pbs.append(item_widget_edit_pb)
        self.item_widget_remove_pbs.append(item_widget_remove_pb)

        item_widget_layout = QtGui.QHBoxLayout()
        item_widget_layout.addWidget(item_widget_label)
        item_widget_layout.addStretch(0)
        #item_widget_layout.addWidget(item_widget_edit_pb)
        item_widget_layout.addWidget(item_widget_remove_pb)


        item_widget = QtGui.QWidget()
        item_widget.setLayout(item_widget_layout)
        item_widget.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)
        item = QtGui.QListWidgetItem()
        item.setSizeHint(item_widget.sizeHint())

        item.setFlags(item.flags())
        self.item_list.addItem(item)
        self.item_list.setItemWidget(item, item_widget)

        num_items = self.item_list.count()
        self.item_list.insertItem(num_items - 1, item)

    def remove_item(self, item):
        for index in range(self.item_list.count()):
            if(item == self.item_list.itemWidget(self.item_list.item(index)).layout().itemAt(0).widget().text()):

                self.item_list.takeItem(index)
        pass