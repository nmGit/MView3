import numpy as np
import pyqtgraph as pg
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from PyQt4 import QtGui
class MCurve(QObject):
    data_changed_sig = pyqtSignal(str)
    def __init__(self, plot, name, parent = None, **kwargs):
        QtGui.QWidget.__init__(self, parent)

        self.plot = plot
        self.name = name
        self.curve = self.plot.get_plot().plot([0], name=name.replace('_',' '), antialias=False)
        self.linear_selector_curve_x = self.plot.get_linear_region_plot_x().plot([0], antialias=False)
        self.linear_selector_curve_y = self.plot.get_linear_region_plot_y().plot([0], antialias=False)
        self.random_color()
        self.range_select_subsample = kwargs.get("range_select_subsample", 30)



    def random_color(self):
        self.r = np.random.random() * 200
        self.g = np.random.random() * 200
        self.b = np.random.random() * 200

        pen = pg.mkPen(cosmetic=True, width=2,
                       color=(self.r, self.g, self.b))
        self.curve.setPen(pen)
        self.linear_selector_curve_x.setPen(pen)
        self.linear_selector_curve_y.setPen(pen)

    def set_data(self, independent, dependent):
        '''
        Set the independent and dependent variables.
        Independent and dependent variables must be the same length
        :param independent: Independent vector
        :param dependent: Dependent vector
        :return:
        '''
        # for i,d in enumerate(independent):
        #     print "indep:", independent[i], "dep:", dependent[i]
        self.curve.setData(independent, dependent, connect='finite')
        self.curve.setDownsampling(auto=True, method='subsample')
#[0:-1:self.range_select_subsample]
        self.linear_selector_curve_x.setData(independent, dependent)
        self.linear_selector_curve_x.setDownsampling(ds=self.range_select_subsample, method='subsample')

        self.linear_selector_curve_y.setData(independent, dependent)
        self.linear_selector_curve_y.setDownsampling(ds=self.range_select_subsample, method='subsample')

        self.data_changed_sig.emit(str(self.name))
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
    def dataBounds(self, axis):
        return self.curve.dataBounds(axis)