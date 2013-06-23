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

from host_interface import HostInterface
from master import Master
from peripheral_bus import PeripheralBus
from memory_bus import MemoryBus
from peripheral_slave import PeripheralSlave
from memory_slave import MemorySlave

import fpga_designer





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
import wishbone_model

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
        m = Master(scene = self.canvas.scene())
        self.boxes["master"] = m

        self.output.Debug(self, "Add Host Interface")
        hi_name = self.model.get_host_interface_name()
        hi = HostInterface(self.canvas.scene(), 
                           hi_name)
        hi.link_master(m)
        self.boxes["host_interface"] = hi

        self.output.Debug(self, "Add Peripheral Bus")
        pb = PeripheralBus(self.canvas.scene(),
                           m)
        m.link_peripheral_bus(pb)
        self.boxes["peripheral_bus"] = pb


        self.output.Debug(self, "Add Memory Bus")
        mb = MemoryBus(self.canvas.scene(),
                       m)
        self.boxes["memory_bus"] = mb
        m.link_memory_bus(mb)
        self.refresh_slaves()


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

    def refresh_slaves(self):
        #Create a list of slaves to send to the bus
        slave_type = SlaveType.PERIPHERAL
        nslaves = self.model.get_number_of_slaves(slave_type)
        slave_list = []
        for i in range(nslaves):
            sitem = {}
            sitem["instance_name"] = self.model.get_slave_name(slave_type, i)
            sitem["parameters"] = self.model.get_slave_parameters(slave_type, i)
            slave_list.append(sitem)

        pb = self.boxes["peripheral_bus"]
        #update the bus
        print "WBC: updating slave view"
        pb.update_slaves(slave_list)



        slave_type = SlaveType.MEMORY
        nslaves = self.model.get_number_of_slaves(slave_type)
        slave_list = []
        for i in range(nslaves):
            sitem = {}
            sitem["instance_name"] = self.model.get_slave_name(slave_type, i)
            sitem["parameters"] = self.model.get_slave_parameters(slave_type, i)
            slave_list.append(sitem)

        mb = self.boxes["memory_bus"]
        #update the bus
        print "WBC: updating slave view"
        mb.update_slaves(slave_list)


    def add_slave(self, slave_dict, index):
        print "WBC: Adding slave"
        module_name = slave_dict["name"]
        slave_type = None
        if slave_dict["type"] == "peripheral_slave":
            slave_type = SlaveType.PERIPHERAL
        elif slave_dict["type"] == "memory_slave":
            slave_type = SlaveType.MEMORY

        if slave_type is None:
            raise fpga_deisgner.FPGADesignerError("Unrecognized slave type: %s" % slave_type)

        fn = utils.find_module_filename(module_name, self.fd.user_dirs)
        fn = utils.find_rtl_file_location(fn, self.fd.user_dirs)

        #Need to create a new name for the slave

        #start with the module name
        name = module_name

        print "WBC: Getting number of slaves"
        nslaves = self.model.get_number_of_slaves(slave_type)
        snames = []
        #Get all the slave names
        for i in range(nslaves):
            snames.append(self.model.get_slave_name(slave_type, i))

        unique = False
        append_num = 0
        temp_name = "%s_%d" % (name, append_num)

        while (temp_name in snames):
            append_num += append_num + 1
            temp_name = "%s_%d" % (name, append_num)

        name = temp_name
        try:
            self.model.add_slave(name, fn, slave_type, index)
        except ibuilder_error.SlaveError, err:
            #Can't a non DRT device to address 0 of the peripheral bus
            self.model.add_slave(name, fn, slave_type, 1)

        self.refresh_slaves()

    #def move_slave(self, slave_bus, from_index, to_index):
    #    print "Moving Slave"

    def find_slave_position(self, drop_position):
        self.output.Debug(self, "Looking for slave position")
        return drop_position


    def drop_event(self, event):
        print "VC: drop_event()"
        if event.mimeData().hasFormat("application/flowchart-data"):
            data = event.mimeData().data("application/flowchart-data")
            position = self.fd.position()

            #print "Data: %s" % str(data)
            d = json.loads(str(data))
            if "type" in d.keys():
                print "\ttype: %s" % d["type"]
                if d["type"] == "memory_slave" or d["type"] == "peripheral_slave":

                    if d["type"] == "peripheral_slave":
                        print "\tSearching peripheral bus"
                        pb = self.boxes["peripheral_bus"]
                        index = pb.find_index_from_position(position)
                        self.add_slave(d, index)

                    else:
                        mb = self.boxes["memory_bus"]
                        index = mb.find_index_from_position(position)
                        self.add_slave(d, index)
            event.accept()
        else:
            event.ignore()

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

