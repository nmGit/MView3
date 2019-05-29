from MDevice import MDevice
import random
class MDummyDevice(MDevice):

    def __init__(self, *args, **kwargs):
        super(MDummyDevice, self).__init__(*args, **kwargs)
        self.name = args[0]
        self.last = 0.0
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
            if random.randint(0,9) > 7:
                self.setReading(param, None)
            else:
                self.last = self.last + random.randint(-10,10) + float(random.randint(-10,10))/10.0
                self.setReading(param, self.last)