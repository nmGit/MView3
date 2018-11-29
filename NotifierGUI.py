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
        #self.limits = {}
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
        list = str(list)
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

        web.persistentData.persistentDataAccess(state, "NotifierInfo", key, "enable")

    def get_enabled(self, key):

        return web.persistentData.persistentDataAccess(None, "NotifierInfo", key, "enable", default=False)
    def set_min(self, key, minimum):
        web.persistentData.persistentDataAccess(minimum, "NotifierInfo", "Limits", key, "Min")
        #self.limits[key]["Min"] = minimum
        return
    def get_min(self, key):
        minimum = web.persistentData.persistentDataAccess(None, "NotifierInfo", "Limits", key, "Min", default=None)

        return minimum
    def set_max(self, key, maximum):
        web.persistentData.persistentDataAccess(maximum, "NotifierInfo", "Limits", key, "Max")
        #self.limits[key]["Max"] = maximum
        return
    def get_max(self, key):
        maximum = web.persistentData.persistentDataAccess(None, "NotifierInfo", "Limits", key, "Max", default=None)

        return maximum
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
        limits = web.persistentData.getDict()['NotifierInfo']['Limits']
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
       # web.persistentData.getDict()['NotifierInfo']['Limits'] = limits

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

        # Configure password input
        self.login_config = LoginConfig()
        tabWidget.addTab(self.login_config, "Mailer Configuration")
        self.login_config.email_credential_change_made.connect(self.email_changed)
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
    def email_changed(self, host, email, pwd):
        web.telecomm.changeCredentials(host, email, pwd)

    def close_cancel(self):
        self.close()
    def close_ok(self):
        web.alert_data.save()
        self.close()

class LoginConfig(QtGui.QWidget):
    email_credential_change_made = pyqtSignal(str, str, str)

    def __init__(self, parent = None):
        super(LoginConfig, self).__init__(parent)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)


        email = web.persistentData.persistentDataAccess(None,'Email', 'Address', default = None)
        pwd = web.persistentData.persistentDataAccess(None,'Email', 'Password', default = None)
        host = web.persistentData.persistentDataAccess(None,'Email', 'Host', default = None)

        host_layout = QtGui.QHBoxLayout()
        host_layout.addWidget(QtGui.QLabel("Host Address:"))
        host_layout.addStretch(0)
        self.host_input = QtGui.QLineEdit()
        if(host and type(host) is str):
            self.host_input.setText(host)
        else:
            self.host_input.setPlaceholderText("smtp.googlemail.com for GMail")
        host_layout.addWidget(self.host_input)

        username_layout = QtGui.QHBoxLayout()
        username_layout.addWidget(QtGui.QLabel("Email Address:"))
        username_layout.addStretch(0)
        self.username_input = QtGui.QLineEdit()
        if(email and type(email) is str):
            self.username_input.setText(email)

        username_layout.addWidget(self.username_input)

        pwd_layout = QtGui.QHBoxLayout()
        pwd_layout.addWidget(QtGui.QLabel("Email Password:"))
        pwd_layout.addStretch(0)
        self.pwd_input = QtGui.QLineEdit()
        if(pwd and type(pwd) is str):
            self.pwd_input.setText(pwd)
        self.pwd_input.setEchoMode(QtGui.QLineEdit.Password)
        pwd_layout.addWidget(self.pwd_input)

        layout.addLayout(username_layout)
        layout.addLayout(pwd_layout)
        layout.addLayout(host_layout)

        self.username_input.textEdited.connect(self.email_changed)
        self.pwd_input.textEdited.connect(self.pwd_changed)
        self.host_input.textEdited.connect(self.host_changed)

        verify_pb = QtGui.QPushButton("Verify and save...")
        verify_pb.clicked.connect(self.verify_email)
        pb_layout = QtGui.QHBoxLayout()
        pb_layout.addStretch(0)
        pb_layout.addWidget(verify_pb)
        layout.addLayout(pb_layout)
        layout.addStretch(0)
        warning_lbl = QtGui.QLabel("NOTE: These login credentials are NOT stored securely."
                                      " Please only use a dedicated email address."
                                      " DO NOT use an organizational email address.")
        warning_lbl.setWordWrap(True)
        layout.addWidget(warning_lbl)
    def verify_email(self):
        host = self.host_input.text()
        email = self.username_input.text()
        pwd = self.pwd_input.text()
        success = web.telecomm.verify(host, email, pwd)
        if(success):
            self.email_credential_change_made.emit(host, email, pwd)
        pass
    def email_changed(self):
        pass
    def pwd_changed(self):
        pass
    def host_changed(self):
        pass
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

                    maximum = web.alert_data.get_max(key)
                    minimum = web.alert_data.get_min(key)

                    if(maximum):
                        max_lineedit.setText(str(maximum))
                    if(minimum):
                        min_lineedit.setText(str(minimum))

                    min_lineedit.editingFinished.connect(partial(self.min_val_changed, key, min_lineedit.text))
                    max_lineedit.editingFinished.connect(partial(self.max_val_changed, key, max_lineedit.text))
                    enabled_chkbx.stateChanged.connect(partial(self.enable_state_changed, key))

                    self.allWidgetDict[key] = [enabled_chkbx,
                                               min_lineedit,
                                               max_lineedit,
                                               combo_box]
                    enabled_chkbx.setChecked(web.alert_data.get_enabled(key))
                    #min_lineedit.setText(web.alert_data.get_min(key))
                    #max_lineedit.setText(web.alert_data.get_max(key))

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
    def min_val_changed(self, key, text):
        if(callable(text)):
            text = text()
        print "Min val changed", key, text
       # if ('E' == text[-1] or 'e' == text[-1] or '-' == text[-1] or '.' == text[-1]):
       #     return
        text = str(text)
        if (len(text.strip()) == 0):
            return
        try:
            val = float(text)

        except ValueError:

            QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Invalid Minimum Value", "Minimum Value must be a number "
                                                                                  "in one of the following forms:\n\n"
                                                                                  "1234.5678\n"
                                                                                  "1.24E56\n\n"
                                                                                  "Changes not saved.",
                              QtGui.QMessageBox.Ok).exec_()
            return
        web.alert_data.set_min(key, val)

    def max_val_changed(self, key, text):
      #  if ('E' == text[-1] or 'e' == text[-1] or '-' == text[-1]):
      #      return\
        if (callable(text)):
            text = text()
        text = str(text)
        if (len(text.strip()) == 0):
            return
        try:
            val = float(text)

        except ValueError:
            QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Invalid Maximum Value", "Maximum Value must be a number "
                                                                                  "in one of the following forms:\n\n"
                                                                                  "1234.5678\n"
                                                                                  "1.24E56\n\n"
                                                                                  "Changes not saved.",
                              QtGui.QMessageBox.Ok).exec_()
            return
        web.alert_data.set_max(key, val)

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
            ml = web.alert_data.get_mailing_lists()
            self.mailing_lists = {}
            self.mailing_list_widgets = {}

            self.mailing_period_label = QtGui.QLabel("Mailing Period:")
            self.mailing_period_edit = QtGui.QLineEdit()
            self.mailing_period_unit = QtGui.QComboBox()
            self.mailing_period_unit.addItem("Days")
            self.mailing_period_unit.addItem("Hours")
            self.mailing_period_unit.addItem("Minutes")
            self.mailing_period_unit.addItem("Seconds")

            self.mailing_period_layout = QtGui.QHBoxLayout()
            self.mailing_period_layout.addWidget(self.mailing_period_label)
            self.mailing_period_layout.addStretch(0)
            self.mailing_period_layout.addWidget(self.mailing_period_edit)
            self.mailing_period_layout.addWidget(self.mailing_period_unit)

            self.main_v_box.addLayout(self.mailing_period_layout)

            self.mailing_period_edit.editingFinished.connect(self.mailingPeriodEdited)
            self.mailing_period_unit.activated.connect(self.mailingPeriodEdited)
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
            print "Notifier GUI mailing_lists", ml
            for list in ml.keys():
                self.addList(list)
                print "Constructing",ml[list]
                members = [member for member in ml[list]['Members']]
                print "adding members", members
                for member in members:
                    print "\t adding member", member
                    self.mailing_list_widgets[list].add_item(member, backend=True)
        def addList_gui(self):
            text, accept = QtGui.QInputDialog.getText(self, "Add Mailing List", "List name:")
            if accept:
                self.addList(text)
                web.alert_data.add_list(text)
            self.mailing_list_added_sig.emit(text)

        def addList(self, listName):
            listName = str(listName)
            if(listName not in self.mailing_lists.keys()):
                self.mailing_lists[listName] = {}
            self.mailing_list_widgets[listName] = MEditableList(self.mailing_lists[listName])
            self.tabWidget.addTab(self.mailing_list_widgets[listName], listName)

            self.mailing_list_widgets[listName].item_added.connect(partial(web.alert_data.add_members, listName))
            self.mailing_list_widgets[listName].item_removed.connect(partial(web.alert_data.remove_members, listName))

        def deleteList_gui(self):
            text, accept = QtGui.QInputDialog.getItem(self, "Add Mailing List", "Select the list to delete", self.mailing_lists.keys())
            if accept:
                self.deleteList(text)
        def deleteList(self, listName):
            listName = str(listName)
            # find the correct tab
            num_tabs = self.tabWidget.count()
            #web.alert_data.remove_list(listName)
            for tab_index in range(num_tabs):
                if(self.tabWidget.tabText(tab_index) == listName):
                    print "removing tab", listName
                    #self.tabWidget.widget(tab_index).setParent(None)  # Delete widget
                    self.tabWidget.removeTab(tab_index)
                    del self.mailing_lists[listName]
                    self.mailing_list_removed_sig.emit(listName)
                    break

        def mailingPeriodEdited(self, unit = None):
            if not unit:
                unit = self.mailing_period_unit.currentText()
                web.persistentData.persistentDataAccess(unit)

            try:
                value = float(self.mailing_period_edit.text())
                web.persistentData.persistentDataAccess(unit)
            except ValueError:
                self.mailing_period_edit.clear()
                QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Invalid period", "Period Value must be a number "
                                                                                      "in one of the following forms:\n\n"
                                                                                      "1234.5678\n"
                                                                                      "1.24E56\n\n"
                                                                                      "Changes not saved.",
                                  QtGui.QMessageBox.Ok).exec_()

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
    def __add_item(self, **kwargs):
        text, accept = QtGui.QInputDialog.getText(self, "Add Entry...", "Email:")
        if(accept):
            self.add_item(text, **kwargs)

    def add_item(self, text, **kwargs):

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
        if(not kwargs.get("backend", False)):
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