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
  6/17/2013: Initial commit
'''

import os
import sys
from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4 import QtCore
from PyQt4.QtGui import *

from box import Box

from graphics_scene import view_state as vs


from link import side_type as st
from link import link_type as lt
from link import Link



from defines import ARB_MASTER_RECT
from defines import ARB_MASTER_COLOR

from defines import ARB_MASTER_RECT
from defines import ARB_MASTER_COLOR

from defines import ARB_MASTER_ACT_RECT
from defines import ARB_MASTER_ACT_COLOR

highlight_width = 8

class ArbitorMaster(Box):
    """Host Interface Box"""

    def __init__(self,
                 name,
                 position,
                 scene,
                 slave):

        QGraphicsItem.__init__(self)

        self.box_name = name
        self.color = ARB_MASTER_COLOR
        self.activate = False
        self.user_data = "arbitor_master"
        self.rect = QRectF(ARB_MASTER_RECT)
        self.start_rect = QRectF(self.rect)
        self.s = scene


        self.link = None
        self.slave = slave

        #UI Stuff
        global Dirty
        Dirty = True

        #User cannot move us directly
        self.setFlags(QGraphicsItem.ItemIsSelectable    |
                      QGraphicsItem.ItemIsFocusable)
        scene.addItem(self)

        self.connected_slave = None
        #Tooltip
        self.setToolTip(
          "Name: %s" % self.box_name
        )

        #Drawing components
        self.setMatrix(QMatrix())

        self.style = Qt.SolidLine
        self.setPos(position)
        #Font
        self.text_font = QFont('White Rabbit')
        self.text_font.setPointSize(16)


        #Setup the drawing rectangles

        self.label_rect = QRectF(ARB_MASTER_ACT_RECT)
        self.label_rect.setHeight(self.label_rect.height() / 2)

        self.back_rect = QRectF(ARB_MASTER_ACT_RECT)
        self.back_rect.setX(self.label_rect.left())
        self.back_rect.setY(self.label_rect.bottom())

        self.back_rect.setHeight(ARB_MASTER_ACT_RECT.height() / 2)
        self.back_rect.setWidth(ARB_MASTER_ACT_RECT.width() / 2)

        self.disconnect_rect = QRectF(ARB_MASTER_ACT_RECT)
        self.disconnect_rect.setX(self.back_rect.right())
        self.disconnect_rect.setY(self.back_rect.top())

        self.disconnect_rect.setHeight(ARB_MASTER_ACT_RECT.height() / 2)
        self.disconnect_rect.setWidth(ARB_MASTER_ACT_RECT.height() / 2)


    def set_activate(self, enable):
        self.activate = enable
        if self.activate:
            print "AM: Activate"
            if self.connected_slave is not None:
                self.setToolTip(
                    "Select a slave to bind to a this master\n" + \
                    "Back: to choose a different arbitor master\n"
                    "Disconnect: disconnect the current slave"
                )
            else:
                self.setToolTip(
                    "Select a slave to bind to a this master\n" + \
                    "Back: to choose a different arbitor master"
                )

            self.rect = QRectF(ARB_MASTER_ACT_RECT)
            self.color = ARB_MASTER_ACT_COLOR
        else:
            print "AM: Deactivate"
            self.rect = QRectF(ARB_MASTER_RECT)
            self.color = ARB_MASTER_COLOR

        self.start_rect = self.rect

    def mousePressEvent(self, event):
        print "AM: Mouse Press Event"
        if self.s.get_state() == vs.arbitor_master_selected:
            if self.back_rect.contains(event.pos()):
                self.clear_link()
                self.s.arbitor_master_deselected(self.slave, self)
            elif self.disconnect_rect.contains(event.pos()) and self.connected_slave is not None:
                self.clear_link()
                self.s.arbitor_master_disconnect(self, self.connected_slave)
        else:
            self.s.arbitor_master_selected(self.slave, self)
            self.setSelected(True)
        return QGraphicsItem.mousePressEvent(self, event)


    def connect_slave(self, slave):
        print "AM: connect slave"
        self.connected_slave = slave
        print "AM: Connected to slave: %s" % slave.box_name

        if self.link is None:
            self.link = Link(self, slave, self.s, lt.arbitor_master)
            self.s.set_link_ref(self.link)
            self.link.from_box_side(st.right)
            self.link.to_box_side(st.left)
            self.link.en_bezier_connections(True)
            #self.s.addItem(self.link)
            self.update_link()

        self.update(self.rect)

    def clear_link(self):
        print "AM: Clear Link"
        if self.link is not None:
            print "\tAM: Link to Remove"
            self.s.removeItem(self.link)

    def disconnect_slave(self):
        print "AM: disconnect slave"
        self.connected_slave = None
        if self.link is None:
            return
        self.s.removeItem(self.link)
        self.link = None

    def update_link(self):
        if self.link is None:
            return
        #print "AM: update links: %s" % self.box_name
        pos = self.pos()
        x = ARB_MASTER_ACT_RECT.width()
        y = ARB_MASTER_ACT_RECT.height() / 2 - pos.y()
        #The added pos.y() is the offset, we need to remove it it should be zero

        p = QPointF(x, y)
        #print "AM: Connectio Position: %f, %f" % (p.x(), p.y())
        x = ARB_MASTER_ACT_RECT.width()
        start = self.mapToScene(p)
        to_box = self.link.to_box
        end = self.mapToScene(self.mapFromItem(to_box, to_box.side_coordinates(st.left)))
        self.link.set_start_end(start, end)

    #Paint
    def paint(self, painter, option, widget):
        if self.activate:
            self.paint_selected(painter, option, widget)
        else:
            self.paint_not_selected(painter, option, widget)

    def paint_selected(self, painter, option, widget):
        m = QMatrix(painter.matrix())
        #painter.save()
        pen = QPen(self.style)
        pen.setColor(Qt.black)
        pen.setWidth(1)
        if option.state & QStyle.State_Selected:
            #Selected
            pen.setColor(QColor("black"))
            pen.setWidth(highlight_width)


        painter.setPen(pen)
        #Draw all the boxes
        painter.drawRect(self.rect)
        
        painter.fillRect(self.rect, QColor(self.color))
        #print "AM: Paint: Rectangle: %f, %f, %f, %f" % (self.rect.left(), self.rect.top(), self.rect.right(), self.rect.bottom())

        painter.drawRect(self.label_rect)
        painter.fillRect(self.label_rect, QColor(self.color))
        painter.drawRect(self.back_rect)
        painter.fillRect(self.back_rect, QColor("white"))
        painter.setFont(self.text_font)

        #draw text
        pen.setColor(Qt.black)
        painter.setPen(pen)
        r = QRectF(self.label_rect)
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
            br.translate(0.0, box_height * (0.5 / scale_x) - font_height / 2)
            painter.drawText(br, Qt.TextSingleLine, self.box_name)

        #draw back
        pen.setColor(Qt.black)
        painter.setPen(pen)
        r = QRectF(self.back_rect)
        br = painter.fontMetrics().boundingRect("back")

        scale_x = r.width() / br.width()

        if scale_x > 1.0:
            painter.drawText(r, Qt.AlignCenter, "back")
        else:
            #For the cases where the text is larger than th box

            font_height = br.height()
            box_height = r.height()

            painter.scale(scale_x, scale_x)
            br.translate(r.left() - br.left(), r.top() - br.top())
            br.translate(0.0, box_height * (0.5 / scale_x) - font_height / 2)
            painter.drawText(br, Qt.TextSingleLine, "back")


        #draw disconnect
        if self.connected_slave is not None:
            painter.drawRect(self.disconnect_rect)
            painter.fillRect(self.disconnect_rect, QColor("red"))


            pen.setColor(Qt.black)
            painter.setPen(pen)
            r = QRectF(self.disconnect_rect)
            br = painter.fontMetrics().boundingRect("disconnect")

            scale_x = r.width() / br.width()
            painter.scale(1.0, 1.0)

            #painter.resetTransform()
            #pos = self.mapToScene(self.pos())
            #painter.translate(pos.x(), pos.y())
            #painter.setMatrix(QMatrix(m))
            if scale_x > 1.0:
                painter.drawText(r, Qt.AlignCenter, "disconnect")
            else:
                #For the cases where the text is larger than th box
                pos = self.mapToScene(self.pos())
                font_height = br.height()
                box_height = r.height()
                w = br.width()
                h = br.height()
                pen.setColor(QColor("blue"))
                br.translate(0 - br.left(), 0 - br.top())
                painter.translate(r.left(), r.top())
                br.translate(0.0, box_height * (0.5 / scale_x) - font_height / 2)
                painter.scale(scale_x, scale_x)
                painter.drawText(br, Qt.TextSingleLine, "disconnect")

        #painter.setMatrix(m)
        #painter.restore()
        #print "AM: End Paint Position: %f, %f" % (self.pos().x(), self.pos().y())
        #painter.resetTransform()
        #print "AM: End Paint Position reset transfrom: %f, %f" % (self.pos().x(), self.pos().y())

    def paint_not_selected(self, painter, option, widget):

        pen = QPen(self.style)
        pen.setColor(Qt.black)
        pen.setWidth(1)
        if option.state & QStyle.State_Selected:
            #Selected
            pen.setColor(QColor("black"))
            pen.setWidth(highlight_width)

        painter.setPen(pen)
        #Draw all the boxes
        painter.drawRect(self.rect)
        painter.fillRect(self.rect, QColor(self.color))


        pen.setColor(Qt.black)
        painter.setPen(pen)
        r = QRectF(self.rect)
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
            br.translate(0.0, box_height * (0.5 / scale_x) - font_height / 2)
            painter.drawText(br, Qt.TextSingleLine, self.box_name)


    def get_connected_slave(self):
        return self.connected_slave

    def get_slave(self):
        return self.slave
