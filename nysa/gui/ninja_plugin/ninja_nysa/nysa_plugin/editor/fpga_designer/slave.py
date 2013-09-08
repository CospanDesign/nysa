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
import graphics_utils as gu

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
        #if self.sdbg: print "SLAVE: itemChange()"
        if self.isSelected():
            #if self.sdbg: print "\t%s is selected" % self.box_name
            self.s.slave_selected(self.box_name, self.bus, self.user_data)
        else:
            #if self.sdbg: print "\t%s is NOT selected" % self.box_name
            self.s.slave_deselected(self.box_name, self.bus, self.user_data)
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

            else:
                self.dragging = True
                self.hide()
                if self.sdbg: print "SLAVE.%s: startDrag: %s" % (inspect.getframeinfo(inspect.currentframe()).function, self.box_name)
                mime_data = QMimeData()
                mime_data.setData("application/flowchart-data", self.slave_data)
                
               
                #Create and dispatch a move event
                drag = QDrag(event.widget())
                drag.start(Qt.MoveAction)
                drag.setMimeData(mime_data)
                #drag.start(Qt.MoveAction)
                
                #create an image for the drag
                size = QSize(self.start_rect.width(), self.start_rect.height())
                pixmap = QPixmap(size)
                pixmap.fill(QColor(self.color))
                painter = QPainter(pixmap)
                pen = QPen(self.style)
                pen.setColor(Qt.black)
                painter.setPen(pen)
                painter.setFont(self.text_font)
                #painter.drawText(0, 0, 100, 100, 0x24, self.box_name)

                gu.add_label_to_rect(painter, self.rect, self.box_name)
                painter.end()
                drag.setPixmap(pixmap)
                #p = QPointF(event.buttonDownScreenPos(Qt.LeftButton))
                #p = p.toPoint()
                if self.dbg: print "Position: %f, %f" % (pos.x(), pos.y())
                drag.setHotSpot(epos.toPoint())
                
                if self.sdbg: print "\tdrag started"
                drag.exec_()
                event.accept
                #self.s.invalidate(self.s.sceneRect())

        super(Slave, self).mouseMoveEvent(event)


    def paint(self, painter, option, widget):
        if self.dbg: print "Position: %f %f" % (self.pos().x(), self.pos().y())
        super(Slave, self).paint(painter, option, widget)
        
