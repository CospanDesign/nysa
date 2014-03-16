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
import copy


from PyQt4.QtCore import *
from PyQt4.QtGui import *

import controller


from defines import PS_COLOR
from defines import MS_COLOR

from host_interface import HostInterface
from master import Master
from peripheral_bus import PeripheralBus
from memory_bus import MemoryBus
from peripheral_slave import PeripheralSlave
from memory_slave import MemorySlave

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             "common"))

from status import Status

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
import utils
import wishbone_utils
import ibuilder_error

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


from graph_manager import NodeType
from graph_manager import SlaveType
from .wishbone_model import WishboneModel

class WishboneController (controller.Controller):

    def __init__(self, config_dict, scene, debug = False):
        self.status = Status()
        self.dbg = debug
        self.model = WishboneModel(config_dict)
        self.scene = scene

        super(WishboneController, self).__init__(self.model)
        self.status.Debug(self, "Wishbone controller started")
        self.bus = "wishbone"
        if "INTERFACE" not in config_dict.keys():
            self.model.set_default_board_project(config_dict["board"])
        else:
            self.model.load_config_dict(config_dict)
        #self.model.initialize_graph(debug = True)
        self.model.initialize_graph(debug = False)
        #self.initialize_view()

    def initialize_view(self):
        self.status.Debug(self, "Add Master")
        m = Master(scene = self.scene)
        self.boxes["master"] = m

        self.status.Debug(self, "Add Host Interface")
        hi_name = self.model.get_host_interface_name()
        hi = HostInterface(self.scene,
                           hi_name)
        hi.link_master(m)
        self.boxes["host_interface"] = hi

        self.status.Debug(self, "Add Peripheral Bus")
        pb = PeripheralBus(self.scene,
                           m)
        m.link_peripheral_bus(pb)
        self.boxes["peripheral_bus"] = pb

        self.status.Debug(self, "Add Memory Bus")
        mb = MemoryBus(self.scene,
                       m)
        self.boxes["memory_bus"] = mb
        m.link_memory_bus(mb)
        self.refresh_slaves()

    def add_arbitor_link(self, arb_master, slave):
        self.add_link(arb_master, slave, lt.arbitor, st.right)

    def refresh_slaves(self):
        if self.dbg: print "WBC: refresh_slaves"
        #Create a list of slaves to send to the bus
        slave_type = SlaveType.PERIPHERAL
        nslaves = self.model.get_number_of_slaves(slave_type)
        slave_list = []
        for i in range(nslaves):
            sitem = {}
            sitem["instance_name"] = self.model.get_slave_name(slave_type, i)
            slave_list.append(sitem)

        pb = self.boxes["peripheral_bus"]
        #update the bus
        if self.dbg: print "\tupdating slave view"
        pb.update_slaves(slave_list)

        slave_type = SlaveType.MEMORY
        nslaves = self.model.get_number_of_slaves(slave_type)
        slave_list = []
        for i in range(nslaves):
            sitem = {}
            sitem["instance_name"] = self.model.get_slave_name(slave_type, i)
            slave_list.append(sitem)

        mb = self.boxes["memory_bus"]
        #update the bus
        if self.dbg: print "WBC: updating slave view"
        mb.update_slaves(slave_list)

    def connect_arbitor_master(self, from_type, from_index, arbitor_name, to_type, to_index):
        if from_type == SlaveType.PERIPHERAL and from_index == 0:
            raise DesignControlError("DRT cannot be a Arbitor slave")
        self.model.add_arbitor(from_type, from_index, arbitor_name, to_type, to_index)

    def disconnect_arbitor_master(self, from_type, from_index, arbitor_name, to_type, to_index):
        self.model.remove_arbitor(from_type, from_index, to_type, to_index)

    def get_arbitor_master_connected(self, host_type, host_index, arbitor_name):
        name = self.model.get_slave_name(host_type, host_index)
        #print "WBC: get_arbitor_master_connected name: %s" % name
        uname = self.model.get_unique_name(name = name,
                                           node_type = NodeType.SLAVE,
                                           slave_type = host_type,
                                           slave_index = host_index)
        #print "WBC: unique name: %s" % uname
        uname = self.model.get_connected_arbitor_slave(uname, arbitor_name)
        if uname is None:
            return None, None

        s = self.model.get_graph_manager().get_node(uname)
        return s.slave_type, s.slave_index

    def get_project_name(self):
        return self.model.get_project_name()

