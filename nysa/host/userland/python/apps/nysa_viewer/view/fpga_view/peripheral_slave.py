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
  6/14/2013: Initial commit
'''

import os
import sys
from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4 import QtCore
from PyQt4.QtGui import *

from visual_graph.box import Box
from slave import Slave

from defines import SLAVE_RECT
from defines import PERIPHERAL_SLAVE_COLOR
from defines import ARB_MASTER_HORIZONTAL_SPACING
from defines import ARB_MASTER_VERTICAL_SPACING
from defines import ARB_MASTER_RECT

from defines import ARB_MASTER_ACT_RECT
from defines import ARB_MASTER_ACT_COLOR


from link import side_type as st
from link import link_type as lt
from link import Link

highlight_width = 8

class PeripheralSlave(Slave):
    """Host Interface Box"""

    def __init__(self,
                 scene,
                 instance_name,
                 parameters,
                 bus):

        self.nochange = False

        self.links = {}
        self.am_selected = False
        self.peripheral_bus = bus
        self.ignore_selection = False
        self.dbg = False

        super(PeripheralSlave, self).__init__(position = QPointF(0.0, 0.0),
                                             scene = scene,
                                             instance_name = instance_name,
                                             color = PERIPHERAL_SLAVE_COLOR,
                                             rect = SLAVE_RECT,
                                             bus = bus,
                                             parameters = parameters)
        self.s = scene
        self.movable(False)

    def paint(self, painter, option, widget):

        pen = QPen(self.style)
        pen.setColor(Qt.black)
        pen.setWidth(1)
        if option.state & QStyle.State_Selected:
          #Selected
          pen.setColor(QColor("black"))
          pen.setWidth(highlight_width)

        painter.setPen(pen)
        painter.drawRect(self.rect)
        painter.fillRect(self.rect, QColor(self.color))

        #draw text
        r = QRectF(self.rect)

        painter.setFont(self.text_font)
        pen.setColor(Qt.black)
        painter.setPen(pen)
        br = painter.fontMetrics().boundingRect(self.box_name)

        scale_x = r.width() / br.width()

        if scale_x > 1.0:
            painter.drawText(r, Qt.AlignCenter, self.box_name)
        else:
            #For the cases where the text is larger than th box
            font_height = br.height()
            box_height = r.height()
            painter.scale(scale_x, scale_x)
            br.translate(r.left() - br.left(), r.top() - br.top())
            br.translate(0.0, box_height * (0.5/scale_x) - font_height/2)
            painter.drawText(br, Qt.TextSingleLine, self.box_name)

    def update_links(self):
        if self.dbg: print "PS: update_links()"
        start = self.mapToScene(self.side_coordinates(st.right))

        for link in self.links:
            end = self.mapToScene(self.mapFromItem(link, link.side_coordinates(st.left))) 
            self.links[link].set_start_end(start, end)

    def mouseReleaseEvent(self, event):
        if self.dbg: print "PS: mouse release event()"
        return QGraphicsItem.mouseReleaseEvent(self, event)

    def itemChange(self, a, b):
        if self.isSelected():
            self.peripheral_bus.slave_selection_changed(self)
        return super(PeripheralSlave, self).itemChange(a, b)
