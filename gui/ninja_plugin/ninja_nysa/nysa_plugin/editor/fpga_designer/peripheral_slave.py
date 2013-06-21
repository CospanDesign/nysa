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

from box import Box
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

from arbitor_master import ArbitorMaster

highlight_width = 8

class PeripheralSlave(Slave):
    """Host Interface Box"""

    def __init__(self,
                 scene,
                 instance_name,
                 parameters,
                 bus):

        self.nochange = False

        self.arbitor_masters = []
        self.links = {}
        self.arbitor_boxes = []
        self.selected_arbitor = None
        self.am_selected = False
        self.peripheral_bus = bus
        self.ignore_selection = False

        super(PeripheralSlave, self).__init__(position = QPointF(0.0, 0.0),
                                             scene = scene,
                                             instance_name = instance_name,
                                             color = PERIPHERAL_SLAVE_COLOR,
                                             rect = SLAVE_RECT,
                                             bus = bus,
                                             parameters = parameters)
        self.s = scene
        if 'arbitor_masters' in parameters:
            self.arbitor_masters = parameters["arbitor_masters"]
            #print "Arbitor Masters: %s" % self.arbitor_masters


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

        if len(self.arbitor_masters) > 0:
            arb_height = self.rect.height()
            arb_width  = self.rect.width() / 4
            arb_pos = QPointF(self.rect.width() - arb_width, 0)
            arb_rect = QRectF(arb_pos, QSizeF(arb_width, arb_height))
            r = QRectF(QPointF(r.x(), r.y()), QSizeF(self.rect.width() - arb_width, r.height())) 

            pen = QPen(self.style)
            pen.setColor(Qt.black)
            pen.setWidth(1)
            if option.state & QStyle.State_Selected:
                #Selected
                pen.setColor(Qt.black)
                pen.setWidth(highlight_width)

            painter.setPen(pen)
            painter.drawRect(arb_rect)
            painter.fillRect(arb_rect, QColor(Qt.white))

            painter.drawText(arb_rect, Qt.AlignCenter, "M")

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
        start = self.mapToScene(self.side_coordinates(st.right))

        for link in self.links:
            end = self.mapToScene(self.mapFromItem(link, link.side_coordinates(st.left))) 
            self.links[link].set_start_end(start, end)

    def show_arbitor_masters(self):
        if len(self.arbitor_boxes) > 0:
            #print "There are already arbitor boxes: %d" % len(self.arbitor_boxes)
            return 

        num_m = len(self.arbitor_masters)
        if num_m == 0:
            return

        #print "Add %d arbitor boxes" % num_m

        #setup the start position for the case where there is only one master
        position = QPointF(self.pos())
        rect = QRectF(self.rect)
        arb_x = position.x() + rect.width() + ARB_MASTER_HORIZONTAL_SPACING
        arb_y = position.y() + rect.height() / 2
        arb_y -= (num_m - 1) * ARB_MASTER_VERTICAL_SPACING
        arb_y -= ((num_m - 1) * ARB_MASTER_RECT.height()) / 2

        arb_pos = QPointF(arb_x, arb_y)

        for i in range(0, len(self.arbitor_masters)):
            #print "Add Arbitor %s" % self.arbitor_masters[i]
            arb_rect = QRectF(ARB_MASTER_RECT)

            am = ArbitorMaster(name = self.arbitor_masters[i], 
                               position = arb_pos,
                               scene = self.scene(),
                               slave = self)

            #am.movable(False)

            self.arbitor_boxes.append(am)
            al = Link(self, am, self.scene(), lt.arbitor_master)
            al.from_box_side(st.right)
            al.to_box_side(st.left)

            al.en_bezier_connections(True)
            self.links[am] = al

            #Progress the position
            arb_pos = QPointF(arb_pos.x(), arb_pos.y() + arb_rect.height() + ARB_MASTER_VERTICAL_SPACING)

        self.update_links()

    def is_arbitor_master_selected(self):
        for am in self.arbitor_boxes:
            if am.isSelected():
                return True
        return False

    def arbitor_master_selected(self, arbitor_master):
        #print "Slave arbitor master selected: %s" % arbitor_master
        if self.ignore_selection:
            return

        self.ignore_selection = True
        self.remove_arbitor_masters()
        position = QPointF(self.pos())
        rect = QRectF(self.rect)
        arb_x = position.x() + rect.width() + ARB_MASTER_HORIZONTAL_SPACING
        arb_y = position.y() + (rect.height() / 2)  - (ARB_MASTER_ACT_RECT.height() / 2)

        arb_pos = QPointF(arb_x, arb_y)
        #print "Adding arbitor master"
        am = ArbitorMaster(name = arbitor_master,
                           position = arb_pos,
                           scene = self.scene(),
                           slave = self)

        am.set_activate(True)
        self.arbitor_boxes.append(am)
        al = Link(self, am, self.scene(), lt.arbitor_master)
        al.from_box_side(st.right)
        al.to_box_side(st.left)

        al.en_bezier_connections(True)
        self.links[am] = al

        #print "update links"
        self.update_links()
        self.ignore_selection = False

    def remove_arbitor_masters(self):
        print "PS: Remove Arbitor Masters"
        ams = self.links.keys()
        for am in ams:
            self.scene().removeItem(self.links[am])

        self.links = {}
        for am in ams:
            am.clear_link()
            self.s.removeItem(am)

        #if len(ams) > 0:
        #    print "Removed arbitor masters"

        self.arbitor_boxes = []

    def mouseReleaseEvent(self, event):
        if (len(self.arbitor_masters) > 0) and (len(self.arbitor_boxes) == 0):
            self.show_arbitor_masters()
        return QGraphicsItem.mouseReleaseEvent(self, event)

    def itemChange(self, a, b):
        #print "Peripheral slave item change: %s" % self.box_name
        if self.isSelected():
            self.peripheral_bus.slave_selection_changed(self)

        return super(PeripheralSlave, self).itemChange(a, b)


