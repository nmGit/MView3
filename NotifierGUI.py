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
import pprint
sys.dont_write_bytecode = True
from functools import partial

class Notifier:
    # Lists take the form:
    # self.lists = {"list1":
    #                   {"Members":
    #                       ["Member1", "Member1",...],
    #                    "Subscriptions":
    #                       ["device1:param1, "device1:param2", "device2:param1",...]
    #                    }
    #               "list2": ...
    #              }
    pp = pprint.PrettyPrinter(indent=4)
    def __init__(self):
        self.lists = {}
        self.limits = {}
        self.open()
    def add_list(self, list):
        self.lists[str(list)] = {"Members":[], "Subscriptions":[]}
    def add_members(self, mailinglist, members):
        if type(members) is list:
            self.lists[str(mailinglist)]["Members"].extend(members)
        else:
            self.lists[str(mailinglist)]["Members"].append(str(members))
        print "added members", members
        self.pp.pprint(self.lists)
    def add_subscription(self, mailinglist, subscription_keys):
        mailinglist = str(mailinglist)
        print "adding subscriptions", subscription_keys
        if type(subscription_keys) is list:
            print "is array"
            self.lists[mailinglist]["Subscriptions"].extend(subscription_keys)
        else:
            print "is not array"
            subscription_keys = str(subscription_keys)
            self.lists[mailinglist]["Subscriptions"].append(str(subscription_keys))
        self.pp.pprint(self.lists)

    def remove_list(self, list):
        del self.lists[list]
        self.pp.pprint(self.lists)

    def remove_members(self, list, members):
        list = str(list)
        if type(members) is list:
            for member in members:
                index = self.lists[list]["Members"].index(member)
                del self.lists[list]["Members"][index]
        else:
            members = str(members)
            index = self.lists[list]["Members"].index(str(members))
            del self.lists[list]["Members"][index]
        self.pp.pprint(self.lists)

    def remove_subscription(self, list, subscriptions):
        list = str(list)
        if type(subscriptions) is list:
            for subscription in subscriptions:
                index = self.lists[list]["Subscriptions"].index(subscription)
                del self.lists[list]["Subscriptions"][index]
        else:
            index = self.lists[list]["Subscriptions"].index(str(subscriptions))
            del self.lists[list]["Subscriptions"][index]
        self.pp.pprint(self.lists)

    def set_enabled(self, key, state):
        if key not in self.limits.keys():
            self.limits[key] = {}
        self.limits[key]['enable'] = state
        self.pp.pprint(self.limits)
    def get_enabled(self, key):
        if key not in self.limits.keys():
            self.limits[key] = {}
            self.limits[key]['enable'] = False
        return self.limits[key]['enable']
    def set_min(self, key, min):
        return
    def get_min(self, key):
        return ''
    def set_max(self, key, min):
        return
    def get_max(self, key):
        return ''
    def get_mailing_lists(self):
        return self.lists
    # def get_members(self, list):
    #     print "get members:",self.lists
    #     return self.lists[list]['Members']
    def open(self):
        print "opening notifier data"
        print "---------------------------------------------------------"
        self.pp.pprint(web.persistentData.getDict())
        print "---------------------------------------------------------"
        saved_state = web.persistentData.getDict().get('NotifierInfo', False)
        if not saved_state:
            return
        else:
            saved_state = saved_state['Mailing']
        print "saved state", saved_state

        for list in saved_state.keys():
            subscriptions = saved_state[list]['Subscriptions']
            members = saved_state[list]['Members']
            print "saved members:", members
            print "saved subscriptions:", subscriptions
            self.add_list(list)
            self.add_members(list, members)
            self.add_subscription(list, subscriptions)
        print "done opening notifier data", self.lists
    def save(self):
        print "saving notifier data"
        if 'NotifierInfo' not in web.persistentData.getDict().keys():
            web.persistentData.getDict()['NotifierInfo'] = {'Mailing': {}, 'Limits': {}}
        web.persistentData.getDict()['NotifierInfo']['Mailing'] = self.lists
        web.persistentData.getDict()['NotifierInfo']['Limits'] = self.limits
class NotifierGUI(QtGui.QDialog):

    def __init__(self, loader, parent=None):
        '''Initialize the Notifier Gui'''
        super(NotifierGUI, self).__init__(parent)
        # Create a new tab
        tabWidget = QtGui.QTabWidget()
        web.alert_data.open()
        # The name of the main MView program
        self.loader = loader
        # The the config data should be stored with the the main class
        self.location = os.path.dirname(traceback.extract_stack()[0][0])
        # Dictionary that will store all data
        self.allDataDict = {}
        # print "Looking for config file in: ", self.location
        # New widget
        self.alert = AlertConfig(self.location, loader)
        self.alert.mailing_list_selected.connect(web.alert_data.add_subscription)
        self.alert.mailing_list_deselected.connect(web.alert_data.remove_subscription)
        # AlDatatxt holds the text contents of all data entered in table
        self.allDatatxt = [[], [], [], []]
        # The settings window has a tab
        tabWidget.addTab(self.alert, "Alert Configuration")
        # Create email list in a new tab
       # print self.alert.allDataDict

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
        okButton.clicked.connect(self.close_ok)
        cancelButton.clicked.connect(self.close_cancel)
        self.setWindowTitle("Notifier Settings")


#        self.saveData()
    def list_added(self, name):
        self.alert.add_mailing_list(name)
        web.alert_data.add_list(name)

    def list_removed(self, name):
        self.alert.remove_mailing_list(name)
        web.alert_data.remove_list(name)

    def getDict(self):
        return self.alert.allDataDict

    def close_cancel(self):
        self.close()
    def close_ok(self):
        web.alert_data.save()
        self.close()
class AlertConfig(QtGui.QWidget):
    list_change_made = pyqtSignal(str)
    mailing_list_selected = pyqtSignal(str,str)
    mailing_list_deselected = pyqtSignal(str, str)
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
        self.allDataDict = {}
        # Retreive the previous settings
        #self.openData()
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
        mailing_lists = web.alert_data.get_mailing_lists()
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
            key_copies = []
            for y in range(1, len(web.devices[j].getFrame().getNicknames()) + 1):
                paramName = web.devices[j].getFrame().getNicknames()[y - 1]
                u = y - 1
                if(paramName is not None):
                    title = web.devices[j].getFrame().getTitle()
                    nickname = web.devices[j].getFrame().getNicknames()[u]
                    key = (title + ":" + nickname)
                    combo_box = MCheckableComboBox(color_scheme="light")
                    key_copies.append(str("%s" % key))
                    combo_box.activated.connect(partial(self.combo_box_item_clicked, key))
                    enabled_chkbx = QtGui.QCheckBox()
                    min_lineedit = QtGui.QLineEdit()
                    max_lineedit = QtGui.QLineEdit()

                    enabled_chkbx.stateChanged.connect(partial(self.enable_state_changed, key))

                    self.allWidgetDict[key] = [enabled_chkbx,
                                               min_lineedit,
                                               max_lineedit,
                                               combo_box]
                    enabled_chkbx.setChecked(web.alert_data.get_enabled(key))
                    min_lineedit.setText(web.alert_data.get_min(key))
                    max_lineedit.setText(web.alert_data.get_max(key))

                    for list in mailing_lists.keys():
                        combo_box.addItem(list)
                        if key in mailing_lists[list]['Subscriptions']:

                            combo_box.setChecked(combo_box.findText(list), True)
                 #   self.allWidgetDict[key][3].setText(
                 #       str(self.allDataDict[key][3]))
                 #    else:
                 #        self.allWidgetDict[key] = [QtGui.QCheckBox(),
                 #                                   QtGui.QLineEdit(),
                 #                                   QtGui.QLineEdit(),
                 #                                   QtGui.QLineEdit()]
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
        print
    def combo_box_item_clicked(self, key, index):
        text = self.allWidgetDict[key][3].itemText(index)

        checked = self.allWidgetDict[key][3].isChecked(index)
        print "List changed:", key,  text,checked
        if(checked):
            self.mailing_list_selected.emit(text, key)
        else:

            self.mailing_list_deselected.emit(text, key)
        #self.sync_backend_with_frontend()
    def enable_state_changed(self, key, state):
        print "enable clicked", key, state
        web.alert_data.set_enabled(key, state)

    # def openData(self):
    #     '''Retreive a user's previous settings.'''
    #     try:
    #         print "Starting notifier, looking for config file: ",str(self.loader)+'_NotifierSettings.config'
    #         self.allDataDict = pickle.load(open(os.path.join(
    #             self.location, str(self.loader)+'_NotifierSettings.config'), 'rb'))
    #         NotifierGUI.allDataDict = self.allDataDict
    #         print "Config Data Opened"
    #
    #     except:
    #         #traceback.print_exc()
    #         self.allDataDict = {}
    #         print("No notifier config file found")
    #     return self.allDataDict

class MMailingLists(QtGui.QWidget):
        mailing_list_added_sig = pyqtSignal(str)
        mailing_list_removed_sig = pyqtSignal(str)
        def __init__(self, parent=None):
            '''Initialize the Notifier Gui'''
            super(MMailingLists, self).__init__(parent)
            self.main_v_box = QtGui.QVBoxLayout()
            self.setLayout(self.main_v_box)

            self.mailing_lists = web.alert_data.get_mailing_lists()
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
                self.addList(list)

                for member in self.mailing_lists[list]['Members']:
                    self.mailing_list_widgets[-1].addItem(member)
        def addList_gui(self):
            text, accept = QtGui.QInputDialog.getText(self, "Add Mailing List", "List name:")
            if accept:
                self.addList(text, [])
                web.alert_data.add_list(text)

        def addList(self, listName):
            listName = str(listName)

            self.mailing_lists[listName] = []
            self.mailing_list_widgets[listName] = MEditableList(self.mailing_lists[listName])
            self.tabWidget.addTab(self.mailing_list_widgets[listName], listName)
            #
            #web.alert_data.add_members(listName,entries)
            self.mailing_list_widgets[listName].item_added.connect(partial(web.alert_data.add_members, listName))
            self.mailing_list_widgets[listName].item_removed.connect(partial(web.alert_data.remove_members, listName))
            self.mailing_list_added_sig.emit(listName)

        def deleteList_gui(self):
            text, accept = QtGui.QInputDialog.getItem(self, "Add Mailing List", "Select the list to delete", self.mailing_lists.keys())
            if accept:
                self.deleteList(text)
        def deleteList(self, listName):
            # find the correct tab
            num_tabs = self.tabWidget.count()
            web.alert_data.remove_list(listName)
            for tab_index in range(num_tabs):
                if(self.tabWidget.tabText(tab_index) == listName):
                    print "removing tab", listName
                    #self.tabWidget.widget(tab_index).setParent(None)  # Delete widget
                    self.tabWidget.removeTab(tab_index)
                    del self.mailing_lists[listName]
                    self.mailing_list_removed_sig.emit(listName)
                    break



class MEditableList(QtGui.QWidget):
    item_added = pyqtSignal(str)
    item_removed = pyqtSignal(str)
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
        item_widget_remove_pb.clicked.connect(partial(self.remove_item,text))

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
        self.item_added.emit(text)
    def remove_item(self, item):
        try:
            for index in range(self.item_list.count()):
                #print "looking at index", index, self.item_list.itemWidget(self.item_list.item(index)).layout().itemAt(0).widget().text()
                if(item == self.item_list.itemWidget(self.item_list.item(index)).layout().itemAt(0).widget().text()):
                     self.item_list.takeItem(index)
                     break;
            self.item_removed.emit(item)
        except:
            traceback.print_stack()
            traceback.print_exc()