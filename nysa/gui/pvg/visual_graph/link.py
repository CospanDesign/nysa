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

#Thanks to http://github.com/woopeex edd repository... I love his picture too

'''
Log
  6/05/2013: Initial commit
'''

__author__ = "Dave McCoy dave.mccoy@cospandesign.com"


from PyQt4.QtCore import *
from PyQt4.QtGui import *


def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

side_type = enum(   "top",
                    "bottom",
                    "right",
                    "left")

from defines import BEZIER_CONNECTION
from defines import LINK_DEMO_COLOR

padding = 20


class BoxLinkError(Exception):
    """
    Errors associated with Links between boxes

    Error associated with:
        -invalid side
        -invalid link type
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class Link (QGraphicsItem):

    def __init__(self, from_box, to_box):
        super(Link, self).__init__(parent = None, scene = from_box.scene())
        self.rect = QRectF(0, 0, 0, 0)
        self.from_box = from_box
        self.to_box = to_box
        self.scene().set_link_ref(self)
        self.setFlags
        self.setZValue(-1)
        #self.setFlags(QGraphicsItem.ItemIsSelectable    |
        #          QGraphicsItem.ItemIsFocusable)
        self.from_side = side_type.right
        self.to_side = side_type.left

        style = Qt.SolidLine
        pen = QPen(style)
        pen.setColor(QColor("black"))
        self.pen = pen
        self.path = QPainterPath()
        self.track_nodes()
        self.bezier_en = BEZIER_CONNECTION
        self.start = QPointF(0.0, 0.0)
        self.end = QPointF(0.0, 0.0)
        self.start_offset = QLineF(0.0, 0.0, 0.0, 0.0)
        self.end_offset = QLineF(0.0, 0.0, 0.0, 0.0)
        self.line = QLineF(self.start, self.end)
        self.dbg = False
        self.center_track = True
        self.directed = False
        self.padding = padding

    def en_center_track(self, enable):
        self.center_track = True

    def set_padding(self, p = 20):
        self.padding = padding

    def is_center_track(self):
        return self.center_track

    def en_bezier_connections(self, enable):
        if self.dbg: print "Enable Bezier Connections: %s" % str(enable)
        self.bezier_en = enable

    def bezier_connections(self):
        return self.bezier_en

    def from_box_side(self, side):
        self.from_side = side

    def to_box_side(self, side):
        self.to_side = side

    def set_directed(self, enable):
        self.directed = enable

    def track_nodes(self):
        self.update()

    def get_min_max_to(self):
        return self.end_offset.y()

    def set_start_end(self, start, end):
        self.prepareGeometryChange()

        self.start = start
        self.end = end

        s_offset_point = QPointF(self.start.x() + 15, self.start.y())
        e_offset_point = QPointF(self.end.x() - 15, self.end.y())
        

        self.start_offset = QLineF(self.start, s_offset_point)
        self.end_offset = QLineF(self.end, e_offset_point)

        self.line = QLineF(self.start, self.end)

    def auto_update_center(self):
        #print "Auto update!"
        self.prepareGeometryChange()

        self.start = self.mapFromItem(self.from_box, self.from_box.side_coordinates(self.from_side))
        self.end = self.mapFromItem(self.to_box, self.from_box.side_coordinates(self.to_side))


        self.start_offset = QLineF(self.start, QPointF(self.start.x() + 15, self.start.y()))
        self.end_offset = QLineF(self.end, QPointF(self.end.x() - 15, self.end.y()))

        self.line = QLineF(self.start, self.end)


    def boundingRect(self):
        extra = (self.pen.width() * 64) / 2
        return QRectF(self.line.p1(),
                QSizeF( self.line.p2().x() - self.line.p1().x(),
                        self.line.p2().y() - self.line.p1().y())).normalized().adjusted(-extra, 
                                                                                        -extra, 
                                                                                        extra, 
                                                                                        extra)

    def shape(self):
        return QPainterPath(self.path)

    def paint_direct_connect(self, painter, width, color):
        center_point = QLineF(self.start, self.end).pointAt(0.5)
        pen = self.pen
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setColor(color)
        pen.setWidth(width)
        painter.setPen(pen)

        path = QPainterPath()

        pstart = self.start_offset.p1()
        pend = self.end_offset.p1()

        pstart = QPointF(pstart.x(), pend.y())
        path.moveTo(pstart)
        path.lineTo(pend)

        self.path = path
        painter.drawPath(path)
        if self.directed:

            height = 2 * pen.width()
            pa = None
            pb = None
            if self.to_side == side_type.left:
                pa = QPointF(end_pad.x(), end_pad.y() + (height / 2))
                pb = QPointF(end_pad.x(), end_pad.y() - (height / 2))
            if self.to_side == side_type.right:
                pa = QPointF(end_pad.x(), end_pad.y() + (height / 2))
                pb = QPointF(end_pad.x(), end_pad.y() - (height / 2))
         
            if self.to_side == side_type.top:
                pa = QPointF(end_pad.x() + height / 2, end_pad.y())
                pb = QPointF(end_pad.x() - height / 2, end_pad.y())
         
            if self.to_side == side_type.bottom:
                pa = QPointF(end_pad.x() + height / 2, end_pad.y())
                pb = QPointF(end_pad.x() - height / 2, end_pad.y())
         
            arrow_head = QPolygonF([pa, pb, pend])
            painter.drawPolygon(arrow_head)



    def paint_normal_connect(self, painter, width, color):
        center_point = QLineF(self.start, self.end).pointAt(0.5)
        pen = self.pen
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setColor(color)
        pen.setWidth(width)
        painter.setPen(pen)

        path = QPainterPath()

        pstart = self.start_offset.p1()
        pend = self.end_offset.p1()

        start_pad = QPointF(pstart.x() + self.padding, pstart.y())
        end_pad = QPointF(pend.x() -  self.padding, pend.y())
        center = QLineF(pstart, pend).pointAt(0.5)

        one = (QPointF(pend.x(), pstart.y()) + pstart) / 2
        two = (QPointF(pstart.x(), pend.y()) + pend) / 2
                                
        path.moveTo(pstart)

        if self.bezier_en:
            path.cubicTo(one, two, pend)

        else:
            if (pstart.x() + self.padding) < pend.x():
                path.lineTo(one)
                path.lineTo(two)
                path.lineTo(pend)
            
            else:
                start_pad = 0
                end_pad = 0
                if self.from_side == side_type.left:
                    start_pad = QPointF(pstart.x() - self.padding, pstart.y())
                if self.from_side == side_type.right:
                    start_pad = QPointF(pstart.x() + self.padding, pstart.y())
                if self.from_side == side_type.top:
                    start_pad = QPointF(pstart.x(), pstart.y() - self.padding)
                if self.from_side == side_type.bottom:
                    start_pad = QPointF(pstart.x(), pstart.y() + self.padding)


                if self.to_side == side_type.left:
                    end_pad = QPointF(pend.x() - self.padding, pend.y())
                if self.to_side == side_type.right:
                    end_pad = QPointF(pend.x() + self.padding, pend.y())
                if self.to_side == side_type.top:
                    end_pad = QPointF(pend.x(), pend.y() - self.padding)
                if self.to_side == side_type.bottom:
                    end_pad = QPointF(pend.x(), pend.y() + self.padding)


                center = QLineF(pstart, pend).pointAt(0.5)
                one = (QPointF(start_pad.x(), center.y()))
                two = (QPointF(end_pad.x(), center.y()))
                path.lineTo(start_pad)
                path.lineTo(one)
                path.lineTo(two)
                path.lineTo(end_pad)
                path.lineTo(pend)

        self.path = path
        painter.drawPath(path)
        if self.directed:

            height = 2 * pen.width()
            pa = None
            pb = None
            if self.to_side == side_type.left:
                pa = QPointF(end_pad.x(), end_pad.y() + (height / 2))
                pb = QPointF(end_pad.x(), end_pad.y() - (height / 2))
            if self.to_side == side_type.right:
                pa = QPointF(end_pad.x(), end_pad.y() + (height / 2))
                pb = QPointF(end_pad.x(), end_pad.y() - (height / 2))
         
            if self.to_side == side_type.top:
                pa = QPointF(end_pad.x() + height / 2, end_pad.y())
                pb = QPointF(end_pad.x() - height / 2, end_pad.y())
         
            if self.to_side == side_type.bottom:
                pa = QPointF(end_pad.x() + height / 2, end_pad.y())
                pb = QPointF(end_pad.x() - height / 2, end_pad.y())
         
            arrow_head = QPolygonF([pa, pb, pend])
            painter.drawPolygon(arrow_head)


    def paint(self, painter, option, widget):
        self.paint_normal_connect(painter, 4, LINK_DEMO_COLOR)
        #self.paint_direct_connect(painter, 4, LINK_DEMO_COLOR)

def get_inverted_side(side):
    if side == side_type.top:
        return side_type.bottom
    if side == side_type.bottom:
        return side_type.top
    if side == side_type.right:
        return side_type.left
    if side == side_type.left:
        return side_type.right
    #This should be an error
    raise BoxLinkError("Invalid side: %s" % str(side))
