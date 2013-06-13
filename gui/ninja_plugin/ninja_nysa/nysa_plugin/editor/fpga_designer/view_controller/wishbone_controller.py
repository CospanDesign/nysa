# -*- coding: utf-8 -*-

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
  6/10/2013: Initial commit
'''



import os
import sys
import json


from PyQt4.QtCore import *
from PyQt4.QtGui import *

import controller

sys.path.append(os.path.join( os.path.dirname(__file__),
                              os.pardir))

from link import link_type as lt

sys.path.append(os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "ibuilder",
                              "lib"))

sys.path.append(os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "ibuilder",
                              "gui"))


sys.path.append(os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "cbuilder",
                              "drt"))


import wishbone_model
import utils

from controller import BoxType

from view_defines import HOST_INTERFACE_SIZE
from view_defines import HOST_INTERFACE_POS
from view_defines import HOST_INTERFACE_COLOR

from view_defines import MASTER_SIZE
from view_defines import MASTER_POS
from view_defines import MASTER_COLOR

from view_defines import PBUS_SIZE
from view_defines import PBUS_POS
from view_defines import PBUS_COLOR

from view_defines import MBUS_SIZE
from view_defines import MBUS_POS
from view_defines import MBUS_COLOR

class WishboneController (controller.Controller):

    def __init__(self, fpga_designer, canvas, output, config_dict):
        self.model = wishbone_model.WishboneModel()
        super(WishboneController, self).__init__(fpga_designer, self.model, canvas, output)
        self.output.Debug(self, "Wishbone controller started")
        self.bus = "wishbone"
        if "INTERFACE" not in config_dict.keys():
            self.model.set_default_board_project(config_dict["board"])
        else:
            self.model.load_config_dict(config_dict)
        self.model.initialize_graph()

        self.initialize_view()

    def initialize_view(self):
        self.output.Debug(self, "Add Master")
        m = self.add_box(box_type = BoxType.MASTER,
                         color = MASTER_COLOR,
                         name = "Master",
                         ID = "master",
                         position = QPointF(MASTER_POS[0], MASTER_POS[1]))
        m.set_size(MASTER_SIZE[0], MASTER_SIZE[1])
        self.boxes["master"] = m

        self.output.Debug(self, "Add Host Interface")
        hi_name = self.model.get_host_interface_name()
        hi = self.add_box(box_type = BoxType.HOST_INTERFACE,
                         color = HOST_INTERFACE_COLOR,
                         name = hi_name,
                         ID = "host_interface",
                         position = QPointF(HOST_INTERFACE_POS[0], HOST_INTERFACE_POS[1]))

        hi.set_size(HOST_INTERFACE_SIZE[0], HOST_INTERFACE_SIZE[1])
        self.boxes["host_interface"] = hi


        self.output.Debug(self, "Add Peripheral Bus")
        pb = self.add_box(box_type = BoxType.PERIPHERAL_INTERCONNECT,
                         color = PBUS_COLOR,
                         name = "Peripheral Bus",
                         ID = "peripheral_bus",
                         position = QPointF(PBUS_POS[0], PBUS_POS[1]))
        pb.set_size(PBUS_SIZE[0], PBUS_SIZE[1])
        self.boxes["peripheral_bus"] = pb

        self.output.Debug(self, "Add Memory Bus")
        mb = self.add_box(box_type = BoxType.MEMORY_INTERCONNECT,
                         color = MBUS_COLOR,
                         name = "Memory Bus",
                         ID = "memory_bus",
                         position = QPointF(MBUS_POS[0], MBUS_POS[1]))
        mb.set_size(MBUS_SIZE[0], MBUS_SIZE[1])
        self.boxes["memory_bus"] = mb

        self.add_host_interface_link(hi, m)
        self.add_bus_link(m, pb)
        self.add_bus_link(m, mb)

    def add_arbitor_link(self, arb_master, slave):
        self.add_link(arb_master, slave, lt.arbitor, st.right) 

    def drag_enter(self, event):
        """
        An item has entered the canvas
        """
        #Check to see if this is a box
        if event.mimeData().hasFormat("application/flowchart-data"):
            self.output.Debug(self, "Detect box")
            event.accept()
        else:
            event.ignore()

    def drag_move(self, event):
        if event.mimeData().hasFormat("application/flowchart-data"):
            #print "Good"
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

        #check if this is a slave
        #if this is a slave check if it is a memory
        #if this is a slave, or memory make sure it's in the correct area

    def drop_event(self, event):
        if event.mimeData().hasFormat("application/flowchart-data"):
            data = event.mimeData().data("application/flowchart-data")
            #print "Data: %s" % str(data)
            d = json.loads(str(data))
            #print "view drop event"
            self.add_box(d["name"], d["color"])
            event.accept()
        else:
            event.ignore()


