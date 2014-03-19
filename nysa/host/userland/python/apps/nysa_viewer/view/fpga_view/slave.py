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

from visual_graph.box import Box
import visual_graph.graphics_utils as gu

class Slave(Box):
    """Slave Box"""

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
        self.dragging = False
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
            md["type"] = "peripheral_slave"
        elif bus_type == "memory_bus":
            md["type"] = "memory_slave"

        js = json.dumps(md)
        self.slave_data = js
        self.setAcceptDrops(True)
        self.sdbg = False

    def contextMenuEvent(self, event):

        menu_items = (("&Remove", self.remove_slave),)

        menu = QMenu(self.parentWidget())
        for text, func in menu_items:
            menu.addAction(text, func)
        menu.exec_(event.screenPos())


    def remove_slave(self):
        self.s.remove_slave(self)

    def itemChange(self, a, b):
        if QGraphicsItem.ItemSelectedHasChanged == a:
            if b.toBool():
                self.s.slave_selected(self.box_name, self.bus)
            else:
                self.s.slave_deselected(self.box_name, self.bus)
        return super(Slave, self).itemChange(a, b)

    def dragMoveEvent(self, event):
        if self.dbg: print "Drag Move Event"
        super(Slave, self).dragMoveEvent(event)

    def mouseMoveEvent(self, event):
        if self.sdbg: print "SLAVE: mouseMoveEvent: %s" % self.box_name
        if (Qt.LeftButton & event.buttons()) > 0:
            pos = event.pos()
            epos = event.buttonDownPos(Qt.LeftButton)
            l = QLineF(pos, epos)
            if (l.length() < QApplication.startDragDistance()):
            #if (l.length() < 10):
                if self.dbg: print "\tLength: %f" % l.length()
                event.accept
                return
        super(Slave, self).mouseMoveEvent(event)


    def paint(self, painter, option, widget):
        if self.dbg: print "Position: %f %f" % (self.pos().x(), self.pos().y())
        super(Slave, self).paint(painter, option, widget)
        
