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

link_type = enum(   "bus",
                    "host_interface",
                    "arbitor",
                    "port")


side_type = enum(   "top",
                    "bottom",
                    "right",
                    "left")


from defines import LINK_ARBITOR_COLOR
from defines import LINK_BUS_COLOR
from defines import LINK_HOST_INTERFACE_COLOR
from defines import LINK_PORT_COLOR
from defines import LINK_MASTER_COLOR


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

    def __init__(self, from_box, to_box, scene, ltype):
        super(Link, self).__init__(parent = None, scene = scene)
        self.rect = QRectF(0, 0, 0, 0)
        self.from_box = from_box
        self.to_box = to_box
        self.setFlags
        self.setZValue(-1)
        self.scene = scene
        self.scene.addItem(self)
        #self.setFlags(QGraphicsItem.ItemIsSelectable    |
        #          QGraphicsItem.ItemIsFocusable)
        self.link_type = ltype
        self.from_side = side_type.right
        self.to_side = side_type.left

        style = Qt.SolidLine
        pen = QPen(style)
        pen.setColor(get_color_from_type(ltype))
        self.pen = pen
        self.path = QPainterPath()
        self.track_nodes()



    def from_box_side(self, side):
        self.from_side = side

    def to_box_side(self, side):
        self.to_side = side

    def track_nodes(self):
        self.update()

    def update(self):
        self.prepareGeometryChange()

        self.start = self.mapFromItem(self.from_box, self.from_box.side_coordinates(self.from_side))
        self.end = self.mapFromItem(self.to_box, self.from_box.side_coordinates(self.to_side))

        self.start_offset = QLineF(self.start, QPointF(self.start.x() + 15, self.start.y()))
        self.end_offset = QLineF(self.end, QPointF(self.end.x() - 15, self.end.y()))

        self.line = QLineF(self.start, self.end)

        #self.setPos(px1, py1)

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


    def paint(self, painter, option, widget):
        center_point = QLineF(self.start, self.end).pointAt(0.5)

        pen = self.pen
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setWidth(4)
        if self.link_type == link_type.bus:
            pen.setWidth(4)
        if self.link_type == link_type.host_interface:
            pen.setWidth(8)
        if self.link_type == link_type.arbitor:
            pen.setWidth(4)
        if self.link_type == link_type.port:
            pen.setWidth(4)
        painter.setPen(pen)

        path = QPainterPath()
        
        pstart = self.start_offset.p1()
        pend = self.end_offset.p1()

        one = (QPointF(pend.x(), pstart.y()) + pstart) / 2
        two = (QPointF(pstart.x(), pend.y()) + pend) / 2


        path.moveTo(pstart)

        if (pstart.x() + padding) < pend.x():
            path.lineTo(one)
            path.lineTo(two)
            path.lineTo(pend)

        else:
            start_pad = QPointF(pstart.x() + padding, pstart.y())
            end_pad = QPointF(pend.x() - padding, pend.y())
            center = QLineF(pstart, pend).pointAt(0.5)
            one = (QPointF(start_pad.x(), center.y()))
            two = (QPointF(end_pad.x(), center.y()))


            path.lineTo(start_pad)
            path.lineTo(one)
            path.lineTo(two)
            path.lineTo(end_pad)
            path.lineTo(pend)



        '''
        if pstart.x() > pend.x():
            dist = (pstart.x() - pend.x()) * 2
            tLine = QLineF((dist / 2), 0.0, -(dist / 2), 0.0).translated(QLineF(pstart, pend).pointAt(0.5))
            one = tLine.p1()
            two = tLine.p2()
        '''



        #path.cubicTo(one, two, pend)

        #painter.drawRect(self.rect)
        #painter.drawText(self.rect, Qt.AlignCenter, "%s,%s" % (str(start.x()), str(start.y())))
        self.path = path
        painter.drawPath(path)





def get_color_from_type(lt):
    if lt == link_type.bus:
        return LINK_BUS_COLOR
    elif lt == link_type.host_interface:
        return LINK_HOST_INTERFACE_COLOR
    elif lt == link_type.arbitor:
        return LINK_ARBITOR_COLOR
    elif lt == link_type.port:
        return LINK_PORT_COLOR
    raise BoxLinkError("Invalid or undefined link type: %s, valid options \
            are: %s" % (str(lt), str(link_type)))

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
