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

class MMail:
    """Very simple email client."""

    def __init__(self):

        self.smtpObj = smtplib.SMTP('smtp.googlemail.com')
        # Say hello to the email server.
        self.smtpObj.ehlo()
        # Initialize TLS security.
        self.smtpObj.starttls()
        try:
            self.smtpObj.login('physics.labrad@gmail.com', 'mcdermott')
        except:
            MPopUp.PopUp("Notifier failed to login to email.\n\n" + traceback.format_exc(1)).exec_()
            traceback.print_exc()
        self.smtpObj.quit();
        # Send the email.

    def sendMail(self, To, From, Subject, Body):
        success = True
        self.smtpObj = smtplib.SMTP("smtp.gmail.com", 587)

        self.smtpObj.ehlo()
        # Initialize TLS security.
        self.smtpObj.starttls()
        try:
            self.smtpObj.login('physics.labrad@gmail.com', 'mcdermott')
        except:
            print("ERROR: Could not log in to email.")
            MPopUp.PopUp("Notifier failed to login to email.\n\n" + traceback.format_exc(1)).exec_()
            traceback.print_exc()
            success = False
        # Send the email.
        msg = MIMEText(Body)
        msg['Subject'] = Subject
        msg['From'] = From
        msg['To'] = To
        try:
            self.smtpObj.sendmail('physics.labrad@gmail.com', To,
                            Body)
            print("Successfully sent mail.")
        except:
            traceback.print_exc()
            print("ERROR: Could not send mail")
            success = False
        self.smtpObj.quit()
        return success
