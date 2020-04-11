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
__version__ = "2.0.0"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"

"""
version = 2.0.0
description = Handles all data error checking
"""

import smtplib
import MMail
import threading

import time
import sys
from MWeb import web
sys.dont_write_bytecode = True
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
import queue

class MAlert(QThread):

    mail_queue = queue.Queue()
    queuedMail = {}
    def __init__(self):
        super(MAlert, self).__init__()
        # Configure all public variables
        web.telecomm = MMail.MMail()
        self.devices = web.devices
        self.t1 = 0
        self.message = []
        self.people = ''
        # Have the specified people been notified about the specific device?
        self.mailSent = {}
        # Keep running, this is false when settings are changed and a
        # new NAlert instance is created. Setting this to false terminates
        # the thread.
        self.keepGoing = True
        # Keep track of which mail was sent
        for i in range(0, len(self.devices)):
            for y in range(0, len(self.devices[i].getFrame().getNicknames())):
                if(self.devices[i].getFrame().getNicknames()[y] is not None):
                   # print self.mailSent
                    self.mailSent[self.devices[i].getFrame().getTitle(
                    ) + ":" + self.devices[i].getFrame().getNicknames()[y]] = False
                    # print(len(self.mailSent))
        self.start()
    def begin(self):
        # This runs on its own thread

        self.keepGoing = True

    def setMailingPeriod(self, period_in_seconds):
        self.mailingPeriod = period_in_seconds

    def monitorReadings(self, dev):
        # The dictionary keys are in the format 'devicename:parametername' : '
       # print "checking readigns"

           # print "checking device", i
           # print "nicknames:", self.devices[i].getFrame().getNicknames()
        for y, param in enumerate(dev.getFrame().getNicknames()):
                # print "checking param", param
                # print "Nicknames from MAlert:",
                # self.devices[i].getFrame().getNicknames()
            key = dev.getFrame().getTitle() + ":" + \
                dev.getFrame().getNicknames()[y]
         #   if(key in web.limitDict):
            enabled = web.persistentData.persistentDataAccess(None, "NotifierInfo", "Limits", key,  "enable", default=False)
            min = None
            max = None
            if enabled:
                min = web.persistentData.persistentDataAccess(None, "NotifierInfo", "Limits", key,  "Min", default=None)
                max = web.persistentData.persistentDataAccess(None, "NotifierInfo", "Limits", key, "Max", default=None)

            else:
                web.limitDict[key]= (False, None, None, None)
                continue
            if(min or max):
                min = self.toFloat(min)
                max = self.toFloat(max)
                if dev.getFrame().getReading(param) != None:
                    reading = dev.getFrame().getReading(param)
                    # print "enabled: ", enabled
                    if(enabled):

                        if(min != None and min > reading):
                            #print "MALERT reading below min ", min
                            dev.setOutOfRange(param)
                            self.queueMail(dev, param, reading, key, min, max)
                            # print " min sent to ", people
                        elif(max != None and max < reading):
                            dev.setOutOfRange(param)
                            self.queueMail(dev, param, reading, key, min, max)
                            # print " max sent to ", people

                        else:
                            dev.getFrame().setInRange(param)
                    else:
                        dev.getFrame().setInRange(param)

    def toFloat(self, val):
        try:
            return float(val)
        except:
            return None

    def stop(self):
        self.keepGoing = False

    def run(self):
        list_and_messages = {}
        while(True):
            # Run once a second
            self.sleep(1)
            # Wait until there is something in the mail queue
            if(not self.mail_queue.empty()):
                # "DEQUEUEING"
                # Retrieve what is on the mail queue
                mailing_list, message = self.mail_queue.get()
                # If the mailing list has never been registered in list_and_messages, then register it.
                #print "list and messages:", list_and_messages
                if mailing_list not in list_and_messages.keys():
                    list_and_messages[mailing_list] = {"Messages": [message], "TimeLastSent": -1}
                # Otherwise add the message to the list of outgoing messages for the given list.
                else:
                    list_and_messages[mailing_list]["Messages"].append(message)

            # Go through all mailing lists and decide whether or not to send the message
            for mailing_list in list_and_messages.keys():
                # Base our decision on whether or not to send on the elaped time
                now = time.time()
                elapsed_time = now - list_and_messages[mailing_list]["TimeLastSent"]
                # Get the messages
                messages = list_and_messages[mailing_list]["Messages"]
                # Get the recipients
                recipients = web.alert_data.get_members(mailing_list)

               # print "elapsed time:", list_and_messages

                # If there are messages to send and enough time has elapsed, then send the message.
                # Also ensure that there are recipients
                if(len(recipients) != 0 and len(messages) != 0 and elapsed_time > self.mailingPeriod):
                    list_and_messages[mailing_list]["TimeLastSent"] = now

                    try:
                        success = web.telecomm.sendMail(
                            recipients,
                            "MView Mailing List",
                            str(web.title),
                            str("\n".join(messages))
                        )
                    except:
                        print("Mailing failed!")
                    list_and_messages[mailing_list]["Messages"] = []

                    for key in self.queuedMail[mailing_list].keys():
                        self.queuedMail[mailing_list][key] = False

    def queueMail(self, device, param, reading, key, min, max):
        '''Send mail if the given amount of time has elapsed.'''

        # Get all lists which subscribe to this key
        subscribing_lists = web.alert_data.get_subscribing_lists(key)

        # Iterate over all lists that subscribe to this key and queue mail for the list if necessary
        for mailing_list in subscribing_lists:
            # If this mailing list is not registered, then register it
            if mailing_list not in self.queuedMail.keys():
                self.queuedMail[mailing_list] = {}
            if key not in self.queuedMail[mailing_list].keys():
                self.queuedMail[mailing_list][key] = False
            # Check if mail has already been queued for this list (the queuedMail is reset anytime mail is sent to
            # that mailing list).
            # print "Queued mail:", self.queuedMail
            if(not self.queuedMail[mailing_list][key]):
                unit = device.getUnit(param)
                unit = unit if unit else ''
                min = min if min else '-infinity'
                max = max if max else 'infinity'
                self.message = (time.strftime('%x at %X', time.localtime(time.time()))
                                         + " | " + str(device) + "->"
                                         + param + ": " +
                                         str(device.getReading(param)) + " " +
                                         str(unit) +
                                         " | Range: "
                                         + str(str(min)) + " "
                                         + str(unit) +
                                         " to " + str(str(max)) + " " +
                                         str(unit) + ".")
                # Queue mail
                # print "QUEUEING"
                self.mail_queue.put([mailing_list, self.message])
                # Mark the key is queued for the given mailing list
                self.queuedMail[mailing_list][key] = True
