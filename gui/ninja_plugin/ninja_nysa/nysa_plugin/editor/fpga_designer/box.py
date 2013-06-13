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


#A huge thanks to 'Rapid GUI Programming with Python and Qt' by Mark Summerfield

'''
Log
  6/05/2013: Initial commit
  6/12/2013: Adding support for links
'''

__author__ = "Dave McCoy dave.mccoy@cospandesign.com"

import os
import sys
from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4 import QtCore
from PyQt4.QtGui import *


from link import Link
from link import link_type as lt
from link import side_type as st

from link import get_inverted_side

Dirty = False

DEFAULT_BOX_SIZE = (100, 50)


class Box (QGraphicsItem):
    """Generic box used for flow charts"""

    def __init__( self,
                  position,
                  scene,
                  name = "Test",
                  color = "green",
                  select_func = None,
                  deselect_func = None,
                  rect = None,
                  user_data = None):

        super(Box, self).__init__()
        #Box Properties
        self.box_name = name
        self.color = QColor(color)
        self.user_data = user_data
        self.select_func = select_func
        self.deselect_func = deselect_func

        self.setFlags(QGraphicsItem.ItemIsSelectable    |
                      QGraphicsItem.ItemIsMovable       |
                      QGraphicsItem.ItemIsFocusable)
        if rect is None:
            rect = QRectF(0, 0, DEFAULT_BOX_SIZE[0], DEFAULT_BOX_SIZE[1])
        self.rect = rect
        self.style = Qt.SolidLine
        self.setPos(position)
        self.setMatrix(QMatrix())
        scene.clearSelection()
        scene.addItem(self)
        self.setSelected(True)
        self.setFocus()

        #Tooltip
        self.setToolTip(
          "Name: %s" % self.box_name
        )

        #Font
        self.text_font = QFont('White Rabbit')
        self.text_font.setPointSize(16)

        if self.select_func is not None:
          self.select_func(self.user_data)

        global Dirty
        Dirty = True
        self.links = {}

    def side_coordinates(self, side):
        if side == st.top:
            return QPointF(self.rect.width()/2, self.rect.top())
        if side == st.bottom:
            return QPointF(self.rect.width()/2, self.rect.bottom())
        if side == st.left:
            return QPointF(self.rect.left(), self.rect.height()/2)
        if side == st.right:
            return QPointF(self.rect.right(), self.rect.height()/2)


    def set_size(self, width, height):
        self.rect.setWidth(width)
        self.rect.setHeight(height)

    def contextMenuEvent(self, event):
        wrapped = []
        menu = QMenu(self.parentWidget())
        for text, func in (("&Demo Function", self.demo_function),):
            menu.addAction(text, func)
        menu.exec_(event.screenPos())

    def demo_function(self):
        print "Demo function!"

    def itemChange(self, a, b):
        if self.isSelected():
            self.select_func(self.user_data)
        else:
            self.deselect_func()
        return QGraphicsItem.itemChange(self, a, b)


    #Paint
    def paint(self, painter, option, widget):

        highlight_width = 8

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
        painter.setFont(self.text_font)

        #draw text
        pen.setColor(Qt.black)
        painter.setPen(pen)
        r = self.rect

        #qfm = QFontMetrics(self.text_font)
        #size = qfm.boundingRect(r, Qt.AlignCenter, self.box_name)
        painter.drawText(r, Qt.AlignCenter, self.box_name)
        self.update_connections()


    def boundingRect(self):
        return self.rect.adjusted(-2, -2, 2, 2)

    def parentWidget(self):
        return self.scene().views()[0]

    #Edges
    def add_connection(self, box_widget, link_type, side):
        self.links[box_widget] = Link(self, box_widget, self.scene(), link_type)
        self.links[box_widget].from_box_side(side)

        #Set up the other side
        side = get_inverted_side(side)
        #self.output.Debug(self, "Link: %s" % str(self.links[box_widget]))
        box_widget.add_link_connection(self, self.links[box_widget], side)

    def add_link_connection(self, box_widget, link, side):
        """This is used to call add connection from one box to another"""
        #self.output.Debug(self, "in add_connection")
        self.links[box_widget] = link
        self.links[box_widget].to_box_side(side)

    def is_connected(self):
        if len(self.links) > 0:
            return True
        return False

    def get_connections(self):
        ls = []
        for link in self.links:
            ls.append(self.links[link])
        return ls

    def update_connections(self):
        for link in self.links:
            self.links[link].track_nodes()

    def remove_connection(self, box_widget):
        if box_widget in self.links:
            del self.links[box_widget]

    def remove_all_connections(self):
        keys = self.links.keys()
        for key in keys:
            self.remove_connection(key)

