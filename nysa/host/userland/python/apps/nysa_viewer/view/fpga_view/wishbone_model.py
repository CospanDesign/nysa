#!/usr/bin/env python

#Distributed under the MIT licesnse.
#Copyright (c) 2013 Cospan Design (dave.mccoy@cospandesign.com)

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




import os
import sys
import json
import copy

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, "lib"))
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

#Inner package modules
from lib import ibuilder
from lib import constraint_utils as cu

from ibuilder_error import ModuleNotFound
from ibuilder_error import SlaveError

from gui_error import WishboneModelError

import graph_manager as gm

from graph_manager import GraphManager
from graph_manager import SlaveType
from graph_manager import NodeType
from graph_manager import get_unique_name

import utils
import verilog_utils as vutils


class WishboneModel():
    def __init__(self, config_dict):
        self.gm = GraphManager()
        self.bus_type = "wishbone"
        self.tags = {}
        self.config_dict = {}
        self.config_dict["PROJECT_NAME"] = "project"
        self.config_dict["TEMPLATE"] = config_dict["bus_type"]
        self.config_dict["INTERFACE"] = {}
        self.config_dict["SLAVES"] = {}
        self.config_dict["MEMORY"] = {}
        self.config_dict["board"] = config_dict["board"]

        self.load_config_dict(config_dict)
        self.initialize_graph()

    def load_config_dict(self, config_dict):
        self.config_dict = config_dict
        self.build_tool = {}
        self.board_dict = config_dict["board"]

    def initialize_graph(self, debug=False):
        """Initializes the graph and project tags."""

        if debug:
            print ("Initialize graph")
        # Clear any previous data.
        self.gm.clear_graph()

        # Set the bus type.
        if self.config_dict["TEMPLATE"] == "wishbone_template.json":
            self.set_bus_type("wishbone")
        elif self.config_dict["TEMPLATE"] == "axi_template.json":
            self.set_bus_type("axi")
        else:
            raise WishboneModelError("Template is not specified")

        # Add the nodes that are always present.
        self.gm.add_node("Host Interface", NodeType.HOST_INTERFACE)
        self.gm.add_node("Master", NodeType.MASTER)
        self.gm.add_node("Memory", NodeType.MEMORY_INTERCONNECT)
        self.gm.add_node("Peripherals", NodeType.PERIPHERAL_INTERCONNECT)
        self.add_slave("DRT", SlaveType.PERIPHERAL, slave_index=0)

        # Get all the unique names for accessing nodes.
        hi_name = get_unique_name("Host Interface",
                                    NodeType.HOST_INTERFACE)
        m_name = get_unique_name("Master", NodeType.MASTER)
        mi_name = get_unique_name("Memory", NodeType.MEMORY_INTERCONNECT)
        pi_name = get_unique_name("Peripherals",
                                    NodeType.PERIPHERAL_INTERCONNECT)
        drt_name = get_unique_name("DRT",
                                        NodeType.SLAVE,
                                        SlaveType.PERIPHERAL,
                                        slave_index=0)

        # Attach all the appropriate nodes.
        self.gm.connect_nodes(hi_name, m_name)
        self.gm.connect_nodes(m_name, mi_name)
        self.gm.connect_nodes(m_name, pi_name)
        self.gm.connect_nodes(pi_name, drt_name)

        # Get module data for the DRT.
        # Attempt to load data from the tags.
        sp_count = self.gm.get_number_of_peripheral_slaves()
        if debug:
            print (("loading %d peripheral slave(s)" % sp_count))

        #print "Config Dict: %s" % str(self.config_dict)
        if "SLAVES" in self.config_dict:
            for slave_name in self.config_dict["SLAVES"]:
                if debug:
                    print (("loading slave: %s" % slave_name))

                uname = self.add_slave(slave_name,
                                       SlaveType.PERIPHERAL)

        # Load all the memory slaves.
        sm_count = self.gm.get_number_of_memory_slaves()
        if debug:
            print(("loading %d memory slaves" % sm_count))

        if "MEMORY" in self.config_dict:
            for slave_name in self.config_dict["MEMORY"]:

                uname = self.add_slave(slave_name,
                                        SlaveType.MEMORY,
                                        slave_index=-1)

        # Check if there is a host interface defined.
        if "INTERFACE" in self.config_dict:
            self.set_host_interface("Host Interface")

        if debug:
            print ("Finish Initialize graph")

    def get_number_of_slaves(self, slave_type):
        if slave_type is None:
            raise SlaveError("slave type was not specified")

        if slave_type == SlaveType.PERIPHERAL:
            return self.get_number_of_peripheral_slaves()

        return self.get_number_of_memory_slaves()

    def get_number_of_memory_slaves(self):
        return self.gm.get_number_of_memory_slaves()

    def get_number_of_peripheral_slaves(self):
        return self.gm.get_number_of_peripheral_slaves()

    def apply_slave_tags_to_project(self, debug=False):
        """Apply the slave tags to the project tags."""
        # Get all the slaves.
        p_count = self.get_number_of_slaves(SlaveType.PERIPHERAL)
        m_count = self.get_number_of_slaves(SlaveType.MEMORY)
        self.config_dict["SLAVES"] = {}
        self.config_dict["MEMORY"] = {}

        for i in range(0, p_count):
            #print "apply slave tags to project: %d:" % i
            sc_slave = self.gm.get_slave_at(SlaveType.PERIPHERAL, i)
            uname = sc_slave.unique_name
            name = sc_slave.name
            if debug:
                print (("name: %s" % str(name)))
            #if debug:
            #    print (("Projct tags: %s" % str(self.config_dict)))
            if name == "DRT":
                continue
            if name not in list(self.config_dict["SLAVES"].keys()):
                self.config_dict["SLAVES"][name] = {}

            pt_slave = self.config_dict["SLAVES"][name]

            # Overwrite the current arbitor dictionary.
            if "BUS" in list(pt_slave.keys()):
                pt_slave["BUS"] = {}

            if "arbitor_masters" in list(sc_slave.parameters.keys()):
                ams = sc_slave.parameters["arbitor_masters"]
                if len(ams) > 0:
                    # Add the BUS keyword to the arbitor master.
                    pt_slave["BUS"] = {}
                    # Add all the items from the sc version.
                    for a in ams:
                        if debug:
                            print (("arbitor name: %s" % a))
                        arb_slave = self.get_connected_arbitor_slave(uname, a)

                        arb_name = self.gm.get_node(arb_slave).name
                        if arb_slave is not None:
                            pt_slave["BUS"][a] = arb_name

        # Memory BUS
        for i in range(0, m_count):
            sc_slave = self.gm.get_slave_at(SlaveType.MEMORY, i)
            uname = sc_slave.unique_name
            name = sc_slave.name
            if debug:
                print (("name: %s" % str(name)))
            if name not in list(self.config_dict["MEMORY"].keys()):
                self.config_dict["MEMORY"][name] = {}

            pt_slave = self.config_dict["MEMORY"][name]

            # Overwrite the current arbitor dictionary.
            if "BUS" in list(pt_slave.keys()):
                pt_slave["BUS"] = {}

            if "arbitor_masters" in list(sc_slave.parameters.keys()):
                ams = sc_slave.parameters["arbitor_masters"]
                if len(ams) > 0:
                    # Add the BUS keyword to the arbitor master.
                    pt_slave["BUS"] = {}
                    # Add all the items from the sc version.
                    for a in list(ams):
                        if debug:
                            print (("arbitor name: %s" % a))
                        arb_slave = self.get_connected_arbitor_slave(uname, a)

                        arb_name = self.gm.get_node(arb_slave).name
                        if arb_slave is not None:
                            pt_slave["BUS"][a] = arb_name
            module = sc_slave.parameters["module"]

    def get_board_name(self):
        if "board" in list(self.config_dict.keys()):
            return self.config_dict["board"]
        return "undefined"

    def set_bus_type(self, bus_type):
        """Set the bus type to Wishbone or Axie."""
        self.bus_type = bus_type

    def get_bus_type(self):
        return self.bus_type

    def get_host_interface_name(self):
        hi_name = get_unique_name("Host Interface",
                                       NodeType.HOST_INTERFACE)
        hi = self.gm.get_node(hi_name)
        return "Host Interface"

    def get_slave_name(self, slave_type, slave_index):
        s_name = self.gm.get_slave_name_at(slave_type, slave_index)
        slave = self.gm.get_node(s_name)
        return slave.name

    def is_arb_master_connected(self, slave_name, arb_host, debug=False):
        slaves = self.gm.get_connected_slaves(slave_name)
        for key in slaves:
            #print "key: %s" % key
            edge_name = self.gm.get_edge_name(slave_name, slaves[key])
            if (arb_host == edge_name):
                return True
        return False

    def add_arbitor_by_name(self, host_name, arbitor_name, slave_name):
        tags = self.gm.get_parameters(host_name)
        if arbitor_name not in tags["arbitor_masters"]:
            raise WishboneModelError("%s is not an arbitor of %s" %
                                    (arbitor_name, host_name))

        self.gm.connect_nodes(host_name, slave_name)
        self.gm.set_edge_name(host_name, slave_name, arbitor_name)

    def add_arbitor(self, host_type, host_index,
                         arbitor_name, slave_type, slave_index):
        """Adds an arbitor and attaches it between the host and the slave."""
        h_name = self.gm.get_slave_name_at(host_type, host_index)
        s_name = self.gm.get_slave_name_at(slave_type, slave_index)
        self.add_arbitor_by_name(h_name, arbitor_name, s_name)

    def get_connected_arbitor_slave(self, host_name, arbitor_name):
        tags = self.gm.get_parameters(host_name)
        if arbitor_name not in tags["arbitor_masters"]:
            SlaveError("This slave has no arbitor masters")

        slaves = self.gm.get_connected_slaves(host_name)
        for arb_name in slaves:
            slave = slaves[arb_name]
            edge_name = self.gm.get_edge_name(host_name, slave)
            if edge_name == arbitor_name:
                return slave
        return None

    def get_connected_arbitor_name(self, host_type, host_index,
                                      slave_type, slave_index):
        h_name = self.gm.get_slave_name_at(host_type, host_index)
        s_name = self.gm.get_slave_name_at(slave_type, slave_index)

        tags = self.gm.get_parameters(h_name)
        for arb_name in tags["arbitor_masters"]:
            slave_name = self.get_connected_arbitor_slave(h_name, arb_name)
            if slave_name == s_name:
                return arb_name

        raise WishboneModelError(
            "host: %s is not connected to %s" % (h_name, s_name))

    def remove_arbitor_by_arb_master(self, host_name, arb_name):
        slave_name = self.get_connected_arbitor_slave(host_name, arb_name)
        self.remove_arbitor_by_name(host_name, slave_name)

    def remove_arbitor_by_name(self, host_name, slave_name):
        self.gm.disconnect_nodes(host_name, slave_name)

    def remove_arbitor(self, host_type, host_index, slave_type, slave_index):
        """Finds and removes the arbitor from the host."""
        h_name = self.gm.get_slave_name_at(host_type, host_index)
        s_name = self.gm.get_slave_name_at(slave_type, slave_index)
        self.remove_arbitor_by_name(h_name, s_name)

    def is_active_arbitor_host(self, host_type, host_index):
        h_name = self.gm.get_slave_name_at(host_type, host_index)
        tags = self.gm.get_parameters(h_name)
        if h_name not in tags["arbitor_masters"]:
            if len(tags["arbitor_masters"]) == 0:
                return False

        if not self.gm.is_slave_connected_to_slave(h_name):
            return False

        return True

    def get_slave_name_by_unique(self, slave_name):
        node = self.gm.get_node(slave_name)
        return node.name

    def get_arbitor_dict(self, host_type, host_index):
        if not self.is_active_arbitor_host(host_type, host_index):
            return {}

        h_name = self.gm.get_slave_name_at(host_type, host_index)
        return self.gm.get_connected_slaves(h_name)

    def add_slave(self, name, slave_type, slave_index=-1):
        """Adds a slave to the specified bus at the specified index."""
        # Check if the slave_index makes sense.  If slave index s -1 then add it
        # to the next available location
        s_count = self.gm.get_number_of_slaves(slave_type)
        self.gm.add_node(name, NodeType.SLAVE, slave_type)

        slave = None

        if slave_index == -1: #Add slave at the end
            slave_index = s_count
        else:  # Add the slave to where the index is pointing
            if slave_type == SlaveType.PERIPHERAL:
                if slave_index == 0 and name != "DRT":
                    raise gm.SlaveError("Only the DRT can be at position 0")
                s_count = self.gm.get_number_of_peripheral_slaves()
                uname = get_unique_name(name,
                                        NodeType.SLAVE,
                                        slave_type,
                                        s_count - 1)
                slave = self.gm.get_node(uname)
                if slave_index < s_count - 1:
                    self.gm.move_peripheral_slave(slave.slave_index,
                                                  slave_index)
            elif slave_type == SlaveType.MEMORY:
                s_count = self.gm.get_number_of_memory_slaves()
                uname = get_unique_name(name,
                                        NodeType.SLAVE,
                                        slave_type,
                                        s_count - 1)
                slave = self.gm.get_node(uname)
                if slave_index < s_count - 1:
                    self.gm.move_slave(slave.slave_index,
                                       slave_index,
                                       SlaveType.MEMORY)

        uname = get_unique_name(name,
                                NodeType.SLAVE,
                                slave_type,
                                slave_index)

        slave = self.gm.get_node(uname)
        return uname

    def get_graph_manager(self):
        '''Returns the graph manager.'''
        return self.gm

    def get_unique_from_module_name(self, module_name):
        """Return the unique name associated with the module_name"""
        if module_name == "Host Interface":
            return self.get_host_interface_name()
        pcount = self.get_number_of_peripheral_slaves()
        for i in range(pcount):
            name = self.get_slave_name(SlaveType.PERIPHERAL, i)
            if module_name == name:
                return get_unique_name(name, NodeType.SLAVE, SlaveType.PERIPHERAL, i)

        mcount = self.get_number_of_memory_slaves()
        for i in range(mcount):
            name = self.get_slave_name(SlaveType.MEMORY, i)
            if module_name == name:
                return get_unique_name(name, NodeType.SLAVE, SlaveType.MEMORY, i)

        raise SlaveError("Module with name %s not found" % module_name)

    def set_host_interface(self, host_interface_name, debug=False):
        """Sets the host interface type. If host_interface_name is not a valid
        module name (or cannot be found for whatever reason), throws a
        ModuleNotFound exception."""
        hi_name = get_unique_name("Host Interface",
                                       NodeType.HOST_INTERFACE)
        if debug:
            print (("hi_name: %s" % hi_name))

        node_names = self.gm.get_node_names()
        if hi_name not in node_names:
            self.gm.add_node("Host Interface", NodeType.HOST_INTERFACE)

        return True


