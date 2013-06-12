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
'''

__author__ = "Dave McCoy dave.mccoy@cospandesign.com"


from PyQt4.QtCore import *
from PyQt4.QtGui import *


def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

link_type = enum(   "wishbone_bus",
                    "axi_bus",
                    "host_interface",
                    "arbitor")

class Link (QGraphicsLineItem):

    def __init__(self, from_box, to_box, scene, color, ltype):
        super(Link, self).__init__(parent = None, scene = scene)
        self.from_box = from_box
        self.to_box = to_box
        self.setFlags
        self.setZValue(-1)
        self.setFlags(QGraphicsItem.ItemIsSelectable    |
                  QGraphicsItem.ItemIsFocusable)

        self.color = color
        self.link_type = ltype
        self.track_nodes()

    def track_nodes(self):
        x1 = 0.0
        y1 = 0.0
        x2 = 0.0
        y2 = 0.0
        x1 = self.from_box.pos().x()
        y1 = self.from_box.pos().y()
        x2 = self.to_box.pos().x()
        y2 = self.to_box.pos().y()
        self.setLine(x1, y1, x2, y2)


