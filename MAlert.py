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
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
import Queue

class MAlert(QThread):

    mail_queue = Queue.Queue()
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
                            print "MALERT reading below min ", min
                            dev.setOutOfRange(param)
                            self.queueMail(dev, param, reading, web.alert_data.get_subscribers(key), min, max)
                            # print " min sent to ", people
                        elif(max != None and max < reading):
                            dev.setOutOfRange(param)
                            self.queueMail(dev, param, reading, people, min, max)
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
        while(True):
            #print("Running MAlert")
            #HOURS_BETWEEN_EMAILS = 3

            list_and_messages = {}
            web.persistentData.persistentDataAccess(None, "NotifierInfo")
            while(not self.mail_queue.empty()):
                list, message = self.mail_queue.get()
                if list not in list_and_messages.keys():
                    list_and_messages[list] = {"Messages" : [], "TimeLastSent" : -1}
                else:
                    list_and_messages[list]["Messages"].append(message)
                now = time.time()
                for list in list_and_messages.keys():
                    if((now -  list_and_messages[list]["TimeLastSent"]) > self.mailingPeriod):
                        list_and_messages[list]["TimeLastSent"] = now
                        recipients = web.alert_data.get_members(list)
                        success = web.tele.sendMail(
                            recipients,
                            "MView Mailing List " + list,
                            str(web.title),
                            str('\n'.join(message))
                        )
                self.queuedMail[list] = []
            self.sleep(1)



            # recipients =  [str(person).strip() for person in self.people.split(',')]
            # if(len(recipients) != 0 and not self.mail_queue.empty()):
            #     message = []
            #     while(not self.mail_queue.empty()):
            #         message.append(self.mail_queue.get() + "\n")
            #     print message
            #     success = web.tele.sendMail(
            #         recipients,
            #         "MView",
            #         str(web.title),
            #         str('\n'.join(message))
            #     )
            #     if not success:
            #         print "Error while sending mail."
            #     else:
            #         print "sleeping for 3 hours"
            #         self.sleep(self.mailing_period)


    def queueMail(self, device, param, reading, addresses, min, max):
        '''Send mail if the given amount of time has elapsed.'''

       # elapsedHrs = (time.time() - self.t1) / 3600
        key = str(device) + ":" + param
        for address in addresses:
            if address not in self.queuedMail.keys():
                self.queuedMail[address] = []
            if(key not in self.queuedMail[address]):
                unit = device.getUnit(param)
                unit = unit if unit else ''
                min = min if min else ''
                max = max if max else ''
                self.message = (time.strftime('%x at %X', time.localtime(time.time()))
                                         + " | " + str(device) + "->"
                                         + param + ": " +
                                         str(device.getReading(param)) + " " +
                                         str(unit) +
                                         " | Range: "
                                         + str(str(min)) + " "
                                         + str(device.getUnit(param)) +
                                         " - " + str(str(max)) + " " +
                                         str(device.getUnit(param)) + ".")
                #people = web.alert_data.getMembersOfList(list)
                self.mail_queue.put([address, self.message])

                self.queuedMail[address].append(key)

        # if people != '':
        #     if(not self.mailSent[key]):
        #
        #         self.mailSent[key] = True
        #         self.message.append((time.strftime('%x at %X', time.localtime(time.time()))
        #                              + " | " + str(device) + "->"
        #                              + param + ": " +
        #                              str(device.getReading(param)) + " " +
        #                              str(device.getUnit(param)) +
        #                              " | Range: "
        #                              + str(str(min)) + " "
        #                              + str(device.getUnit(param)) +
        #                              " - " + str(str(max)) + " " +
        #                              str(device.getUnit(param)) + "."))
        #
        #     if(HOURS_BETWEEN_EMAILS < elapsedHrs):
        #         if not len([str(person).strip() for person in people.split(',')][0]) == 0:
        #             print "sending mail"
        #             # print self.message
        #             for key in self.mailSent:
        #                 self.mailSent[key] = False
        #             print "Email message:", self.message
        #             print "in MAlert web title", web.title
        #             success = self.tele.sendMail(
        #                 [str(person).strip() for person in people.split(',')],
        #                 "MView",
        #                 str(web.title) + ":" + str(device),
        #                 str('\n'.join(self.message))
        #                 )
        #             print [str(person).strip() for person in people.split(',')]
        #             if (not success):
        #                 print("Couldn't send email to group.");
        #             self.message = []
        #             for key in self.mailSent:
        #                 self.mailSent[key] = False
        #             self.t1 = time.time()
