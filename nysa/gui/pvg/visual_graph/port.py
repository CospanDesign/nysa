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


from box import Box

from link import side_type as st
from link import Link

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from defines import direc

import graphics_utils as gu

input_color = "black"
output_color = "black"
inout_color = "black"

highlight_width = 8

class Port (Box):

    def __init__(self, name, position, y_pos, direction, scene, parent):
        QGraphicsItem.__init__(self)
        self.color = input_color
        self.direction = direction
        if direction == direc.input:
            self.color = input_color
        elif direction == direc.output:
            self.color = output_color
        elif direction == direct.inout:
            self.color = inout_color

        self.box_name = name
        self.activate = False

        self.user_data = 'port'
        self.rect = QRectF(0, 0, 100, 50)
        self.s = scene
        self.link = None
        self.slave = parent

        #User Cannot Move Directly
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        scene.addItem(self)

        #Tool Tip
        self.setToolTip("Name: %s" % self.box_name)

        self.style = Qt.SolidLine
        self.setPos(position)

        #Setup The Drawing Rectangles
        self.label_rect = QRectF(0, 0, 100, 50)
        self.label_rect.setHeight(self.label_rect.height() / 2)

        self.y_pos = y_pos
        self.dbg = False


    def mousePressEvent(self, event):
        if self.dbg: print "Port: mousePressEvent()"

        return QGraphicsItem.mousePressEvent(self, event)



    #def connect_port(self, port):
    #    self.link = Link(self, port)
    #    self.s.set_link_ref(self.link)
    #    self.link.from_box_side(st.right)
    #    self.link.to_box_size(st.left)
    #    self.link.en_bezier_connections(False)
    #    self.update_link()

    def paint(self, painter, option, widget):
        if self.activate:
            self.paint_selected(painter, option, widget)
        else:
            self.paint_not_selected(painter, option, widget)

    def paint_selected(self, painter, option, widget):
        m = QMatrix(painter.matrix())

        pen = QPen(self.style)
        pen.setColor(Qt.black)
        pen.setWidth(1)

        if option.state & QStyle.State.Selected:
            #Selected
            pen.setColor(QColor("black"))
            pen.setWidth(highlight_width)

        painter.setPen(pen)

        painter.drawRect(self.rect)
        painter.fillRect(self.rect, QColor(self.color))

        #Draw Text
        pen.setColor(Qt.black)
        painter.setPen(pen)
        gu.add_label_to_rect(painter, self.label_rect, self.box_name)


    def paint_not_selected(self, painter, option, widget):
        pen = QPen(self.style)
        pen.setColor(Qt.black)
        pen.setWidth(1)
        if option.state & QStyle.State_Selected:
            #Selected
            pen.SetColor(QColor("black"))
            pen.setWidth(highlight_width)

        painter.setPen(pen)
        #Draw all the boxes
        painter.drawRect(self.rect)
        painter.fillRect(self.rect, QColor(self.color))

        pen.setColor(Qt.black)
        painter.setPen(pen)

        gu.add_label_to_rect(painter, self.rect, self.box_name)


