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


#epath = os.path.abspath(os.path.join(os.path.dirname(__file__),
#                                     os.pardir,
#                                     os.pardir,
#                                     os.pardir,
#                                     "editor",
#                                     "fpga_designer"))
#print "epath %s" % epath

sys.path.append(os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "editor",
                              "fpga_designer"))

from defines import PS_COLOR
from defines import MS_COLOR

from host_interface import HostInterface
from master import Master
from peripheral_bus import PeripheralBus
from memory_bus import MemoryBus
from peripheral_slave import PeripheralSlave
from memory_slave import MemorySlave
from constraint_editor_box import ConstraintEditorBox


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
import constraint_utils as cu

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

    def __init__(self, output, config_dict):
        self.dbg = False
        self.model = wishbone_model.WishboneModel()
        super(WishboneController, self).__init__(self.model, output)
        self.output.Debug(self, "Wishbone controller started")
        self.bus = "wishbone"
        if "INTERFACE" not in config_dict.keys():
            self.model.set_default_board_project(config_dict["board"])
        else:
            self.model.load_config_dict(config_dict)
        self.model.initialize_graph()
        #self.initialize_view()

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

        #Add the constraint editor box
        self.output.Debug(self, "Add Constraint Editor")
        ceb = ConstraintEditorBox(self.canvas.scene())
        self.boxes["constraint_editor"] = ceb

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
            #event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
        #check if this is a slave
        #if this is a slave check if it is a memory
        #if this is a slave, or memory make sure it's in the correct area

    def refresh_slaves(self):
        if self.dbg: print "WBC: refresh_slaves"
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
        if self.dbg: print "\tupdating slave view"
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
        if self.dbg: print "WBC: updating slave view"
        mb.update_slaves(slave_list)


    def get_project_name(self):
        return self.model.get_project_name()

    def add_slave(self, slave_dict, index):
        if self.dbg: print "WBC: Adding slave"
        module_name = slave_dict["name"]
        slave_type = None
        if slave_dict["type"] == "peripheral_slave":
            slave_type = SlaveType.PERIPHERAL
        elif slave_dict["type"] == "memory_slave":
            slave_type = SlaveType.MEMORY

        if slave_type is None:
            raise fpga_deisgner.FPGADesignerError("Unrecognized slave type: %s" % slave_type)

        fn = utils.find_module_filename(module_name, self.get_user_dirs())
        fn = utils.find_rtl_file_location(fn, self.get_user_dirs())

        #Need to create a new name for the slave

        #start with the module name
        name = module_name

        if self.dbg: print "WBC: Getting number of slaves"
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
        self.refresh_constraint_editor()

    def move_slave(self, bus, slave_name, to_index):
        if self.dbg: print "VC: Moving Slave"
        from_index = bus.get_slave_index(slave_name)
        if from_index == to_index:
            self.refresh_slaves()
            return

        slave_type = None

        if bus.get_bus_type() == "peripheral_bus":
            slave_type = SlaveType.PERIPHERAL
        else:
            slave_type = SlaveType.MEMORY

        try:
            self.model.move_slave(slave_name = slave_name,
                                  from_slave_type = slave_type,
                                  from_slave_index = from_index,
                                  to_slave_type = slave_type,
                                  to_slave_index = to_index)

        except ibuilder_error.SlaveError, err:
            pass

        self.refresh_slaves()

    def remove_slave(self, bus, index):
        if self.dbg: print "VC: Remove slave"
        slave_type = None
        if bus == "peripheral_bus":
            slave_type = SlaveType.PERIPHERAL
        else:
            slave_type = SlaveType.MEMORY
        self.model.remove_slave(slave_type, index)
        self.refresh_slaves()
        self.refresh_constraint_editor()


    def find_slave_position(self, drop_position):
        self.output.Debug(self, "Looking for slave position")
        return drop_position


    def drop_event(self, position, event):
        if self.dbg: print "VC: drop_event()"
        if event.mimeData().hasFormat("application/flowchart-data"):
            data = event.mimeData().data("application/flowchart-data")
            #position = self.fd.position()

            #print "Data: %s" % str(data)
            d = json.loads(str(data))
            if event.dropAction() == Qt.MoveAction:
                if self.dbg: print "Moving Slave"
                if "type" in d.keys():
                    if self.dbg: print "\tSlave type: %s" % d["type"]
                    if d["type"] == "peripheral_slave":
                        pb = self.boxes["peripheral_bus"]
                        if self.dbg: print "\tMoving within peripheral bus"
                        index = pb.find_index_from_position(position)
                        self.move_slave(bus=pb, slave_name = d["name"], to_index = index)
                    else:
                        if self.dbg: print "\tMoving within memory bus"
                        mb = self.boxes["memory_bus"]
                        index = mb.find_index_from_position(position)
                        self.move_slave(bus=mb, slave_name = d["name"], to_index = index)
            else:
                if "type" in d.keys():
                    if self.dbg: print "\ttype: %s" % d["type"]
                    if d["type"] == "memory_slave" or d["type"] == "peripheral_slave":

                        if d["type"] == "peripheral_slave":
                            if self.dbg: print "\tSearching peripheral bus"
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


    def get_project_name(self):
        return self.model.get_project_name()


    def bus_refresh_constraint_editor(self, name = None):
        self.dbg = True
        if self.dbg: print "Wishbone Specific Constraint editor refresh"
        if name is not None:
            if self.dbg: print "View only one module"
        else:
            if self.dbg: print "Display all modules"
            pcount = self.model.get_number_of_peripheral_slaves()
            mcount = self.model.get_number_of_memory_slaves()
            for i in range(pcount):
                name = self.model.get_slave_name(SlaveType.PERIPHERAL, i)
                ports = self.model.get_slave_ports(SlaveType.PERIPHERAL, i)
                if self.dbg: print "%s ports: %s" % (name, str(ports))
                bindings = self.model.get_slave_bindings(SlaveType.PERIPHERAL, i)
                if self.dbg: print ""
                signals = ports.keys()
                #signals = bindings.keys()
                #Add Peripheral Signals
                #for key in bindings:
                bound_count = 0
                for key in bindings:
                    if not bindings[key]["range"]:
                        self.constraint_editor.add_connection(color = PS_COLOR,
                                                              module_name = name,
                                                              port = key,
                                                              direction = bindings[key]["direction"],
                                                              pin_name = bindings[key]["loc"])
                    else:
                        indexes = copy.deepcopy(bindings[key].keys())
                        if self.dbg: print "Indexes: %s" % str(indexes)
                        indexes.remove("range")
                        bound_count = 0
                        for i in indexes:
                            bound_count += 1
                            #XXX: This should change to accomodate the tree constraints view
                            #n = "%s[%d]" % (key, i)
                            self.constraint_editor.add_connection(color = PS_COLOR,
                                                                  module_name = name,
                                                                  port = key,
                                                                  direction = bindings[key][i]["direction"],
                                                                  pin_name = bindings[key][i]["loc"],
                                                                  index = i)


                    if key in signals:
                        if not bindings[key]["range"]:
                            signals.remove(key)
                        else:
                            if self.dbg: print "Signal: %s" % key
                            if self.dbg: print "Checking if bound count: %d == %d" % (bound_count, ports[key]["size"])
                            if bound_count == ports[key]["size"]:
                                if self.dbg: print "All of the items in the bus are constrained"
                                signals.remove[key]
                    else:
                        if self.dbg: print "%s is not a port of %s" % (key, name)
                    #XXX: Need a way to detect vectors, sometimes a user will only use part of a vector


                for key in signals:
                    if key == "clk":
                        continue
                    if key == "rst":
                        continue
                    if wishbone_utils.is_wishbone_bus_signal(key):
                        continue

                    print "key: %s" % key
                    if ports[key]["size"] > 1:
                        rng = (ports[key]["max_val"], ports[key]["min_val"])
                        self.constraint_editor.add_signal(PS_COLOR,
                                                          name,
                                                          key,
                                                          rng,
                                                          ports[key]["direction"])

                    else:
                        self.constraint_editor.add_signal(PS_COLOR,
                                                          name,
                                                          key,
                                                          None,
                                                          ports[key]["direction"])


            for i in range(mcount):
                name = self.model.get_slave_name(SlaveType.MEMORY, i)
                ports = self.model.get_slave_ports(SlaveType.MEMORY, i)
                bindings = self.model.get_slave_bindings(SlaveType.MEMORY, i)
                signals = ports.keys()
                #signals = bindings.keys()

                #Add Memory Signals
                for key in bindings:
                    if not bindings[key]["range"]:
                        self.constraint_editor.add_connection(color = MS_COLOR,
                                                              module_name = name,
                                                              port = key,
                                                              direction = bindings[key]["direction"],
                                                              pin_name = bindings[key]["loc"])
                    else:
                        indexes = copy.deepcopy(bindings[key].keys())
                        if self.dbg: print "Indexes: %s" % str(indexes)
                        indexes.remove("range")
                        bound_count = 0
                        for i in indexes:
                            bound_count += 1
                            #XXX: This should change to accomodate the tree constraints view
                            n = "%s[%d]" % (key, i)
                            self.constraint_editor.add_connection(color = MS_COLOR,
                                                                  module_name = name,
                                                                  port = key,
                                                                  direction = bindings[key][i]["direction"],
                                                                  pin_name = bindings[key][i]["loc"],
                                                                  index = i)


                    if key in signals:
                        if not bindings[key]["range"]:
                            signals.remove(key)
                        else:
                            if self.dbg: print "Signal: %s" % key
                            if self.dbg: print "Checking if bound count: %d == %d" % (bound_count, ports[key]["size"])
                            if bound_count == ports[key]["size"]:
                                if self.dbg: print "All of the items in the bus are constrained"
                                signals.remove(key)
                    else:
                        if self.dbg: print "%s is not a port of %s" % (key, name)
                    #XXX: Need a way to detect vectors, sometimes a user will only use part of a vector



                for key in signals:
                    if key == "clk":
                        continue
                    if key == "rst":
                        continue
                    if wishbone_utils.is_wishbone_bus_signal(key):
                        continue

                    if ports[key]["size"] > 1:
                        rng = (ports[key]["max_val"], ports[key]["min_val"])
                        self.constraint_editor.add_signal(MS_COLOR,
                                                          name,
                                                          key,
                                                          rng,
                                                          ports[key]["direction"])
                    else:
                        self.constraint_editor.add_signal(MS_COLOR,
                                                          name,
                                                          key,
                                                          None,
                                                          ports[key]["direction"])


        self.dbg = True




