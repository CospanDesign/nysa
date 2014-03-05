



import sys
import os
import time

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *


os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

import status
import actions

from graphics_scene import GraphicsScene
from graphics_view import GraphicsView


p = os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             "gui",
                             "pvg")
p = os.path.abspath(p)
sys.path.append(p)

#from default_graphics_scene import GraphicsScene
from visual_graph.graphics_widget import GraphicsWidget

class FPGABusView(GraphicsWidget):

    def __init__(self, parent):
        self.actions = actions.Actions()
        #Create a view
        self.view = GraphicsView(parent)
        #Create a scene
        self.scene = GraphicsScene(self.view)
        super (FPGABusView, self).__init__(self.view, self.scene)
        self.status = status.Status()
        self.boxes = {}
        self.show()
        self.fi = parent

    def clear(self):
        #self.status.Verbose(self, "Clearing the FPGA Image")
        #self.boxes = {}
        pass

    def update(self):
        self.view._scale_fit()
        super (FPGAImage, self).update()

    def sizeHint (self):
        size = QSize()
        size.setWidth(600)
        return size

