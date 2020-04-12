import sys
import traceback
import os

sys._excepthook = sys.excepthook
def exception_hook(exctype, value, tb):


    traceback.print_tb(tb)
    print(exctype, value, tb)
#    sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook

sys.dont_write_bytecode = True

print("importing mgui")
print('__file__={0:<35} | __name__={1:<20} | __package__={2:<20}'.format(__file__, __name__, str(__package__)))
print(os.getcwd())
from MGui import MGui  # Handles all gui operations. Independent of labrad.

from PyQt5 import QtCore, QtGui
from MDevices.MDummyDevice import MDummyDevice
from MDevices.MVirtualDevice import MVirtualDevice
from MDevices.Mhdf5Device import Mhdf5Device

# import grapher as alexGrapher
from MNodeEditor.MNodes import runningAverage
from MNodeEditor import MNodeTree

from MNodeEditor.MNodes import MDeviceNode

sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(0)
sys.excepthook = exception_hook

class mViewer:
    gui = None
    devices = []

    def __init__(self, parent=None):
        # Establish a connection to labrad
        print("here")
        self.gui = MGui.MGui()

        self.dd1 = MDummyDevice("Dummy 1")

        self.dd1.addParameter("Field 1")
        self.dd1.addParameter("Field 2")
        self.dd1.addParameter("Field 3")
        self.dd1.addParameter("Field 4")
        self.dd1.addParameter("Field 5")
        self.dd1.addParameter("Field 6")
        self.dd1.addParameter("Field 7")
        self.dd1.addParameter("Field 8")
        self.dd1.addParameter("Field 9")
        self.dd1.log(True)
        self.dd1.addPlot()
        self.dd1.begin()
        self.gui.addDevice(self.dd1)

        self.dd2 = MDummyDevice("Dummy 2")
        self.dd2.addParameter("Field 1")
        self.dd2.addParameter("Field 2")
        self.dd2.addParameter("Field 3")
        self.dd2.addParameter("Field 4")
        self.dd2.addParameter("Field 5")
        self.dd2.log(True)
        self.dd2.addPlot()
        self.dd2.begin()
        self.gui.addDevice(self.dd2)

        self.gui.addWidget(QtGui.QLabel("HI"))
        self.gui.setRefreshRate(0.5)
        self.gui.startGui('Test Gui')


# In python, the main class's __init__() IS NOT automatically called

viewer = mViewer()
viewer.__init__()