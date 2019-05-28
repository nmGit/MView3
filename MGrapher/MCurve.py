import numpy as np
import pyqtgraph as pg
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from PyQt4 import QtGui
import time
import threading
import traceback
class MCurve(QObject):
    data_changed_sig = pyqtSignal(str)

    def __init__(self, plot, name, parent = None, **kwargs):
        QtGui.QWidget.__init__(self, parent)

        self.plot = plot
        self.name = name
        self.curve = self.plot.get_plot().plot([0], name=name.replace('_',' '), antialias=False)
        self.pen = pg.mkPen(cosmetic=True, width=2)
        self.curve.setPen(self.pen)
        self.linear_selector_curve_x = self.plot.get_linear_region_plot_x().plot([0], antialias=False)
        self.linear_selector_curve_y = self.plot.get_linear_region_plot_y().plot([0], antialias=False)
        self.random_color()
        self.independent = [np.nan]
        self.dependent = [np.nan]



    def random_color(self):
        self.r = np.random.random() * 200
        self.g = np.random.random() * 200
        self.b = np.random.random() * 200


        self.pen.setColor(QtGui.QColor(self.r, self.g, self.b))

        self.curve.setPen(self.pen)
        self.linear_selector_curve_x.setPen(self.pen)
        self.linear_selector_curve_y.setPen(self.pen)

    def setPen(self, pen):
        self.curve.setPen(pen)
        self.pen = pen
    def getPen(self):
        #return self.curve.opts['pen']  # Not part of the actual pyqtgraph API !!!!
        return self.pen
    def refresh(self):
        self.set_data(self.independent, self.dependent)

    def set_data(self, independent, dependent):
        '''
        Set the independent and dependent variables.
        Independent and dependent variables must be the same length
        :param independent: Independent vector
        :param dependent: Dependent vector
        :return:
        '''
        if (not isinstance(threading.current_thread(), threading._MainThread)):
            print "ERROR"
            traceback.print_exc()
            raise RuntimeError("Cannot update curve from outside the main thread")
        #traceback.print_stack()
        self.independent = independent
        self.dependent = dependent
        t1 = time.time()
        if(not self.plot.visible()):
            return
        # for i,d in enumerate(independent):
        #     print "indep:", independent[i], "dep:", dependent[i]

        plot_start_time = self.plot.get_time_range()[0]
       # print "Range", self.plot.get_time_range(), "start time", plot_start_time

        start_index = len(independent)-1
        if(plot_start_time > 0 and independent[0] < plot_start_time):
            while (independent[start_index] > plot_start_time):
                start_index -= 1
        elif(start_index > 0):
            start_index = 0
        else:
            return

        plot_end_time = self.plot.get_time_range()[1]

        end_index = len(independent) - 1
        if (plot_end_time > 0 and independent[0] < plot_end_time):
            while (independent[end_index] > plot_end_time):
                end_index -= 1
        elif (end_index > 0):
            end_index = len(independent)-1
        else:
            return

        t2 = time.time()
       # print "Time find start/end index", t2-t1
        t3 = time.time()

        chopped_independent = independent[start_index:end_index]
        chopped_dependent = dependent[start_index:end_index]

        #print "chopped" ,chopped_dependent, chopped_independent
        self.range_select_subsample = (len(chopped_independent) / self.plot.getWidth()) + 1

        chopped_independent_sub = chopped_independent[0:-1:self.range_select_subsample]
        chopped_dependent_sub = chopped_dependent[0:-1:self.range_select_subsample]

        #print "chopped sub", self.range_select_subsample,chopped_dependent_sub, chopped_independent_sub
        self.curve.setData(chopped_independent_sub, chopped_dependent_sub, connect='finite')
       # self.curve.setDownsampling(ds=self.range_select_subsample, method='subsample')
#[0:-1:self.range_select_subsample]

        independent_subsampled_lsx = independent[0:-1:self.range_select_subsample*100]
        dependent_subsampled_lsx = dependent[0:-1:self.range_select_subsample * 100]

        independent_subsampled_lsy = chopped_independent[0:-1:self.range_select_subsample*10]
        dependent_subsampled_lsy = chopped_dependent[0:-1:self.range_select_subsample * 10]

        self.linear_selector_curve_x.setData(independent_subsampled_lsx, dependent_subsampled_lsx)
    #    self.linear_selector_curve_x.setDownsampling(ds=self.range_select_subsample*10, method='subsample')

        self.linear_selector_curve_y.setData(independent_subsampled_lsy, dependent_subsampled_lsy)
    #    self.linear_selector_curve_y.setDownsampling(ds=self.range_select_subsample*100, method='subsample')

        self.data_changed_sig.emit(str(self.name))
        t4 = time.time()
      #  print "time to set data", t4-t3, "start index:", start_index, "end index:", end_index

    def hide(self):
        self.curve.setVisible(False)
        self.linear_selector_curve_y.setVisible(False)
        self.linear_selector_curve_x.setVisible(False)
    def show(self):
        self.curve.setVisible(True)
        self.linear_selector_curve_y.setVisible(True)
        self.linear_selector_curve_x.setVisible(True)

    def getPyQtCurve(self):
        return self.curve
    def dataBounds(self, axis, frac = 1, orthoRange = None):
        return self.curve.dataBounds(axis, frac, orthoRange)
    def getData(self):
        return [self.independent, self.dependent]