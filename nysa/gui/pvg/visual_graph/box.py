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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from link import Link
from link import side_type as st

Dirty = False

DEFAULT_BOX_SIZE = (100, 50)

PADDING = 20


class Box (QGraphicsItem):
    """Generic box used for flow charts"""

    def __init__(self,
                 position,
                 scene,
                 name="Test",
                 color="green",
                 rect=None,
                 user_data=None):

        super(Box, self).__init__()
        #Box Properties
        self.box_name = name
        self.color = QColor(color)
        self.user_data = user_data

        if rect is None:
            rect = QRectF(0, 0, DEFAULT_BOX_SIZE[0], DEFAULT_BOX_SIZE[1])

        self.rect = rect
        self.start_rect = QRectF(rect)

        self.style = Qt.SolidLine
        self.setPos(position)
        self.setMatrix(QMatrix())
        scene.clearSelection()
        scene.addItem(self)

        #self.setSelected(True)
        #self.setFocus()

        #Tooltip
        self.setToolTip(
          "Name: %s" % self.box_name
        )

        #Font
        self.text_font = QFont('White Rabbit')
        self.text_font.setPointSize(16)

        #if self.select_func is not None:
        #  self.select_func(self.user_data)

        global Dirty
        Dirty = True
        self.links = {}

        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemIsFocusable)
        self.dbg = False

    def movable(self, enable):
        self.setFlag(QGraphicsItem.ItemIsMovable, enable)

    def selectable(self, enable):
        if self.dbg: print "BOX: %s selectable %s" % (self.box_name, str(enable))
        self.setFlag(QGraphicsItem.ItemIsSelectable, enable)

    def side_coordinates(self, side):
        if side == st.top:
            return QPointF(self.rect.width() / 2, self.rect.top())
        if side == st.bottom:
            return QPointF(self.rect.width() / 2, self.rect.bottom())
        if side == st.left:
            return QPointF(self.rect.left(), self.rect.height() / 2)
        if side == st.right:
            return QPointF(self.rect.right(), self.rect.height() / 2)

    def set_size(self, width, height):
        self.rect.setWidth(width)
        self.rect.setHeight(height)

    def contextMenuEvent(self, event):
        #wrapped = []
        menu = QMenu(self.parentWidget())
        for text, func in (("&Demo Function", self.demo_function),):
            menu.addAction(text, func)
        menu.exec_(event.screenPos())

    def demo_function(self):
        print ("Demo function!")

    def itemChange(self, a, b):
        if self.isSelected():
            if self.scene() is not None:
                self.scene().box_selected(self.user_data)
        else:
            if self.scene() is not None:
                self.scene().box_deselected(self.user_data)
        return QGraphicsItem.itemChange(self, a, b)

    def update(self):
        self.update_links()


    def set_pen_border(self, option, pen):
        highlight_width = 8
        pen.setWidth(1)
        if option.state & QStyle.State_Selected:
            #Selected
            pen.setColor(QColor("black"))
            pen.setWidth(highlight_width)
        return pen

    #Paint
    def paint(self, painter, option, widget):


        pen = QPen(self.style)
        pen.setColor(Qt.black)
        pen.setWidth(1)
        self.set_pen_border(option, pen)
        '''
        if option.state & QStyle.State_Selected:
            #Selected
            pen.setColor(QColor("black"))
            pen.setWidth(highlight_width)
        '''

        painter.setPen(pen)
        painter.drawRect(self.rect)
        painter.fillRect(self.rect, QColor(self.color))
        painter.setFont(self.text_font)

        #draw text
        pen.setColor(Qt.black)
        painter.setPen(pen)

        self.add_label_to_rect(painter, self.rect, self.box_name)

    def boundingRect(self):
        return self.rect.adjusted(-2, -2, 2, 2)

    def parentWidget(self):
        return self.scene().views()[0]

    def add_label_to_rect(self, painter, rect, label):
        painter.save()
        r = QRectF(rect)
        br = painter.fontMetrics().boundingRect(label)
        scale = r.width() / br.width()

        if scale >= 1.0:
            painter.drawText(r, Qt.AlignCenter, label)
        else:
            font_height = br.height()
            box_height = r.height()

            painter.scale(scale, scale)
            br.translate(r.left() - br.left(), r.top() - br.top())
            br.translate(0.0, box_height * (0.5 / scale) - font_height / 2)
            painter.drawText(br, Qt.TextSingleLine, label)

        painter.restore()

    def add_link(self, to_box, from_side = st.right, to_side=st.left):
        #print "link"
        name = "%s_%s" % (self.box_name, to_box.box_name)
        self.links[name] = Link(self, to_box)
        self.links[name].from_box_side(from_side)
        self.links[name].to_box_side(to_side)
        self.update_links()
        self.scene().invalidate(self.scene().sceneRect())
        return self.links[name]

    def update_links(self):
        for link in self.links:
            if self.links[link].is_center_track():
                self.links[link].auto_update_center()

