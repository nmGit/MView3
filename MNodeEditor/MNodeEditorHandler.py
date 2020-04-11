from .MNodeEditor import NodeGui
from .MNodeTree import NodeTree
from MWeb import web


class MNodeEditorHandler:
    def __init__(self):
        # Create a nodeTree
        self.nodeTree = NodeTree()

        # Create a nodeEditor GUI window
        self.nodeEditor = NodeGui(web.devices, self.nodeTree)
#        self.scene = self.nodeTree.getScene()

        # Create a new node to represent each device in the node tree
    def begin(self):
        pass
#            newNode = MLabradNode(dev)
#            self.nodeTree.addNode(newNode)
            #devnode = self.nodeTree.newNode(self.nodeTree, device = device,   mode = 'labrad_device')
            # Tell the device's frame what it's node is
  #          dev.getFrame().setNode(newNode)
            # Create nodes representing the tiles in the main mView window
            #virtNode = MVirtualDeviceNode()
            # self.nodeTree.addNode(virtNode)
            #outnode = self.nodeTree.addNode(self.nodeTree, mode = 'output')
            # An anchor has been created on the device node for each parameter that it
            # has, create a ouput node that is able to connect to all of these
  #          self.scene = self.nodeTree.getScene()

    def showEditor(self):
        self.nodeEditor.show()

    def getTree(self):
        return self.nodeTree

    def stop(self):
        # print "stopping handler"
        web.keepGoing = False

