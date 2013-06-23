# Distributed under the MIT licesnse.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

'''
Log
  6/18/2013: Initial commit
'''

import os
import sys
import json
import inspect

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from box import Box

class Slave(Box):
    """Host Interface Box"""

    def __init__(self,
                 scene,
                 position,
                 instance_name,
                 color,
                 parameters,
                 rect,
                 bus):

        self.bus = bus
        self.s = scene
        super(Slave, self).__init__( position = position,
                                     scene = scene,
                                     name = instance_name,
                                     color = color,
                                     rect = rect,
                                     user_data = parameters)
        md = {}
        md["name"] = instance_name
        md["color"] = "color"
        md["data"] = parameters
        md["move_type"] = "move"

        #This will raise an error if there is an illegal bus type
        bus_type = bus.get_bus_type()
        if bus_type == "peripheral_bus":
            md["box_type"] = "peripheral_slave"
        elif bus_type == "memory_bus":
            md["box_type"] = "memory_slave"

        js = json.dumps(md)
        self.slave_data = js
        self.setAcceptDrops(True)
        self.sdbg = True



    def itemChange(self, a, b):
        #if self.sdbg: print "SLAVE: itemChange()"
        if self.isSelected():
            #if self.sdbg: print "\t%s is selected" % self.box_name
            self.s.slave_selected(self.box_name, self.bus, self.user_data)
        else:
            #if self.sdbg: print "\t%s is NOT selected" % self.box_name
            self.s.slave_deselected(self.box_name, self.bus, self.user_data)
        return super(Slave, self).itemChange(a, b)

    def dragEvent(self, dragEvent):
        if self.sdbg: print "SLAVE: dragEvent: %s" % self.box_name
    #    super(QGraphicsItem, self).dragEvent(dragEvent)

    def startDrag(self, dropActions):
        if self.sdbg: print "SLAVE: startDrag: %s" % self.box_name
        super(Slave, self).startDrag(dropActions)
    #    drag.start(Qt.MoveAction)
    #    mime_data = QMimeData()
    #    mime_data.setData("application/flowchart-data", self.slave_data)
    #    drag = QDrag(self)
    #    drag.setMimData(mime_data)
    #    drag.start(Qt.MoveAction)

    #def mousePressEvent(self, event):
    #    #Copy over the mime data to a new structure
    #    if self.sdbg: print "SLAVE.%s: startDrag: %s" % (inspect.getframeinfo(inspect.currentframe()).function, self.box_name)
    #    mime_data = QMimeData()
    #    mime_data.setData("application/flowchart-data", self.slave_data)

    #    #Create and dispatch a move event
    #    drag = QDrag(event.widget())
    #    drag.start(Qt.MoveAction)
    #    drag.setMimeData(mime_data)
    #    #drag.start(Qt.MoveAction)
    #    drag.exec_()
    #    if self.sdbg: print "\tdrag started"
    #    event.accept()
    #    super (Slave, self).mousePressEvent(event)



    #def mouseMoveEvent(self, event):
    #    if self.sdbg: print "SLAVE: mouseMoveEvent: %s" % self.box_name
    #    if (Qt.LeftButton & event.buttons()) > 0:
    #        l = QLineF(event.pos(), QPointF(event.buttonDownScreenPos(Qt.LeftButton)))
    #        if (l.length > QApplication.startDragDistance()):
    #            super(Slave, self).mouseMoveEvent(event)
    #            
    #        #Copy over the mime data to a new structure
    #        mime_data = QMimeData()
    #        mime_data.setData("application/flowchart-data", self.slave_data)

    #        #Create and dispatch a move event
    #        drag = QDrag(event.widget())
    #        drag.start(Qt.MoveAction)
    #        drag.setMimeData(mime_data)
    #        drag.start(Qt.MoveAction)
    #        if self.sdbg: print "\tdrag started"

    #    super(Slave, self).mouseMoveEvent(event)


        
