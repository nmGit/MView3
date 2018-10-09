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
from logilab.common.registry import traced_selection

__author__ = "Noah Meltzer"
__copyright__ = "Copyright 2016, McDermott Group"
__license__ = "GPL"
__version__ = "2.0.2"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"

import numpy as np

import sys
import traceback
from PyQt4 import QtGui, QtCore
from functools import partial
import pyqtgraph as pg
import numpy as np
import time as tm
from dateStamp import *
from dataChest import *
from MCheckableComboBoxes import MCheckableComboBox
from datetime import datetime
import warnings


class mGraph(QtGui.QWidget):
    def __init__(self, device, parent=None, **kwargs):
        QtGui.QWidget.__init__(self, parent)
        self.title = kwargs.get("title", device.getFrame().getTitle())
        # This is the device we want to use.
        self.device = device
        # This sets up axis on which to plot.
        self.hidden = False
        data = None
        self.viewboxes = []
        self.lastValidTime = 60

        pg.setConfigOption('background', (189, 195, 199))
        pg.setConfigOption('foreground', (0, 0, 0))

        self.frame = QtGui.QFrame(self)
        frameLayout = QtGui.QVBoxLayout(self.frame)
        self.frame.setFrameShape(QtGui.QFrame.Panel)
        self.frame.setFrameShadow(QtGui.QFrame.Plain)
        self.frame.setStyleSheet(".QFrame{background-color: rgb(70,80,88); "
                                 "margin:0px; border:2px solid rgb(0, 0, 0);}")
        self.win = pg.GraphicsWindow()

        frameLayout.addWidget(self.win)

        self.v2 = pg.ViewBox()
       # self.p = pg.PlotItem(title=self.title, axisItems={
       #                           'bottom': TimeAxisItem(orientation='bottom')})

        self.v2.setMouseMode(self.v2.RectMode)

        self.p = self.win.addPlot(title=self.title, axisItems={
                                  'bottom': TimeAxisItem(orientation='bottom')}, viewBox = self.v2)

        self.p.addLegend()
        self.p.showGrid(x=True, y=True, alpha=0.5)

        self.p.sigRangeChanged.connect(self.rangeChanged)
        self.processRangeChangeSig = False

        pen = pg.mkPen(cosmetic=True, width=2, color=(
            np.random.random() * 255, np.random.random() * 255, np.random.random() * 255))
        self.textPen = QtGui.QPen()

        #self.curve1 = self.p1.plot([0], pen = pen)
        self.curves = []

        self.setStyleSheet("QPushButton{\
                    color:rgb(189,195, 199); \
                    background:rgb(70, 80, 88)};\
                    ")
        #frame.setStyleSheet(".QPushButton{color:rgb(52, 73, 94)}")

        self.hideButton = QtGui.QPushButton("Hide Plot")
        self.hideButton.clicked.connect(self.togglePlot)
        self.oneMinButton = QtGui.QPushButton("1 min")
        self.oneMinButton.clicked.connect(
            partial(self.plot, start=60, autoRange=True))
        self.tenMinButton = QtGui.QPushButton("10 min")
        self.tenMinButton.clicked.connect(
            partial(self.plot,  start=600, autoRange=True))
        self.twoHrButton = QtGui.QPushButton("2 hr")
        self.twoHrButton.clicked.connect(
            partial(self.plot, start=7200, autoRange=True))
        self.twelveHrButton = QtGui.QPushButton("12 hr")
        self.twelveHrButton.clicked.connect(
            partial(self.plot,  start=43200, autoRange=True))
        self.threeDayButton = QtGui.QPushButton("3 day")
        self.threeDayButton.clicked.connect(
            partial(self.plot, start=259200, autoRange=True))
        self.oneWkButton = QtGui.QPushButton("1 week")
        self.oneWkButton.clicked.connect(
            partial(self.plot,  start=604800, autoRange=True))
        self.allButton = QtGui.QPushButton("All Time")
        self.allButton.clicked.connect(
            partial(self.plot, start=None, autoRange=True))
        self.lineSelect = MCheckableComboBox()
        self.lineSelect.setSizeAdjustPolicy(0)

        self.autoscaleCheckBox = QtGui.QCheckBox("Auto Ranging")
        self.autoscaleCheckBox.setChecked(True)
        self.autoscaleCheckBox.clicked.connect(self.plot)
        self.refreshColors = QtGui.QPushButton("Randomize Colors")
        self.refreshColors.clicked.connect(self.generateColors)
        self.setY100 = QtGui.QPushButton("Auto Y Axis")
        self.setY100.clicked.connect(self.yAxTo100)
        self.setX100 = QtGui.QPushButton("Auto X Axis")
        self.setX100.clicked.connect(self.xAxTo100)
        # self.lockYAx = QtGui.QCheckBox("Lock Y Axis")
        # self.lockYAx.setChecked(True)
        # self.lockYAx.clicked.connect(self.lockYAxisClicked)
        # self.lockXAx = QtGui.QCheckBox("Lock X Axis")
        # self.lockXAx.setChecked(False)
        # self.lockXAx.clicked.connect(self.lockXAxisClicked)

        buttonLayout1 = QtGui.QHBoxLayout()
        buttonLayout1.addWidget(self.hideButton)
        buttonLayout1.addStretch(0)
        buttonLayout1.addWidget(self.lineSelect)

        buttonLayout2 = QtGui.QHBoxLayout()
        buttonLayout2.addWidget(self.oneMinButton)
        buttonLayout2.addWidget(self.tenMinButton)
        buttonLayout2.addWidget(self.twoHrButton)
        buttonLayout2.addWidget(self.twelveHrButton)
        buttonLayout2.addWidget(self.threeDayButton)
        buttonLayout2.addWidget(self.oneWkButton)
        buttonLayout2.addWidget(self.allButton)
        buttonLayout2.addStretch(0)

        buttonLayout3 = QtGui.QHBoxLayout()
        buttonLayout3.addWidget(self.autoscaleCheckBox)
        # buttonLayout3.addWidget(self.lockYAx)
        # buttonLayout3.addWidget(self.lockXAx)
        buttonLayout3.addWidget(self.setY100)
        buttonLayout3.addWidget(self.setX100)
        buttonLayout3.addWidget(self.refreshColors)
        buttonLayout3.addStretch(0)

        self.buttonFrame = QtGui.QFrame()
        self.buttonFrame.setLayout(buttonLayout3)
        self.buttonFrame.setStyleSheet(".QPushButton{background:rgb(70,80,88)}"
                                       "QCheckBox{color:rgb(189,195, 199)}"
                                       ".QFrame{background-color: rgb(52, 73, 94); "
                                       "margin:0px; border:2px solid rgb(0, 0, 0);}")

        self.dropdownFont = QtGui.QFont()
        self.dropdownFont.setPointSize(12)
        self.autoscaleCheckBox.setFont(self.dropdownFont)
        self.refreshColors.setFont(self.dropdownFont)
#        self.lockYAx.setFont(self.dropdownFont)
        self.setY100.setFont(self.dropdownFont)
 #       self.lockXAx.setFont(self.dropdownFont)
        self.setX100.setFont(self.dropdownFont)
        self.initialized = False

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addLayout(buttonLayout1)
        mainLayout.addLayout(buttonLayout2)

        mainLayout.addWidget(self.frame)
        frameLayout.addWidget(self.buttonFrame)
        self.setLayout(mainLayout)

        self.installEventFilter(self)
        self.togglePlot()


        self.timespan = 60 * 60# default 1 minute

        self.device.addParameterSignal.connect(self.addComboBoxItem)

    def eventFilter(self, receiver, event):
        '''Filter out scroll events so that only pyqtgraph catches them'''
        if(event.type() == QtCore.QEvent.Wheel):
            # print "scroll detected"
            return True
        else:
            # print "scroll not detected"
            return False

    def generateColors(self):
        # print "RAINBOW COLORS!!"
        for curve in self.curves:

            self.r = np.random.random() * 200
            self.g = np.random.random() * 200
            self.b = np.random.random() * 200

            pen = pg.mkPen(cosmetic=True, width=2,
                           color=(self.r, self.g, self.b))
            curve.setPen(pen)

    def initialize(self):
        dataset = self.device.getFrame().getDataChestWrapper()
        if dataset == None:
            return
        varNames = dataset.getVariables()
       # print "varNames:", varNames

        for i, var in enumerate(varNames):
            #Qvar = QtCore.QString(var.replace('_',' '))
            self.addComboBoxItem(var)
            self.lineSelect.setChecked(i, True)

        self.initialized = True

        device = self.device

        self.setupUnits()

    def addComboBoxItem(self, name):
        self.lineSelect.addItem(name.replace('_', ' '))
        self.lineSelect.setFont(self.dropdownFont)

    def setupUnits(self):

        frame = self.device.getFrame()
        vars = self.device.getFrame().getDataChestWrapper().getVariables()
        if(len(vars) > 1):
            yLabel = vars[0] # Assume that all params have the same unit for now.
        else:
            yLabel = "Dependent Variable"
        self.viewboxes = []
        axes = []
        units = self.device.getFrame().getDataChestWrapper().getUnits()[0]
        axes.append(self.p.getAxis('left'))

        if units != None:
            axes[-1].setLabel(text=str(yLabel + "(" + units + ")"))
        else:
            axes[-1].setLabel(text=str(yLabel))

    def plot(self, **kwargs):
            # print "plotting"
       # traceback.print_stack()
        if self.hidden:
            return
        if not self.initialized:
            self.initialize()

        for pa in self.viewboxes:
            pa.setGeometry(self.p.vb.sceneBoundingRect())
            pa.linkedViewChanged(self.p.vb, pa.XAxis)

        time = kwargs.get('mode','default')
        maxtime = kwargs.get('end', 'now')
        self.timespan = kwargs.get('start', self.timespan)

        autoRange = kwargs.get('autoRange', False)

        # If time was specified, then autorange
        self.setupUnits()
        if time == 'range':
            if maxtime == 'now':
                maxtime = tm.time()
            if mintime == 'all':
                mintime = 0
        elif time == 'default':
            maxtime = tm.time()
            mintime = maxtime - self.timespan
            #mintime = maxtime - 60*60 # default 1 hour

        elif type(time) is int:
            maxtime = tm.time()
            mintime = maxtime - time # default 1 hour


        # data = self.device.getFrame().getDataSet().getData()
        #print "maxtime:", maxtime, "mintime:", mintime
        columns_to_request = ['capture_time']
        columns_to_request.extend(self.device.getFrame().getDataChestWrapper().getVariables())

        data = self.device.getFrame().getDataChestWrapper().query(columns_to_request, 'range', 'capture_time', mintime, maxtime)

        data = np.array(data).astype(float)
        #print "data is",data
        # if data == None:
        #     print "no data!"
        #     return
        times = [col[0] for col in data]
        i = 0

        while len(self.curves) < len(columns_to_request) - 1:
            self.pen = pg.mkPen(cosmetic=True, width=2, color=(0, 0, 0))
            varNames = self.device.getFrame().getDataChestWrapper().getVariables()
            #print "varNames: ", varNames, i
            self.curves.append(self.p.plot([0], pen=self.pen, name=varNames[i].replace('_', ' ')))
            i = i + 1
            self.generateColors()
        # TODO: Optimize  this
        for i, col in enumerate(columns_to_request[1::]): # Skip capture_time column
            #print "len cols\ttimes", len(col), len(times)
            if self.lineSelect.isChecked(i):
                self.curves[i].setData(times, [d[i+1] for d in data], antialias=False)
                self.curves[i].setVisible(True)
            else:
                self.curves[i].setVisible(False)
        if self.autoscaleCheckBox.isChecked():
            try:
                self.p.autoRange()
                self.autoscaleCheckBox.setChecked(True)
                self.processRangeChangeSig = False
                self.processRangeChangeSig = True
            except:
                pass

    def rangeChanged(self):
        pass
        if self.processRangeChangeSig and self.autoscaleCheckBox.isChecked():
             self.autoscaleCheckBox.setChecked(False)
        # if self.lockYAx.isChecked():
        #     self.yAxTo100()
        #
        # if self.lockXAx.isChecked():
        #     self.xAxTo100()

    def yAxTo100(self):
        pass
        #self.p.enableAutoRange(axis='y')

    def xAxTo100(self):
        pass
        #self.p.enableAutoRange(axis='x')

    def lockXAxisClicked(self):

        self.lockYAx.setChecked(False)
        self.lockXAx.setChecked(True)

        self.processRangeChangeSig = False
        self.rangeChanged()
        self.processRangeChangeSig = True

    def lockYAxisClicked(self):
        self.lockYAx.setChecked(True)
        self.lockXAx.setChecked(False)
        self.processRangeChangeSig = False
        self.rangeChanged()
        self.processRangeChangeSig = True

    def show(self):
        if self.hidden:
            self.togglePlot()

    def togglePlot(self):

        if not self.hidden:
            self.win.hide()
            self.oneMinButton.hide()
            self.tenMinButton.hide()
            self.twoHrButton.hide()
            self.twelveHrButton.hide()
            self.threeDayButton.hide()
            self.oneWkButton.hide()
            self.allButton.hide()
            self.lineSelect.hide()
            self.hideButton.setText("Show Plot")
            self.hidden = True
            self.autoscaleCheckBox.hide()
            self.buttonFrame.hide()
            self.frame.hide()
        elif self.hidden:
            if self.device.getFrame().getDataChestWrapper() == None:
                return
            self.win.show()
            self.oneMinButton.show()
            self.tenMinButton.show()
            self.twoHrButton.show()
            self.twelveHrButton.show()
            self.threeDayButton.show()
            self.oneWkButton.show()
            self.allButton.show()
            self.plot(time='default')
            self.lineSelect.show()
            self.hideButton.setText("Hide Plot")
            self.hidden = False
            self.autoscaleCheckBox.show()
            self.buttonFrame.show()
            self.frame.show()


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        #  super().__init__(*args, **kwargs)

        super(TimeAxisItem, self).__init__(*args, **kwargs)
        # Timezone correction, take daylight savings into account.
        self.timeOffset = -(tm.mktime(tm.gmtime()) - tm.mktime(tm.localtime()))+3600*tm.localtime().tm_isdst

    def tickStrings(self, values, scale, spacing):
        # PySide's QTime() initialiser fails miserably and dismisses args/kwargs
        # return [QTime().addMSecs(value).toString('mm:ss') for value in
        # values]

        return [int2dt(value + self.timeOffset).strftime("%x %X") for value in values]


TS_MULT_us = 1e6


def int2dt(ts, ts_mult=TS_MULT_us):
    return(datetime.utcfromtimestamp(float(ts)))
