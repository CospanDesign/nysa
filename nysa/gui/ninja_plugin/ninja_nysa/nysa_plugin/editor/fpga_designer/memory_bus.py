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

from bus import Bus
from memory_slave import MemorySlave

from defines import MEMORY_BUS_RECT
from defines import MEMORY_BUS_POS
from defines import MEMORY_BUS_COLOR
from defines import MEMORY_BUS_ID

from defines import ARB_MASTER_EXPAND_OFFSET

from defines import SLAVE_RECT
from defines import SLAVE_VERTICAL_SPACING
from defines import SLAVE_HORIZONTAL_SPACING

class MemoryBus(Bus):
    """Host Interface Box"""

    def __init__(self,
                 scene,
                 master):


        super(MemoryBus, self).__init__(position = MEMORY_BUS_POS,
                                            scene = scene,
                                            name = "Memory",
                                            color = MEMORY_BUS_COLOR,
                                            rect = MEMORY_BUS_RECT,
                                            user_data = MEMORY_BUS_ID,
                                            master = master,
                                            slave_class = MemorySlave)
        #Need a reference to a master to update the link if the memory bus
        #   grows
        self.scene().set_memory_bus(self)
        self.movable(False)


    def recalculate_size_pos(self):
        num_slaves = len(self.slaves)
        #the position of of the slaves are at the top left corner
        total_height = (num_slaves * SLAVE_RECT.height())
        if num_slaves > 0:
            total_height += ((num_slaves - 1) * SLAVE_VERTICAL_SPACING)

        #Adjust height and position of the peripheral bus
        if total_height > self.start_rect.height():
            #Adjust the bus's current position and resize
            self.rect.setHeight(total_height)
            #Add 1/2 of the difference of the new height and the original height to original y

        #Calculate the position of each slave
        for i in range(len(self.slaves)):
            self.slaves[i].selectable(False)
            if self.expand_slaves:
                x = MEMORY_BUS_POS.x() + MEMORY_BUS_RECT.width() + SLAVE_HORIZONTAL_SPACING + ARB_MASTER_EXPAND_OFFSET
            else:
                x = MEMORY_BUS_POS.x() + MEMORY_BUS_RECT.width() + SLAVE_HORIZONTAL_SPACING
            y = MEMORY_BUS_POS.y() + i * (SLAVE_RECT.height() + SLAVE_VERTICAL_SPACING)
            self.slaves[i].setPos(QPointF(x, y))
            self.slaves[i].selectable(True)

        self.update_links()
        self.update()
        #print "Position: %f, %f" % (self.pos().x(), self.pos().y())

    def get_bus_type(self):
        return "memory_bus"

