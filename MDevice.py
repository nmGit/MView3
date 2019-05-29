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

from MFrame import MFrame
from PyQt4 import QtCore
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QSemaphore
import threading
from MDataBase.MDataBase import MDataBase
from MDataBase.MSQLiteDataBaseWrapper import MSQLiteDataBaseWrapper
from MWeb import web
import traceback
import time
import threading
import csv
import os
import sys


class MDevice(QThread):
    '''
  MView uses the MDevice class to give all sources of data a common 
  interface with which to interact in the context of MView. These 
  sources of data can be anything including but not limited to LabRad 
  servers, RS232 devices, GPIB Devices, they can even represent the 
  contents of .hdf5 files. Devices in MView are created by instantiating
  their device drivers. For example, if there are two RS232 devices, 
  we create two instances of the RS232 device driver. This means that 
  only one generic device driver needs to be created for one interface 
  (RS232, LabRad Servers, HDF5 files, etc.) and it can then be applied 
  to all devices that use the same interface.
  '''
    updateSignal = pyqtSignal()
    addParameterSignal = pyqtSignal(str)
    device_data_lock = QSemaphore(1)
    loading_data_lock = QSemaphore(1)
    lock = threading.Lock()


    begin_signal = pyqtSignal(name = "begin_signal")


    def __init__(self, name, *args, **kwargs):
        '''Initializes the device:

    1. Sets the frame title. 1.
    2. Sets the refresh rate. 2.

    Function arguments:

    :param name: The name of the device

   '''
        super(MDevice, self).__init__()
        self.lockLoggingSettings = kwargs.get("lock_logging_settings", False)
        self.defaultLogLocation = kwargs.get("default_log_location", None)
        self.dataType = kwargs.get("data_type", "float32")
        # Create a new MFrame
        web.devices.append(self)
        self.frame = MFrame()
        # print "Setting title to:", name, args
        self.frame.setTitle(name)
        self.name = name
        self.refreshRate = 1
        self.container = None
        self.datachest = None
        self.keepGoing = True
        self.log_enabled = False
        self.settingResultIndices = []
        self.notifier_mailing_lists = []
        self.doneLoading = False
        self.independent_data = {}
        self.dependent_data = {}


        #self.memory_tracker = tracker.SummaryTracker()
    def log(self, log):
        """ Tell the device whether to log data or not

        :param log: Boolean

    """
        self.log_enabled = log



    def isLogging(self):
        '''Getter for whether or not datalogging is enabled for this device.

      :rtype: boolean

   '''
        return self.log_enabled

    def setContainer(self, container):
        # traceback.print_stack()
        self.container = container
        self.frame.setContainer(container)

    def getContainer(self):
        return self.container

    def updateContainer(self):
        '''Refresh the devices container (Tile) on the GUI
      by emitting an update signal
   '''
        if self.container != None:
           # if self.container.readyToUpdate():
            self.updateSignal.emit()


    def addButton(self, *args):
        pass

    def setTitle(self, title):
        self.frame.setTitle(title)

    def query(self, *args):
        pass

    def setYLabel(self, *args):
        pass

    def setRefreshRate(self, *args):
        pass

    def setPlotRefreshRate(self, *args):
        pass

    def addButtonToGui(self, button):
        self.frame.appendButton(button)

    def addReadout(self, name, units):
        self.nicknames.append(name)
        self.units.append(units)
    def setData(self, key, indep, dep):
        if (key not in self.independent_data.keys()):
            self.device_data_lock.acquire()

            self.independent_data[key] = []
            self.dependent_data[key] = []
            self.device_data_lock.release()

        if (type(indep) is list and type(dep) is list):

            indep_copy = [x for x in indep]
            dep_copy = [x for x in dep]
            indep_copy_len = len(indep_copy)
            dep_copy_len = len(dep_copy)
            if (dep_copy_len == indep_copy_len):

                # Ok to add
                self.device_data_lock.acquire()

                self.independent_data[key]= indep_copy
                self.dependent_data[key] = dep_copy
                self.device_data_lock.release()

            else:
                traceback.print_exc()
                self.location = os.path.dirname(traceback.extract_stack()[0][0])

                with open(self.location+'\\misaligned.csv', 'wb') as csvfile:
                    filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    maxrows = max(len(indep_copy), len(dep_copy))
                    # the extra row will display error

                    indep_copy.append("ERROR!")
                    dep_copy.append("ERROR!")
                    for row in range(maxrows):
                        filewriter.writerow([indep_copy[row], dep_copy[row]])
                raise ValueError("Independent data and dependent data must be the same length, independent length: %d,"
                                 " dependent length, %d. saved error csv in %s"  %(indep_copy_len, dep_copy_len, self.location))

        elif (type(dep) != list):
            print "Error dependent is not a list:",dep
            traceback.print_exc()
            raise ValueError("Independent data and dependent data must be lists")
    def addData(self, key, indep, dep):
        #self.device_data_lock.acquire()
        if (key not in self.independent_data.keys()):
            self.independent_data[key] = []
            self.dependent_data[key] = []
        if(type(indep) is list):
            indep_copy = [x for x in indep]
            if(type(dep) is list and len(dep) == len(indep_copy)):
                dep_copy = [x for x in dep]
                # Ok to add
                self.device_data_lock.acquire()
                self.independent_data[key].extend(indep_copy)
                self.dependent_data[key].extend(dep_copy)
                self.device_data_lock.release()

            else:
                raise ValueError("Independent data and dependent data must be the same length")
        elif(type(dep) != list):

            self.device_data_lock.acquire()
            self.independent_data[key].append(indep)
            self.dependent_data[key].append(dep)
            self.device_data_lock.release()
        else:
            raise ValueError("Independent data and dependent data must be the same length")
        #print self, "size of independent is", sys.getsizeof(self.independent_data), "sizeof dependent is", sys.getsizeof(self.dependent_data)
    def getData(self, key):
        self.device_data_lock.acquire()
        # Create a copy of the data. Otherwise lists are passed as pointers.
        indep = self.independent_data[key]
        dep = self.dependent_data[key]
        data = [[x for x in indep], [x for x in dep]]
        self.device_data_lock.release()
        return data

    def addPlot(self, length=None, *args):

        if(self.isLogging()):
            self.frame.addPlot(length)
            # Datalogging must be enabled if we want to plot data.

            return self.frame.getPlot()
        else:
            raise Exception("Cannot add plot before enabling data logging.")
            return None
    def getFrame(self):
        """Return the device's frame."""
        return self.frame

    def stop(self):
        # print "stopping device thread..."
        self.keepGoing = False
        # print "device thread stopped."
        #self.device_stop_signal.emit()
        self.save_logging_state()
        if self.frame.DataLoggingInfo()['chest']:
            self.frame.DataLoggingInfo()['chest'].stop()
        self.close()

    def __threadSafeClose(self):
        if self.frame.DataLoggingInfo()['chest']:
            self.frame.DataLoggingInfo()['chest'].stop()

    def plot(self, plot):
        self.frame.setHasPlot(plot)

    def begin(self, **kwargs):
        '''Start the device. 
   '''
        # Automatically refresh node data in callQuery
        self.refreshNodeDataInCallQuery = kwargs.get('auto_refresh_node', True)
        #if self.datachest:
        #    self.independent_data = self.datachest.query(str(self), ["capture_time"], "all")
        #print "independent_data:", self.independent_data
        self.restore_logging_state()
        #print "Data logging info for", str(self), ":", self.frame.DataLoggingInfo()



        self.frame.masterEnableDataLogging(self.log)

        self.onBegin()
        # self.frame.setReadingIndex(self.settingResultIndices)
        #self.configureDataLogging()
        # Each device NEEDS to run on a different thread
        # than the main thread (which ALWAYS runs the GUI).
        # This thread is responsible for querying the devices.
#        self.deviceThread = threading.Thread(target=self.callQuery, args=[])
#        # If the main thread stops, stop the child thread.
#        self.deviceThread.daemon = True
#        # Start the thread.

        self.start()
        #self.callQuery()

    def configureDataLogging(self):
        self.loading_data_lock.acquire()
        self.frame.DataLoggingInfo()[
            'lock_logging_settings'] = self.lockLoggingSettings
        if self.defaultLogLocation != None:
            # If the current directory is a subdirectory of the default,
            # then that is ok and the current directory should not be
            # changed.
            self.frame.DataLoggingInfo()['location'] = self.defaultLogLocation
           # print "current location:", self.frame.DataLoggingInfo()['location']
            #print "default:", self.defaultLogLocation


        location = self.frame.DataLoggingInfo()['location']
        filename = self.frame.DataLoggingInfo()['name']
        if location == None or filename == None:
            self.log(False)
            print self, "Could not initialize logging"
            self.loading_data_lock.release()

            return
        if(self.datachest):
            self.datachest.stop()
            del self.datachest
        print "Configuring logging for", self, "at", location+'\\'+filename
        self.datachest = MSQLiteDataBaseWrapper(location+'\\'+filename)
        self.datachest.db_done_loading.connect(self.__read_all_data_from_file)

        self.frame.DataLoggingInfo()['chest'] = self.datachest

    def __read_all_data_from_file(self):
        #print "reading all data from file"
       # print "before:", self.independent_data, self.dependent_data
        indep = self.datachest.submit_query(str(self), ["capture_time"], "all")
        for param in self.getParameters().keys():
            dep = self.datachest.submit_query(str(self), [param], "all")
            if(indep != None and dep != None):
                self.setData(param, indep, dep)

        self.loading_data_lock.release()
            #print param, "data size2:", len(self.independent_data[param]), len(self.dependent_data[param])
        #print "after:", self.independent_data, self.dependent_data


    def onBegin(self):
        '''Called at the end of MDevice.begin(). This is called before 
        MView starts. This allows us to configure settings that 
        MView might use while starting. This might include datalog 
        locations or device-specific information.'''
        pass

    def loaded(self):

        print self, "loaded."
        self.onLoad()
        self.doneLoading = True

    def isLoaded(self):
        return self.doneLoading

    def onLoad(self):
        '''Called at the end of MGui.startGui(), when the main 
        MView GUI has finished loading. This allows the 
        MDevice to configure pieces of MView only available
        once the program has fully loaded.'''
        pass

    def onAddParameter(self, *args, **kwargs):
        '''Called when when a new parameter is added. 
    It is passed whatever MDevice.addParameter() is passed. 
    (Note: MDevice.onAddParameter() and MDevice.addParameter() 
    are different). This function must return a tuple in 
    the form ((str) Parameter Name, (int)Precision, (str) units)
   '''
        return

    def setPrecisions(self, precisions):
        self.frame.setPrecisions(precisions)

    def setSigFigs(self, parameter, sigfigs):
        self.frame.setSigFigs(parameter, sigfigs)

    def _setReadings(self, readings, update=True):
        '''Tell the frame what the readings are so that they can be logged.

        :param readings: Type: list

       '''
        pass
        # readings = self.frame.getReadings()
        # print "set readings called"
        # traceback.print_stack()
        # if readings != None:
        # node = self.frame.getNode()
        # anchorData = []
        # # # print "HERE A"
        # if node is not None:

        # for input in node.getAnchors():
        # if input.getType() == 'input':
        # print "INPUT ANCHOR", input
        # data = input.getData()
        # if data != None and type(data) is list:
        # anchorData.append(data[-1])
        # elif data != None:
        # anchorData.append(None)
        # print "readigns:", readings
        # print "anchordata:", anchorData
        # readings.extend(anchorData)
        # print "comb readigns:", readings

        # else:
    def isOutOfRange(self, key):
        return self.frame.getOutOfRangeStatus(key)

    def setOutOfRange(self, key):
        # print self, key, "is out of range"
        self.frame.setOutOfRange(key)

    def setInRange(self, key):
        self.frame.setInRange(key)

    def disableRange(self):
        self.frame.disableRange()

    def setReading(self, parameter, reading):
        if reading != None:
            self.frame.setReading(parameter, reading)

    def setMailingLists(self, lists):
        self.notifier_mailing_lists = lists

    def getMailingLists(self):
        return self.notifier_mailing_lists;

    def getUnit(self, parameter):
        return self.frame.getUnit(parameter)

    def setUnit(self, parameter, unit):
        self.frame.setUnit(parameter, unit)

    def setPrecision(self, parameter, precision):
        self.frame.setPrecision(parameter, precision)

    def getPrecision(self, parameter):
        return self.frame.getPrecision(parameter)

    def getSigFigs(self, parameter):
        return self.frame.getSigFigs(parameter)

    def getReading(self, parameter):
        return self.frame.getReading(parameter)

    def setReadingIndex(self, parameter, index):
        self.frame.setReadingIndex(parameter, index)

    def getReadingIndex(self, parameter):
        return self.frame.getReadingIndex(parameter)

    def setCommand(self, parameter, command):
        # print "Setting command for", parameter, "is", command
        self.frame.setCommand(parameter, command)

    def getCommand(self, parameter):
        # print "Getting Parameter:",self.frame.getCommand(parameter)
        return self.frame.getCommand(parameter)

    def getParameters(self):
        return self.frame.getParameters()

    def getNicknames(self):
        return self.frame.getNicknames()

    def setParamVisibility(self, parameter, visible):
        self.frame.setParamVisibility(parameter, True)

    def getParamVisibility(self, paramteter):
        return self.frame.getParamVisibility(parameter)

    def getReadingIndex(self, parameter):
        return self.frame.getReadingIndex(parameter)

    def enableDataLogging(self, parameter):
        self.frame.DataLoggingInfo()['channels'][parameter] = True

    def disableDataLogging(self, parameter):
        self.frame.DataLoggingInfo()['channels'][parameter] = False

    def isDataLoggingEnabled(self, parameter):
        return self.frame.DataLoggingInfo()['channels'][parameter]

    def getParameterType(self, parameter):
        if type(parameter) is dict:
            parameter = parameter.keys()[0]
        return self.frame.getNode().getAnchorByName(parameter).getType()

    def disableAllDataLogging(self):
        self.frame.masterEnableDataLogging(False)
        for p in self.getParameters():
            self.disableDataLogging(p)

    def enableAllDataLogging(self):
        self.frame.masterEnableDataLogging(True)

    def run(self):
        '''Automatically called periodically, 
        determined by MDevice.Mframe.getRefreshRate(). 
        There is also a MDevice.Mframe.setRefreshRate()
        function with which the refresh rate can be configured.
        '''
        #self.currentThread().setPriority(QtCore.QThread.IdlePriority)
        if self.log_enabled == False:
            for p in self.getParameters():
                self.disableDataLogging(p)
        else:
            if (self.frame.getDataChestWrapper() == None):
                self.configureDataLogging()
                self.loading_data_lock.acquire()
                self.loading_data_lock.release()
        while True:
            #t1 = time.time()
            self.query()
            node = self.frame.getNode()
            tm = time.time()
            for param in self.getParameters():
                if param not in self.dependent_data.keys():

                    self.setData(param, [], [])

                reading = self.getReading(param)
                self.addData(param, tm, reading)

            if node is not None and self.refreshNodeDataInCallQuery:
                self.frame.getNode().refreshData()
            if self.datachest is not None and self.doneLoading:
                try:

                    if self.frame.isDataLogging():

                        #print "MDevice:", str(self),"thread id:",int(QThread.currentThreadId())
                        columns = ["capture_time"]
                        rows = [tm]
                        for param in self.getParameters().keys():
                            if(self.isDataLoggingEnabled(param)):
                                columns.append(param)
                                columns.append("unit_"+param)
                                rows.append(self.getReading(param))
                                rows.append(self.getUnit(param))
                        if(self.datachest.isRunning()):
                            self.datachest.insert(str(self), columns, rows)

                except:
                    traceback.print_exc()

            if web.gui != None and web.gui.MAlert != None:
                web.gui.MAlert.monitorReadings(self)
           # print "Requesting container update from", threading.currentThread()
            self.updateContainer()
            #
            #
            # t1_plot = time.time()
            # if self.getFrame().isPlot() and self.getFrame().getPlot() != None:
            #         #self.device.getFrame().getDataSet() != None and\
            #
            #     # print "device container: device:", self.device
            #
            #     plot = self.getFrame().getPlot()
            #     curves = self.getFrame().getPlot().get_curves()
            #     t1_setdata = time.time()
            #     for y, key in enumerate(self.getParameters()):
            #        # self.device.set_data(self.device.get_independent_data()[key], self.device.get_dependent_data()[key])
            #
            #         if(key in curves):
            #             data = self.getData(key)
            #             #print "data size:", len(data[0]), len(data[1])
            #
            #             curves[key].set_data(*data)
            #
            #         else:
            #             plot.add_curve(key)
            #     t2_plot = time.time()
            #
            #     print "time to plot:", t2_plot - t1_plot, "from", threading.currentThread()
            #



            #t2 = time.time()
            #print self, "time to run:", t2 - t1
            if self.keepGoing:
                self.msleep(int(self.frame.getRefreshRate()*1000))
            else:
                return

                #threading.Timer(self.frame.getRefreshRate(),
                 #               self.callQuery).start()

    def prompt(self, button):
        '''Called when 
    a device's button is pushed. Button is an array which 
    is associated with the button. The array is constructed 
    in the device driver code, and the PyQT button is then appended
    to the end by MView. The array associated with the button is passed 
    to prompt() in the device driver. The device driver then determines 
    what to do based on the button pushed. 
   '''
        pass

    def close(self):
        return

    def addParameter(self, *args, **kwargs):
        """Adds a parameter to the GUI. The first argument is the name,
        the other arguments are specific to the device driver.
        """
        try:
            name = args[0]
        except:
            raise AttributError(
                "The first argument of addParameter() must be a name")

        show = kwargs.get("show", True)
        units = kwargs.get('units', None)
        sigfigs = kwargs.get('significant_figures', None)
        precision = kwargs.get('precision', None)
        if sigfigs is None and precision is None:
            precision = 2
        index = kwargs.get('index', None)
        log = kwargs.get("log", self.isLogging())
        self.frame.addParameter((name, units, precision))
        self.setReadingIndex(name, index)
        self.setPrecision(name, precision)
        self.setSigFigs(name, sigfigs)
        self.setUnit(name, units)

        self.setData(name, [],[])

        self.onAddParameter(*args, **kwargs)
        self.frame.setParamVisibility(name, show)
        self.frame.DataLoggingInfo()['channels'][name] = log


        self.addParameterSignal.emit(name)
    def save_logging_state(self):

        dataname = self.getFrame().DataLoggingInfo()['name']
        channels = self.getFrame().DataLoggingInfo()['channels']

        location = self.getFrame().DataLoggingInfo()['location']
        #print "saving logging state:", self.getFrame().DataLoggingInfo()
        web.persistentData.persistentDataAccess(dataname, 'DataLoggingInfo', str(self), 'name')
        web.persistentData.persistentDataAccess(channels, 'DataLoggingInfo', str(self), 'channels')
        web.persistentData.persistentDataAccess(location, 'DataLoggingInfo', str(self), 'location')

    def restore_logging_state(self):

        dataname = web.persistentData.persistentDataAccess(None, 'DataLoggingInfo', str(self), 'name')
        channels = web.persistentData.persistentDataAccess(None, 'DataLoggingInfo', str(self),
                                                           'channels')
        location = web.persistentData.persistentDataAccess(None, 'DataLoggingInfo', str(self),
                                                           'location')
        # Do a sanity check
        # print "device:", self.device
        #print "restoring location of", self, location
        for nickname in self.getFrame().getNicknames():
            if channels == None or nickname not in channels.keys():
                channels = self.getFrame().DataLoggingInfo()['channels']
                print "Error when retreiving logged channels in config file, restoring to", channels
        if dataname is None:
            dataname = self.getFrame().getTitle()

        self.getFrame().DataLoggingInfo()['name'] = dataname
        if channels != None:
            self.getFrame().DataLoggingInfo()['channels'] = channels
        self.getFrame().DataLoggingInfo()['location'] = location
        pass
    # def logData(self, b):
    #     """Enable or disable datalogging for the device."""
    #     # if channels!= None:
    #     #    self.frame.DataLoggingInfo['channels'] = channels
    #     self.frame.enableDataLogging(b)

    def __str__(self):
        if self.frame.getTitle() is None:
            return "Unnamed Device"
        return self.frame.getTitle()
