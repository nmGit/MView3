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
#from logilab.common.registry import traced_selection

__author__ = "Noah Meltzer"
__copyright__ = "Copyright 2016, McDermott Group"
__license__ = "GPL"
__version__ = "3.0.0"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"

import numpy as np
from MWeb import web
import sys
import traceback
from PyQt4 import QtGui, QtCore
from MCurve import MCurve
from functools import partial
import pyqtgraph as pg
import numpy as np
import time as tm
#from dateStamp import *
#from dataChest import *
from MCheckableComboBoxes import MCheckableComboBox
from datetime import datetime
import warnings



class MGrapher(QtGui.QWidget):
    def __init__(self, parent=None, **kwargs):
        '''
        Initialize new grapher
        :param parent: Parent
        :param kwargs: title: title of the graph
        '''
        QtGui.QWidget.__init__(self, parent)
        self.track = False
        self.processRangeChanged = True
        self.mousePressed = False
        self.installEventFilter(self)
        # Set the title
        self.title = kwargs.get("title", None)
        self.liveMode = kwargs.get("live_mode", True)

        pg.setConfigOption('background', web.color_scheme["dark"]["1st background"])
        pg.setConfigOption('foreground', web.color_scheme["dark"]["black"])



        self.mainFrame = QtGui.QFrame()
        self.mainFrame.setStyleSheet("background-color:rgb(100,10,10)")
        main_layout = QtGui.QVBoxLayout()



        self.win = pg.GraphicsWindow()
        #self.win.installEventFilter(self)

        self.mainViewBox = pg.ViewBox()
        self.mainViewBox.setMouseMode(self.mainViewBox.RectMode)
        #self.mainViewBox.installEventFilter(self)

        self.mainPlot = self.win.addPlot(title = self.title, axisItems={'bottom' : TimeAxisItem(orientation='bottom')}, viewBox=self.mainViewBox)
        self.mainPlot.addLegend()
        self.mainPlot.showGrid(x=True,y=True, alpha=0.5)
        self.mainPlot.getViewBox().setMouseEnabled(True, True)
        self.mainPlot.sigRangeChanged.connect(self.__range_changed)
        self.mainPlot.scene().sigMouseMoved.connect(self.__mouse_moved)
        self.mainPlot.scene().installEventFilter(self)
        pg.SignalProxy(self.mainPlot.scene().sigMouseMoved, rateLimit=60, slot=self.__mouse_moved)

        #self.mainPlot.setDownsampling(auto=True, mode='peak')

        self.lr_pen = pg.mkPen(color=(20,20,20),style=QtCore.Qt.DashLine,width=2.5)
        self.lr_hover_pen = pg.mkPen(color=(20,20,20), style=QtCore.Qt.DotLine,width=4.5)
        self.linearRegionSelectorX = pg.LinearRegionItem([100,700], pg.LinearRegionItem.Vertical, None, self.lr_pen, None, self.lr_hover_pen)
        self.linearRegionSelectorX.setZValue(10)

        self.linearRegionSelectorY = pg.LinearRegionItem([100,700], pg.LinearRegionItem.Horizontal, None, self.lr_pen, None, self.lr_hover_pen)
        self.linearRegionSelectorY.setZValue(10)

        self.linearRegionPlotY = self.win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.linearRegionPlotY.addItem(self.linearRegionSelectorY)
        self.linearRegionPlotY.getViewBox().setMouseEnabled(False, True)
        self.linearRegionPlotY.setPreferredHeight(200)
        self.linearRegionPlotY.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Ignored)
        # self.linearRegionPlotX.getViewBox().scaleBy(s=0.1,y=0.1)
        self.linearRegionSelectorY.sigRegionChanged.connect(self.__update_plot_y)

        self.win.nextRow()
        self.linearRegionPlotX = self.win.addPlot(axisItems={'bottom' : TimeAxisItem(orientation='bottom')})
        self.linearRegionPlotX.addItem(self.linearRegionSelectorX)
        self.linearRegionPlotX.getViewBox().setMouseEnabled(True, False)
        self.linearRegionPlotX.setPreferredWidth(200)
        self.linearRegionPlotX.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Maximum)
        #self.linearRegionPlotX.getViewBox().scaleBy(s=0.1,y=0.1)
        self.linearRegionSelectorX.sigRegionChanged.connect(self.__update_plot_x)



        # Dictionary holding all keys
        # {"Curve Name" : MCurve ...}
        self.curves = {}
        self.crosshair_pen = pg.mkPen(color=(150, 150, 180), style=QtCore.Qt.DotLine, width=2)
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.vLine.setZValue(-10)
        self.vLine.setPen( self.crosshair_pen)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.hLine.setZValue(-10)
        self.hLine.setPen( self.crosshair_pen)
        self.mainPlot.addItem(self.vLine, ignoreBounds=True)
        self.mainPlot.addItem(self.hLine, ignoreBounds=True)

        self.span = None
        self.last_y_max = 0
        self.last_y_min = 0
        # add GUI elements
        self.setStyleSheet("QPushButton{\
                           color:rgb(189,195, 199); \
                           background:rgb(70, 80, 88)};\
                           QFrame{\
                           color:rgb(189,195, 199); \
                           background:rgb(70, 80, 88)};")
        self.hideButton = QtGui.QPushButton("Hide Plot")
        self.hideButton.clicked.connect(self.__togglePlot)
        self.hidden = False

        self.oneMinButton = QtGui.QPushButton("1 min")
        self.oneMinButton.clicked.connect(
            partial(self.set_data_span,60))
        self.tenMinButton = QtGui.QPushButton("10 min")
        self.tenMinButton.clicked.connect(
            partial(self.set_data_span, 600))
        self.twoHrButton = QtGui.QPushButton("2 hr")
        self.twoHrButton.clicked.connect(
            partial(self.set_data_span, 7200))
        self.twelveHrButton = QtGui.QPushButton("12 hr")
        self.twelveHrButton.clicked.connect(
            partial(self.set_data_span, 43200))
        self.threeDayButton = QtGui.QPushButton("3 day")
        self.threeDayButton.clicked.connect(
            partial(self.set_data_span, 259200))
        self.oneWkButton = QtGui.QPushButton("1 week")
        self.oneWkButton.clicked.connect(
            partial(self.set_data_span, 604800))

        self.lineSelect = MCheckableComboBox()
        self.lineSelect.itemChecked.connect(self.__show_curve)
        self.lineSelect.itemUnChecked.connect(self.__hide_curve)
        #self.lineSelect.setSizeAdjustPolicy(1)
        self.lineSelect.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Maximum)

        self.autoscaleCheckBox = QtGui.QCheckBox("Auto Ranging")
        self.autoscaleCheckBox.setChecked(True)
        self.autoscaleCheckBox.clicked.connect(self.set_autorange)
        self.refreshColors = QtGui.QPushButton("Randomize Colors")
        self.refreshColors.clicked.connect(self.generate_colors)

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

        buttonLayout2.addStretch(0)

        buttonLayout3 = QtGui.QHBoxLayout()
        buttonLayout3.addWidget(self.autoscaleCheckBox)
        buttonLayout3.addWidget(self.refreshColors)
        buttonLayout3.addStretch(0)

        self.buttonFrame = QtGui.QFrame()
        self.buttonFrame.setLayout(buttonLayout3)
        self.buttonFrame.setStyleSheet(".QPushButton{background:rgb(70,80,88)}"
                                       "QCheckBox{color:rgb(189,195, 199)}"
                                       ".QFrame{background-color: rgb(52, 73, 94); "
                                       "margin:0px; border:2px solid rgb(0, 0, 0);}")


        graph_layout = QtGui.QVBoxLayout()
        graph_frame = QtGui.QFrame()
        graph_frame.setLayout(graph_layout)

        main_layout.addWidget(graph_frame)
        graph_layout.addLayout(buttonLayout1)
        graph_layout.addLayout(buttonLayout2)
        graph_layout.addWidget(self.win)
        self.mainFrame.setLayout(main_layout)
        #mainLayout.addWidget(self.mainFrame)

        graph_layout.addWidget(self.buttonFrame)
        self.setLayout(main_layout)
        self.__togglePlot()
        self.set_data_span(60)
        self.track_waveform(True)


    def add_curve(self, name):
        '''
        Add a curve to the graph
        :param name: Name of the curve to be displayed in the legend
        :return: Curve
        '''
        curve = MCurve(self, name)
        self.curves[name] = curve
        self.lineSelect.addItem(name, True)
        curve.data_changed_sig.connect(self.__data_updated)

        return curve

    def remove_curve(self, name):
        '''
        Remove a curve from the graph
        :param name: Name of the curve to be removed from the graph
        :return: True if success, False if fail
        '''
        pass

    def get_plot(self):
        return self.mainPlot
    def get_linear_region_plot_x(self):
        return self.linearRegionPlotX
    def get_linear_region_plot_y(self):
        return self.linearRegionPlotY
    def track_waveform(self, track):
        #self.mainPlot.setAutoPan(x=track)
        self.track = track
        #print "tracking:", track
        self.autoscaleCheckBox.setChecked(track)
    def get_curves(self):
        return self.curves
    def visible(self):
        return not self.hidden
    def set_data_span(self, span):
        '''
        Set the range of data to be displayed. This does not change the window position,
        rather it changes the width of the window.
        :param span: Width of window in seconds
        :return: Nothing
        '''



        self.span = span

    def get_time_range(self):
       # print self.mainPlot.getViewBox().viewRange()
        return self.mainPlot.getViewBox().viewRange()[0]

    def set_data_range(self, start, end, **kwargs):
        '''
        Set the plot range for the data
        :param kwargs:
        *start* : Include data from [start] seconds in the past
        *end* : Stop including data after [end] seconds in the past.\
                *None* indicates that the graphed data should be up to and including
                the most recent data.
        :return:
        '''
        autorange = kwargs.get("autorange", True)
        self.mainPlot.setXRange(start, end, padding=0)

    def set_autorange(self):
        self.linearRegionPlotY.autoRange()
        self.linearRegionPlotX.autoRange()
        self.mainPlot.enableAutoRange(x=True)
        if(self.autoscaleCheckBox.isChecked()):
            print "autoscale checked"
            self.track_waveform(True)
        else:
            print "autoscale unchecked"
            self.track_waveform(False)

    def generate_colors(self):
        for curve in self.curves:
            self.curves[curve].random_color()
    def getWidth(self):
        return self.width()

    def show_plot(self):
        if self.hidden:
            self.__togglePlot()

    def hide_plot(self):
        if not self.hidden:
            self.__togglePlot()

    def __range_changed(self):
        # Called when main plot is adjusted
        #print "range changed"
        self.processRangeChanged = False
        t1 = tm.time()


        self.__update_regionX()
        self.__update_regionY()

        t2 = tm.time()



        self.processRangeChanged = True
        #print "Time to update:", t2-t1
        pass

    def __update_plot_y(self):
        # Y region changed
        # print "range changed, updating region plot"
        # print "region", self.linearRegionSelectorX.getRegion()

        if(self.processRangeChanged):
           # print "update plot y, process range", self.processRangeChanged
            self.mainPlot.setYRange(*self.linearRegionSelectorY.getRegion(), padding=0)

    def __update_plot_x(self):
        # X region changed
        #print "range changed, updating region plot"
       # print "region", self.linearRegionSelectorX.getRegion()
        if(self.processRangeChanged):
            #print "update plot x, process range", self.processRangeChanged
            self.mainPlot.setXRange(*self.linearRegionSelectorX.getRegion(), padding=0)


    def __update_regionX(self):
        #print "update region x"
        #print "region changed, updating main plot"
        #print "range",self.linearRegionPlotX.getViewBox().viewRange()
        xregion=self.mainPlot.getViewBox().viewRange()[0]
        self.linearRegionSelectorX.setRegion(xregion)
        #yregion = self.linearRegionSelectorY.getRegion()
        #spread = yregion[1] - yregion[0]
        self.linearRegionPlotY.setXRange(*xregion, padding=0)
        #self.linearRegionPlotY.setYRange(yregion[0]-spread * 0.66,yregion[1]+spread * 0.66, padding=0)

    def __update_regionY(self):
        #print "update region y"
        # print "region changed, updating main plot"
        # print "range",self.linearRegionPlotX.getViewBox().viewRange()
        yregion = self.mainPlot.getViewBox().viewRange()[1]
        self.linearRegionSelectorY.setRegion(yregion)
       # xregion = self.linearRegionSelectorX.getRegion()
        #spread = xregion[1] - xregion[0]
        self.linearRegionPlotX.setYRange(*yregion, padding=0)
        #self.linearRegionPlotX.setXRange(xregion[0]-spread ** 2 * 0.66,xregion[1]+spread**2 * 0.66, padding=0)

    def __data_updated(self, curve):

        max_time = 0
        #self.mainPlot.enableAutoRange(y=True, x=False)

        for curve in self.curves:
            curr_time = self.curves[curve].getData()[0][-1]


            #print self.curves[curve].dataBounds(0)
            if (curr_time > max_time):
                max_time = curr_time
        current_x = max_time

        mins = []
        maxs = []
        for curve in self.curves:
            maxs.append(self.curves[curve].dataBounds(1, 1, [current_x - self.span, current_x])[1])
            mins.append(self.curves[curve].dataBounds(1, 1, [current_x - self.span, current_x])[0])
        print [current_x - self.span, current_x],"mins", mins, "maxs", maxs

        # if the window has moved out of bounds of original data bounds, then None is returned and we do not want to
        # rescale
        # TODO Can't tell if the above is a bug or not
        if maxs[0] != None:
            maximum = max(i for i in maxs if i is not None)
            minimum = min(i for i in mins if i is not None)

            if (self.track):
                #print "Min max", mins, maxs
                self.mainPlot.setYRange(minimum, maximum)
                self.mainPlot.setXRange(current_x - self.span, current_x, padding=0)
                self.linearRegionPlotY.autoRange()
                self.linearRegionPlotX.autoRange()
        else:
            current_x = self.mainPlot.getViewBox().viewRange()[0][1]
            #self.mainPlot.enableAutoRange(y=False)

        if (self.span == None):
            self.mainPlot.enableAutoRange(x = True)


    def __togglePlot(self):

        if not self.hidden:
            self.win.hide()
            self.oneMinButton.hide()
            self.tenMinButton.hide()
            self.twoHrButton.hide()
            self.twelveHrButton.hide()
            self.threeDayButton.hide()
            self.oneWkButton.hide()
            self.lineSelect.hide()
            self.hideButton.setText("Show Plot")
            self.hidden = True
            self.autoscaleCheckBox.hide()
            self.buttonFrame.hide()
            #self.mainFrame.hide()
        elif self.hidden:
            self.win.show()
            self.oneMinButton.show()
            self.tenMinButton.show()
            self.twoHrButton.show()
            self.twelveHrButton.show()
            self.threeDayButton.show()
            self.oneWkButton.show()
            self.lineSelect.show()
            self.hideButton.setText("Hide Plot")
            self.hidden = False
            self.autoscaleCheckBox.show()
            self.buttonFrame.show()
            #self.mainFrame.show()
    def __show_curve(self, curve):
        print "Show curve", curve
        curve = str(curve)
        self.curves[curve].show()
    def __hide_curve(self, curve):
        print "Hide curve", curve
        curve = str(curve)
        self.curves[curve].hide()

    def __mouse_moved(self,evt):
        #print "mouse moved",evt
        mousePoint = self.mainPlot.vb.mapSceneToView(evt)
        mouseX = mousePoint.x()
        mouseY = mousePoint.y()

        self.vLine.setPos(mouseX)
        self.hLine.setPos(mouseY)


        pass
    def __mainPlot_mousePressEvent(self):
        print "win mouse pressed"
        self.mousePressed = True
        if(self.mainViewBox):
            self.track_waveform(False)

    def __mainPlot_mouseReleaseEvent(self):
        # Need curves to refresh themselves when range changes if there is no periodic update occurring.
        # Periodic updates occur in a real-time data viewing context
        # It is safe to assume that any time a mouse release event fires, the user has been interacting with
        # the plot and it should be refreshed
        print "win mouse released"
        self.mousePressed = False
        if not self.liveMode:
            for curve in self.curves.keys():
                self.curves[curve].refresh()

    def eventFilter(self, receiver, event):
        '''Filter out scroll events so that only pyqtgraph catches them'''
       # print "Event:", event, "on", object
        if(event.type() == QtCore.QEvent.Wheel):
            # print "scroll detected"
            return True
        elif(event.type() == QtCore.QEvent.GraphicsSceneMousePress):
            print "Graphics scene mouse Press"
            self.__mainPlot_mousePressEvent()
            return False
        elif(event.type() == QtCore.QEvent.GraphicsSceneMouseRelease):
            print "Graphics scene mouse Release"
            self.__mainPlot_mouseReleaseEvent()
            # print "scroll not detected"
            return False
        else:
            return False
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
