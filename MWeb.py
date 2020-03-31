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
__version__ = "1.0.1"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"


import sys

sys.dont_write_bytecode = True
#189, 195, 199

class web:
    """
    Organizes global variables. Allows all other classes to easily
    access important parameters central to mView. Stores and opens all
    data.
    """
    # Store minimum and maximum values for all readings. MAlert uses
    # this to check if readings are still in bounds.

    limitDict = {}
    # All devices.
    devices = []
    # The default refresh GUI rate.
    guiRefreshRate = 1
    # Holds reference to the telecomm server.
    telecomm = None
    # DPI scaling ratio.
    ratio = 1
    scrnHeight = None
    scrnWidth = None
    # List of virtual devices
    virtualDevices = []
    gui = None
    title = None
    nodeFilenames = []
    nodes = []
    persistentData = None

    notifier_email_address = None
    notifier_email_pwd = None
    alert_data = None

    malert = None

    color_scheme = {"dark": {"black":(0,0,0),
                            "1st background" : (189, 195, 199),
                             "2nd background" : (89, 95, 99),
                             "3rd background":(52, 73, 94),
                             "4th background": (52, 94,73)}
    }