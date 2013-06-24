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

from defines import MASTER_RECT
from defines import MASTER_POS
from defines import MASTER_COLOR
from defines import MASTER_ID

from link import Link
from link import link_type as lt
from link import side_type as st

from link import get_inverted_side

class Master(Box):
    """Host Interface Box"""

    def __init__(self,
                 scene):

        super(Master, self).__init__(position = MASTER_POS,
                                     scene = scene,
                                     name = "Master",
                                     color = MASTER_COLOR,
                                     rect = MASTER_RECT,
                                     user_data = MASTER_ID)
        self.peripheral_bus = None
        self.memory_bus = None
        self.scene().set_master(self)
        self.links = {}
        self.movable(False)

    def link_peripheral_bus(self, peripheral_bus):
        self.peripheral_bus = peripheral_bus
        self.links[peripheral_bus] = Link(self, peripheral_bus, self.scene(), lt.bus)
        self.links[peripheral_bus].from_box_side(st.right)
        self.links[peripheral_bus].to_box_side(st.left)

    def link_memory_bus(self, memory_bus):
        self.memory_bus = memory_bus
        self.links[memory_bus] = Link(self, memory_bus, self.scene(), lt.bus)
        self.links[memory_bus].from_box_side(st.right)
        self.links[memory_bus].to_box_side(st.left)

    def paint(self, painter, option, widget):
        super(Master, self).paint(painter, option, widget)
        self.update_master_links()

    def update_master_links(self):
        pbus_start = self.mapToScene(self.side_coordinates(st.right))
        pbus_start = QPointF(pbus_start.x(), pbus_start.y() - (self.rect.height() / 4))
        pbus_end = self.mapToScene(self.mapFromItem(self.peripheral_bus, self.peripheral_bus.side_coordinates(st.left)))
        link = self.links[self.peripheral_bus]
        link.set_start_end(pbus_start, pbus_end)

        mbus_start = self.mapToScene(self.side_coordinates(st.right))
        mbus_start = QPointF(pbus_start.x(), mbus_start.y() + (self.rect.height() / 4))
        mbus_end = self.mapToScene(self.mapFromItem(self.memory_bus, self.memory_bus.side_coordinates(st.left)))

        link = self.links[self.memory_bus]
        link.set_start_end(mbus_start, mbus_end)


