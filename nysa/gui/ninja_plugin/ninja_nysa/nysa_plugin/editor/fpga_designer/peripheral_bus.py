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
from peripheral_slave import PeripheralSlave

from defines import PERIPHERAL_BUS_RECT
from defines import PERIPHERAL_BUS_POS
from defines import PERIPHERAL_BUS_COLOR
from defines import PERIPHERAL_BUS_ID

from defines import SLAVE_RECT
from defines import SLAVE_VERTICAL_SPACING
from defines import SLAVE_HORIZONTAL_SPACING

from defines import ARB_MASTER_EXPAND_OFFSET

from link import link_type as lt
from link import side_type as st

from graphics_scene import view_state

class PeripheralBus(Bus):
    """Host Interface Box"""

    def __init__(self,
                 scene,
                 master):


        super(PeripheralBus, self).__init__(position = PERIPHERAL_BUS_POS,
                                            scene = scene,
                                            name = "Peripherals",
                                            color = PERIPHERAL_BUS_COLOR,
                                            rect = PERIPHERAL_BUS_RECT,
                                            user_data = PERIPHERAL_BUS_ID,
                                            master = master,
                                            slave_class = PeripheralSlave)
        #Need a reference to a master to update the link if the peripheral bus
        #   grows
        self.prev_selected_slave = None
        self.scene().set_peripheral_bus(self)
        self.s = self.scene()
        self.dbg = False
        self.movable(False)

    def recalculate_size_pos(self):
        if self.dbg: print "PB: recalculate_size_pos"
        num_slaves = len(self.slaves)
        #the position of of the slaves are at the top left corner
        total_height = (num_slaves * SLAVE_RECT.height())

        y = PERIPHERAL_BUS_POS.y()

        if num_slaves > 0:
            total_height += ((num_slaves - 1) * SLAVE_VERTICAL_SPACING)

        #Adjust height and position of the memory bus
        if total_height > self.start_rect.height():
            #print "Old Height: %f, new height: %f" % (self.start_rect.height(), total_height)
            self.rect.setHeight(total_height)
            delta_y = total_height - self.start_rect.height()
            y = PERIPHERAL_BUS_POS.y() - delta_y
            #print "Changing position from %f to %f" % (self.pos().y(), y)
            self.setPos(QPointF(PERIPHERAL_BUS_POS.x(), y))

        #Calculate the position of each slave
        for i in range(len(self.slaves)):
            self.slaves[i].selectable(False)
            am = self.s.get_arbitor_master_selected()
            sm = None
            if am is not None:
                sm = am.get_slave()
            if self.expand_slaves and self.slaves[i] != sm and self.slaves[i].box_name != "DRT":
                x = PERIPHERAL_BUS_POS.x() + PERIPHERAL_BUS_RECT.width() + SLAVE_HORIZONTAL_SPACING + ARB_MASTER_EXPAND_OFFSET
            else:
                x = PERIPHERAL_BUS_POS.x() + PERIPHERAL_BUS_RECT.width() + SLAVE_HORIZONTAL_SPACING
            slave_y = y + i * (SLAVE_RECT.height() + SLAVE_VERTICAL_SPACING)
            self.slaves[i].setPos(QPointF(x, slave_y))
            self.slaves[i].selectable(True)

        self.update_links()
        self.update()

    def slave_selection_changed(self, slave):
        if slave == self.prev_selected_slave:
            return

        if self.prev_selected_slave is not None:
            #print "Slave ID: %s" % str(slave.user_data)
            if self.scene().is_arbitor_master_selected():
                return
            self.prev_selected_slave.remove_arbitor_masters()

        self.prev_selected_slave = slave

    def update_slaves(self, slave_list):

        if self.scene().is_arbitor_master_selected():
            am = self.scene().get_arbitor_master_selected()
            self.scene().arbitor_master_deselected(am)
            am.get_slave().remove_arbitor_masters()
            self.scene().clear_links()
 
        if self.prev_selected_slave is not None:

            self.prev_selected_slave.remove_arbitor_masters()
            self.prev_selected_slave = None

           #self.scene().arbitor_master_deselected(am) 
 
        super(PeripheralBus, self).update_slaves(slave_list)

    def enable_expand_slaves(self, arbitor_master, enable):
        super(PeripheralBus, self).enable_expand_slaves(arbitor_master, enable)

    def get_bus_type(self):
        return "peripheral_bus"

