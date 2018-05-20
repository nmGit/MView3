from MDevice import MDevice
import random
class MDummyDevice(MDevice):

    def __init__(self, *args, **kwargs):
        super(MDummyDevice, self).__init__(*args, **kwargs)
        self.name = args[0]
        print "Initialize dummy device"
        # Give initial values

    def onAddParameter(self, *args, **kwargs):
        self.setReading(args[0], 0)
        pass

    def query(self):

        for param in self.getParameters():
            #print self.getReading(param)
            self.setReading(param, self.getReading(param)+random.randint(-10,10))