from MDevice import MDevice
import random
class MDummyDevice(MDevice):

    def __init__(self, *args, **kwargs):
        super(MDummyDevice, self).__init__(*args, **kwargs)
        self.name = args[0]
        print "Initialize dummy device"
        self.input_params = []

        # Give initial values
    def onBegin(self):
        pass
    def onLoad(self):
        for param in self.getParameters():
            #print param, "param type", self.getParameterType(param)
            if self.getParameterType(param) == 'output':
                self.input_params.append(param)
    def onAddParameter(self, *args, **kwargs):
        self.setReading(args[0], 0)
        pass

    def query(self):

        for param in self.input_params:
            #print self.getReading(param)

            self.setReading(param, self.getReading(param)+random.randint(-10,10))