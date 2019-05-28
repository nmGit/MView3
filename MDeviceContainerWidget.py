from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignal, QSemaphore
from MWeb import web
from MGrapher.MGrapher3 import MGrapher
from MReadout import MReadout
import math
from functools import partial
import traceback
from pprint import pprint
import numpy as np
import time
import threading
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QSemaphore, SIGNAL

class MDeviceContainerWidget(QtGui.QFrame):
    done_updating_semaphore = QSemaphore(1)
    def __init__(self, device, parent=None):
        QtGui.QWidget.__init__(self, parent)
        device.updateSignal.connect(self.update)
        device.addParameterSignal.connect(self.addParameter)

        device.setContainer(self)

        #self.nicknameLabels = []
        #self.unitLabels = []
        self.lcds = []
        self.params = {}
        self.device = device
        self.dc = None

        grid = QtGui.QGridLayout()
        self.grid = grid
        self.setLayout(grid)

        self.frameSizePolicy = QtGui.QSizePolicy()
        self.frameSizePolicy.setVerticalPolicy(4)
        self.frameSizePolicy.setHorizontalPolicy(QtGui.QSizePolicy.Preferred)
        self.setSizePolicy(self.frameSizePolicy)
        self.setStyleSheet("background: rgb(52, 73, 94)")
        self.setFrameShape(QtGui.QFrame.Panel)
        self.setFrameShadow(QtGui.QFrame.Plain)
        self.setLineWidth(web.ratio)
        grid.setSpacing(10)
        grid.setColumnStretch(0, 1)

        self.font = QtGui.QFont()
        self.font.setBold(False)
        self.font.setWeight(50)
        self.font.setKerning(True)
        self.font.setPointSize(12)

        self.fontBig = QtGui.QFont()
        self.fontBig.setBold(False)
        self.fontBig.setWeight(50)
        self.fontBig.setKerning(True)
        self.fontBig.setPointSize(18)

        self.isRed = {}
        titleWidget = QtGui.QLabel(device.getFrame().getTitle())
        titleWidget.setFont(self.fontBig)
        titleWidget.setStyleSheet("color:rgb(189, 195, 199);")
        grid.addWidget(titleWidget, 0, 0)

        buttonLayout = QtGui.QHBoxLayout()
        buttons = device.getFrame().getButtons()

        self.hidden = False
        self.plot_updater = MPlotUpdater(self.device)
        self.plot_updater.update_curve_sig.connect(self.__update_curves)
        for button in buttons:
            if button != []:

                button.append(QtGui.QPushButton(button[0], self))
                button[-1].setStyleSheet("color:rgb(189, 195, 199); "
                                         "background:rgb(70, 80, 88)")
                button[-1].setFont(self.font)
                buttonLayout.addWidget(button[-1])
                button[-1].clicked.connect(partial(device.prompt, button))

        grid.addLayout(buttonLayout, 0, 1, 1, 2)

        self.nicknames = device.getFrame().getParamKeyOrder()
        for i, nickname in enumerate(self.nicknames):
            if nickname != None:
                self.params[nickname] = {}
                y = i + 1
                label = QtGui.QLabel(nickname, self)
                label.setFont(self.font)
                label.setWordWrap(True)
                label.setStyleSheet("color:rgb(189, 195, 199);")
                grid.addWidget(label, y, 0)
                # self.nicknameLabels.append(label)
                self.params[nickname]["nickname_label"] = label

                units = QtGui.QLabel('')
                grid.addWidget(units, y, 2)
                units.setFont(self.fontBig)
                units.setStyleSheet("color:rgb(189, 195, 199);")

                self.params[nickname]["unit_label"] = units

                #lcd = QtGui.QLCDNumber(self)
                lcd = MReadout(self)
                self.lcds.append(lcd)
                self.params[nickname]["lcd_readout"] = lcd
                lcd.getLCD().setNumDigits(11)
                lcd.getLCD().setSegmentStyle(QtGui.QLCDNumber.Flat)
                lcd.getLCD().display("-")
                lcd.getLCD().setFrameShape(QtGui.QFrame.Panel)
                lcd.getLCD().setFrameShadow(QtGui.QFrame.Plain)
                lcd.getLCD().setLineWidth(web.ratio)
                lcd.getLCD().setMidLineWidth(100)
                lcd.setStyle("color:rgb(189, 195, 199);\n")
                lcd.getLCD().setFixedHeight(web.scrnHeight / 30)
                lcd.getLCD().setMinimumWidth(web.scrnWidth / 7)
                lcd.setLabelSize(20)
                lcdHBox = QtGui.QHBoxLayout()
                lcdHBox.addStretch(0)
                lcdHBox.addWidget(lcd)

                grid.addLayout(lcdHBox, y, 1)
        self.topHBox = QtGui.QHBoxLayout()
        yPos = len(self.nicknames)
        grid.addLayout(self.topHBox, yPos + 1, 0, yPos + 1, 3)
        if device.getFrame().isPlot():
            self.dc = MGrapher()
            yPos = len(self.nicknames) + 2
            device.getFrame().setPlot(self.dc)
            grid.addWidget(self.dc, yPos, 0, yPos, 3)

        self.bottomHBox = QtGui.QHBoxLayout()

        grid.addLayout(self.bottomHBox, yPos + 2, 0, yPos + 2, 3)

    def getBottomHBox(self):
        return self.bottomHBox

    def getTopHBox(self):
        return self.topHBox

    def addParameter(self, param):
        param = str(param) # will be passed in as a QString, but we need it to be just a normal string
       # traceback.print_stack()
        label = QtGui.QLabel(param, self)
        lcd = MReadout(self)
        units = QtGui.QLabel('')
        self.params[param] = {}
        if not self.device.getFrame().isParamVisible(param):
            lcd.hide()
            label.hide()
            units.hide()
        label.setFont(self.font)
        label.setWordWrap(True)
        label.setStyleSheet("color:rgb(189, 195, 199);")
        self.grid.addWidget(label, self.grid.rowCount(), 0)
        self.params[param]["nickname_label"] = label

        self.grid.addWidget(units, self.grid.rowCount() - 1, 3)

        units.setFont(self.fontBig)
        units.setStyleSheet("color:rgb(189, 195, 199);")
        self.params[param]["unit_label"] = units

        self.params[param]["lcd_readout"] = lcd
        self.lcds.append(lcd)
        lcd.getLCD().setNumDigits(11)
        lcd.getLCD().setSegmentStyle(QtGui.QLCDNumber.Flat)
        lcd.getLCD().display("-")
        lcd.getLCD().setFrameShape(QtGui.QFrame.Panel)
        lcd.getLCD().setFrameShadow(QtGui.QFrame.Plain)
        lcd.getLCD().setLineWidth(web.ratio)
        lcd.getLCD().setMidLineWidth(100)
        lcd.getLCD().setStyleSheet("color:rgb(189, 195, 199);\n")
        lcd.getLCD().setFixedHeight(web.scrnHeight / 30)
        lcd.getLCD().setMinimumWidth(web.scrnWidth / 7)
        lcdHBox = QtGui.QHBoxLayout()
        lcdHBox.addStretch(0)
        lcdHBox.addWidget(lcd)

        self.grid.addLayout(lcdHBox, self.grid.rowCount() - 1, 1)

        if self.dc != None:
            self.grid.removeWidget(self.dc)
            self.grid.addWidget(self.dc, self.grid.rowCount(), 0, 1, 3)

    def visible(self, show=None):
        if self.hidden:
            self.show()
            self.hidden = False
            # print "showing"
        else:
            self.hide()
            self.hidden = True
            # print "hidden"
    # def allow_update(self):
    #     # Only call update if there is no update currently in progress. This prevents signals from building up
    #     # in the queue and crashing the program
    #     if self.done_updating_semaphore.available() != 0:
    #         print "updating container..."
    #         self.__update()
    #     else:
    #         print "update requests coming in too fast!!"
    def readyToUpdate(self):
        return self.done_updating_semaphore.available() > 0
    def __update_curves(self, device):

        if self.device.getFrame().isPlot() and self.device.getFrame().getPlot() != None:
            # self.device.getFrame().getDataSet() != None and\

            # print "device container: device:", self.device

            plot = self.device.getFrame().getPlot()
            curves = self.device.getFrame().getPlot().get_curves()
            t1_setdata = time.time()
            for y, key in enumerate(self.device.getParameters()):
                # self.device.set_data(self.device.get_independent_data()[key], self.device.get_dependent_data()[key])


                if (key in curves):
                    data = self.device.getData(key)
                    # print "data size:", len(data[0]), len(data[1])
                    pen = curves[key].getPen()
                    if (not self.device.isDataLoggingEnabled(key)):
                        pen.setStyle(QtCore.Qt.DotLine)
                    else:
                        pen.setStyle(QtCore.Qt.SolidLine)
                    curves[key].setPen(pen)
                    # print "setting data",key, data
                    # print "--------------"
                    curves[key].set_data(*data)

                else:
                    plot.add_curve(key)
            t2_plot = time.time()
            # print "Time to plot:", t2_plot - t1_plot, "from", threading.currentThread()

    def update(self):
        #QThread.currentThread().setPriority(QtCore.QThread.LowestPriority)
        #self.done_updating_semaphore.acquire()
        #print "updating container from",threading.currentThread()
        if( not isinstance(threading.current_thread(), threading._MainThread)):
            print "ERROR"
            traceback.print_exc()
            raise RuntimeError("Cannot update device container from outside the main thread")
        # It is possible for update signals to be sent more often than update can run.
        # The semaphore allows update to essentially skip an update if updates are being requested too frequently.

        t1 = time.time()
        # print "updating container of", self.device
        frame = self.device.getFrame()

        # print "updating data 1",self.device.getFrame().getTitle()

        # print "updating data 2",self.device.getFrame().getTitle()
        if self.device.getFrame().getPlot() == None and\
                self.device.getFrame().isPlot():
            self.dc = MGrapher.mGraph(self.device)
            yPos = len(self.nicknames) + 2
            self.device.getFrame().setPlot(self.dc)
            self.grid.addWidget(self.dc, yPos, 0, yPos, 3)

        if not frame.isError():

            nicknames = self.device.getNicknames()
            parameters = self.device.getParameters()
#            while len(nicknames) > len(self.lcds):
#                # print "device:", self.device
##                # print "readings:", readings
 #               # print "len(self.lcds:)", len(self.lcds)
 #               # print "nicknames:", self.device.getFrame().nicknames
 #               difference = len(nicknames) - len(self.lcds)
 ##               # print "difference:", difference
  #              self.addParameter(
  #                  nicknames[-difference])

            # print "nicknames:", self.device.getFrame().nicknames

            self.plot_updater.updatePlot()

            for y, key in enumerate(self.device.getFrame().getParameters().keys()):
                param = self.device.getFrame().getParameter(key)
                # pprint(param)
                # print "setting yellow"
                #self.lcds[y].setStyleSheet("color:rgb(189, 100, 5);\n")
                if (self.device.getFrame().isParamVisible(key)):
                    # print self.device.isOutOfRange(key)

                    if self.device.isOutOfRange(key) and not self.isRed.get(key, False):
                        # print "turning it red", self.device, key
                        self.params[key]["lcd_readout"].setStyle(
                            "color:rgb(210, 100, 10);\n")
                        self.params[key]["nickname_label"].setStyleSheet(
                            "color:rgb(210, 100, 10);\n")
                        self.params[key]["unit_label"].setStyleSheet(
                            "color:rgb(210, 100, 10);\n")
                        self.isRed[key] = True
                    elif self.isRed.get(key, False) and not self.device.isOutOfRange(key):
                        # print "turning it white"
                        self.params[key]["lcd_readout"].setStyle(
                            "color:rgb(189, 195, 199);")
                        self.params[key]["nickname_label"].setStyleSheet(
                            "color:rgb(189, 195, 199);")
                        self.params[key]["unit_label"].setStyleSheet(
                            "color:rgb(189, 195, 199);")
                        self.isRed[key] = False
                    try:
                        precision = self.device.getPrecision(key)
                        sigfigs = self.device.getSigFigs(key)
                        # print self.device, key, "precision:", precision

                        # print "precision:", precision
                        if precision is not None:
                            format = "{0:." + str(int(precision)) + "f}"
                        elif sigfigs is not None:
                            format = "{0:." + str(int(sigfigs)) + "g}"
                        else:
                            format = "{0.0f}"
                        try:
                            param['reading'] = float(param['reading'])
                        except:
                            pass
                        # Only try to format the readout if it is a floating point number
                        if type(param['reading']) is float or \
                           type(param['reading']) is np.float64:

                            if not math.isnan(param['reading']):
                                self.params[key]["lcd_readout"].display(
                                    float(format.format(param['reading'])))

                            else:
                                self.params[key]["lcd_readout"].display("---")

                        else:
                            # print "not a float", type(param['reading'])
                            self.params[key]["lcd_readout"].display(
                                param['reading'])

                    except:
                        traceback.print_exc()

                    unit = frame.getUnit(key)
                    # print "DEVICE CONTAINER WIDGET:", unit
                    if unit != None:
                        self.params[key]["unit_label"].setText(str(unit))
                else:
                    self.params[key]["lcd_readout"].hide()
                    self.params[key]["nickname_label"].hide()
                    self.params[key]["unit_label"].hide()
        #t_plot = t2_plot - t1_plot

        t2 = time.time()
        t_total = float(t2 - t1)
        #print "time to update container:", t_total
       # print "time to update container %.8f, %.8f of the total time was spent plotting" % (t_total, (float(t_plot)/t_total) *100)
        #self.done_updating_semaphore.release()

class MPlotUpdater(QThread):
    perform_update_sem = QSemaphore()
    update_curve_sig = pyqtSignal(str)
    def __init__(self, device):
        super(MPlotUpdater, self).__init__()

        self.device = device
        self.setObjectName("PlotUpdater:"+str(device))
        self.start()
    def updatePlot(self):
        curves = self.device.getFrame().getPlot().get_curves()
        for y, key in enumerate(self.device.getParameters()):
            # self.device.set_data(self.device.get_independent_data()[key], self.device.get_dependent_data()[key])
            if (key not in curves):
                plot = self.device.getFrame().getPlot()
                plot.add_curve(key)

        self.perform_update_sem.release()

    def run(self):
        #self.setPriority(QThread.LowestPriority)
        while(True):
            #print "Plot updater for", self.device, " running as:", threading.currentThread()

            self.perform_update_sem.acquire()
            try:
                plot_delay = int(web.persistentData.persistentDataAccess(None, 'deviceRefreshRates', str(self.device), 'plot', default = 1)*1000)
                self.msleep(plot_delay)
            except:
                traceback.print_exc()
            t1_plot = time.time()

            self.update_curve_sig.emit(str(self.device))



