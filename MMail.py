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
__version__ = "1.0.2"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"

import smtplib
from email.mime.text import MIMEText
import MPopUp
import traceback
from MWeb import web
from PyQt5 import QtCore, QtGui

class MMail:
    """Very simple email client."""

    def __init__(self):
        self.mail_sem = QtCore.QSemaphore(1)
        try:
            self.email = web.persistentData.getDict()['Email']['Address']
            self.pwd = web.persistentData.getDict()['Email']['Password']
            self.host = web.persistentData.getDict()['Email']['Host']

            if(self.email):
                print("Initializing MMail...")
                self.smtpObj = smtplib.SMTP(self.host, timeout = 3)
                # Say hello to the email server.
                self.smtpObj.ehlo()
                # Initialize TLS security.
                self.smtpObj.starttls()

                self.smtpObj.login(self.email, self.pwd)
                self.smtpObj.quit()

        except:
            MPopUp.PopUp("Notifier failed to login to email.\n\n" + traceback.format_exc(1)).exec_()
            #traceback.print_exc()

        # Send the email.
       # 'smtp.googlemail.com'
    def verify(self, host, email, pwd):
        true_if_success = True
        host = str(host)
        email = str(email)
        pwd = str(pwd)
        try:
            self.smtpObj = smtplib.SMTP(host, timeout=3)
            # Say hello to the email server.
            self.smtpObj.ehlo()
            # Initialize TLS security.
            self.smtpObj.starttls()

            self.smtpObj.login(email, pwd)
            self.smtpObj.quit()
            QtGui.QMessageBox(QtGui.QMessageBox.Information, "Success!","Login successful! Your new email settings have been saved.",
                              QtGui.QMessageBox.Ok).exec_()
        except:
            QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Notifier failed to login to email.", "Could not log in\n\n"+traceback.format_exc(1),
                              QtGui.QMessageBox.Ok).exec_()
            #MPopUp.PopUp("Notifier failed to login to email.\n\n" + traceback.format_exc(1)).exec_()
            true_if_success = False
        return true_if_success

    def changeCredentials(self, host, email, pwd):
        self.host = str(host)
        self.email = str(email)
        self.pwd = str(pwd)

        host = str(host)
        email = str(email)
        pwd = str(pwd)

        web.persistentData.persistentDataAccess(email, 'Email', 'Address')
        web.persistentData.persistentDataAccess(pwd, 'Email', 'Password')
        web.persistentData.persistentDataAccess(host, 'Email', 'Host')

    def sendMail(self, To, From, Subject, Body):


        # Initialize TLS security.
        self.mail_sem.acquire()
        try:
            success = True
            self.smtpObj = smtplib.SMTP(self.host)
            self.smtpObj.ehlo()
            self.smtpObj.starttls()
            self.smtpObj.login(self.email, self.pwd)
        except:
            print("ERROR: Could not log in to email.")
            traceback.print_exc()
            success = False
        # Send the email.
        #print "Body:\n", Body
        email_text = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (From, ", ".join(To), Subject, Body)
        print ("Sending email with text:")
        print ("-------------------------------------------")
        print (email_text)
        print ("-------------------------------------------")

        try:
            self.smtpObj.sendmail(From, To, email_text)
            print("Successfully sent mail.")
        except:
            traceback.print_exc()
            print("ERROR: Could not send mail")
            success = False
        self.smtpObj.quit()
        self.mail_sem.release()
        return success
