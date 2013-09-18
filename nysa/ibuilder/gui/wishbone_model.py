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
    def __init__(self, board_name=None, config_file=None):
        self.project_tags = {}
        self.new_design()
        self.filename = ""
        self.user_paths = []

        # Add some variable functions for dependency injection.
        self.get_board_config = utils.get_board_config
        self.get_unique_name = get_unique_name
        #self.board_dict = {}
        if config_file is not None:
            self.load_config_file(config_file)
            self.initialize_graph()
        elif board_name is not None:
            self.set_default_board_project(board_name)
            self.initialize_graph()
        else:
            #initialize an empty tags
            self.initialize_graph()

    def add_user_path(self, path):
        if path not in self.user_paths:
            self.user_paths.append(path)

    def get_user_paths(self):
        return self.user_paths

    def remove_user_paths(self, path):
        if path in self.user_paths:
            self.user_paths.remove(path)

    def set_default_board_project(self, board_name):
        self.set_board_name(board_name.lower())

        if self.get_board_name() != "undefined":

            base = utils.get_nysa_base()
            #print "board name: %s" % str(self.get_board_name())
            #print "board dict: %s" % str(self.board_dict)
            #print "project dict: %s" % str(self.project_tags)
            config_file = self.board_dict["default_project"]
            config_file = os.path.join(base,
                                       "ibuilder",
                                       "example_projects",
                                       config_file)
            self.load_config_file(config_file)

    def load_config_dict(self, config_dict):
        self.project_tags = config_dict
        self.build_tool = {}
        self.board_dict = self.get_board_config(self.project_tags["board"])
        # XXX Doing anything?
#       self.get_project_constraint_files()
        return True

    def load_config_file(self, filename, debug=False):
        """Loads a nysa configuration file into memory.  Raises an IOError if
        the file cannot be found."""
        # Open up the specified JSON project config file and copy it into
        #the buffer
        # (may raise an IOError).
        filein = open(filename)
        json_string = filein.read()
        filein.close()

        self.project_tags = json.loads(json_string)
        self.filename = filename
        self.build_tool = {}
        self.board_dict = self.get_board_config(self.project_tags["board"])
        # XXX Doing anything?
#       self.get_project_constraint_files()
        return True

    def set_config_file_location(self, filename):
        self.filename = filename

    def initialize_graph(self, debug=False):
        """Initializes the graph and project tags."""

        if debug:
            print ("Initialize graph")
        # Clear any previous data.
        self.gm.clear_graph()

        # Set the bus type.
        if self.project_tags["TEMPLATE"] == "wishbone_template.json":
            self.set_bus_type("wishbone")
        elif self.project_tags["TEMPLATE"] == "axi_template.json":
            self.set_bus_type("axi")
        else:
            raise WishboneModelError("Template is not specified")

        # Add the nodes that are always present.
        self.gm.add_node("Host Interface", NodeType.HOST_INTERFACE)
        self.gm.add_node("Master", NodeType.MASTER)
        self.gm.add_node("Memory", NodeType.MEMORY_INTERCONNECT)
        self.gm.add_node("Peripherals", NodeType.PERIPHERAL_INTERCONNECT)
        self.add_slave("DRT", None, SlaveType.PERIPHERAL, slave_index=0)

        # Get all the unique names for accessing nodes.
        hi_name = self.get_unique_name("Host Interface",
                                    NodeType.HOST_INTERFACE)
        m_name = self.get_unique_name("Master", NodeType.MASTER)
        mi_name = self.get_unique_name("Memory", NodeType.MEMORY_INTERCONNECT)
        pi_name = self.get_unique_name("Peripherals",
                                    NodeType.PERIPHERAL_INTERCONNECT)
        drt_name = self.get_unique_name("DRT",
                                        NodeType.SLAVE,
                                        SlaveType.PERIPHERAL,
                                        slave_index=0)

        # Attach all the appropriate nodes.
        self.gm.connect_nodes(hi_name, m_name)
        self.gm.connect_nodes(m_name, mi_name)
        self.gm.connect_nodes(m_name, pi_name)
        self.gm.connect_nodes(pi_name, drt_name)

        # Get module data for the DRT.
        try:
            filename = utils.find_rtl_file_location("device_rom_table.v", self.get_user_paths())
        except ModuleNotFound:
            if debug:
                print ("device_rom_table.v not found")
            raise WishboneModelError("DRT module was not found")

        parameters = vutils.get_module_tags(filename=filename,
                                           bus=self.get_bus_type(),
                                           user_paths = self.get_user_paths())
        self.gm.set_parameters(drt_name, parameters)

        # Attempt to load data from the tags.
        sp_count = self.gm.get_number_of_peripheral_slaves()
        if debug:
            print (("loading %d peripheral slaves" % sp_count))

        if "SLAVES" in self.project_tags:
            for slave_name in self.project_tags["SLAVES"]:
                if debug:
                    print (("loading slave: %s" % slave_name))

                filename = self.project_tags["SLAVES"][slave_name]["filename"]
                if "device_rom_table" in filename:
                    filename = None

                if filename is not None:
                    filename = utils.find_rtl_file_location(filename, self.get_user_paths())

                uname = self.add_slave(slave_name,
                                       filename,
                                       SlaveType.PERIPHERAL)

                # Add the bindings from the config file.
                skeys = list(self.project_tags["SLAVES"][slave_name].keys())
##               print "adding bindings"
##               if "bind" not in skeys:
##                 self.project_tags["SLAVES"][slave_name]["bind"] = {}

                if "bind" in skeys:
                    #print "found binding for: %s" % slave_name
                    #print "bindings: %s" % self.project_tags["SLAVES"][slave_name]["bind"]
                    c_bindings = self.project_tags["SLAVES"][slave_name]["bind"]
                    e_bindings = cu.expand_user_constraints(c_bindings)
                    #print "ebindings: %s" % str(e_bindings)
                    self.gm.set_config_bindings(uname, e_bindings)
                else:
                    self.project_tags["SLAVES"][slave_name]["bind"] = {}

        # Load all the memory slaves.
        sm_count = self.gm.get_number_of_memory_slaves()
        if debug:
            print(("loading %d memory slaves" % sm_count))

        if "MEMORY" in self.project_tags:
            for slave_name in self.project_tags["MEMORY"]:

                filename = self.project_tags["MEMORY"][slave_name]["filename"]
                filename = utils.find_rtl_file_location(filename, self.get_user_paths())
                uname = self.add_slave(slave_name,
                                        filename,
                                        SlaveType.MEMORY,
                                        slave_index=-1)

                # Add the bindings from the config file.
                mkeys = list(self.project_tags["MEMORY"][slave_name].keys())
                if "bind" in mkeys:
                    c_bindings = self.project_tags["MEMORY"][slave_name]["bind"]
                    e_bindings = cu.expand_user_constraints(c_bindings)
                    self.gm.set_config_bindings(uname, e_bindings)
                else:
                    self.project_tags["MEMORY"][slave_name]["bind"] = {}

        # Check if there is a host interface defined.
        if "INTERFACE" in self.project_tags:
            filename = utils.find_rtl_file_location(
                            self.project_tags["INTERFACE"]["filename"],
                            self.get_user_paths())
            if debug:
                print (("Loading interface: %s" % filename))
            parameters = vutils.get_module_tags(filename=filename,
                                               bus=self.get_bus_type(),
                                               user_paths = self.get_user_paths())
            self.set_host_interface(parameters["module"])
            if "bind" in list(self.project_tags["INTERFACE"].keys()):
                c_bindings = self.project_tags["INTERFACE"]["bind"]
                e_bindings = cu.expand_user_constraints(c_bindings)
                self.gm.set_config_bindings(hi_name, e_bindings)
            else:
                self.project_tags["INTERFACE"]["bind"] = {}

            self.gm.set_parameters(hi_name, parameters)

        if "SLAVES" in self.project_tags:
            for host_name in self.project_tags["SLAVES"]:
                if "BUS" in list(self.project_tags["SLAVES"][host_name].keys()):
                    for arb_name in \
                            self.project_tags["SLAVES"][host_name]["BUS"]:
                        #there is an arbitor here
                        slave_name = \
                        self.project_tags["SLAVES"][host_name]["BUS"][arb_name]

                        if debug:
                            print ((
                                "arbitor: %s attaches to %s through bus: %s" %
                                (host_name, slave_name, arb_name)))

                        #h_name = ""
                        h_index = -1
                        h_type = SlaveType.PERIPHERAL
                        #s_name = ""
                        s_index = -1
                        s_type = SlaveType.PERIPHERAL

                        # Now to attach the arbitor.
                        p_count = \
                            self.get_number_of_slaves(SlaveType.PERIPHERAL)
                        m_count = self.get_number_of_slaves(SlaveType.MEMORY)

                        # Find the host and slave nodes.
                        for i in range(0, p_count):
                            self.gm.get_slave_name_at(SlaveType.PERIPHERAL, i)
                            sn = self.gm.get_slave_name_at(SlaveType.PERIPHERAL,
                                                            i)
                            slave = self.gm.get_node(sn)

                            if slave.name == host_name:
                                #h_name = slave.unique_name
                                h_index = i
                                h_type = SlaveType.PERIPHERAL

                            if slave.name == slave_name:
                                #s_name = slave.unique_name
                                s_index = i
                                s_type = SlaveType.PERIPHERAL

                        for i in range(0, m_count):
                            self.gm.get_slave_name_at(SlaveType.MEMORY, i)
                            sn = self.gm.get_slave_name_at(SlaveType.MEMORY, i)
                            slave = self.gm.get_node(sn)

                            if slave.name == host_name:
                                #h_name = slave.unique_name
                                h_index = i
                                h_type = SlaveType.MEMORY

                            if slave.name == slave_name:
                                #s_name = slave.unique_name
                                s_index = i
                                s_type = SlaveType.MEMORY

                        # Now I have all the materialst to attach the arbitor.
                        self.add_arbitor(h_type,
                                         h_index,
                                         arb_name,
                                         s_type,
                                         s_index)

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

    def save_config_file(self, filename):
        """Saves a module stored in memory to a file."""

        # If there are no slaves on the memory interconnect then don't generate
        # the structure in the JSON file for it.

        json_string = json.dumps(self.project_tags, sort_keys=True, indent=4)
        try:
            #print "Data to write:\n%s" % json_string
            file_out = open(filename, 'w')
            file_out.write(json_string)
            file_out.close()
        except IOError as err:
            print (("File Error: %s" % str(err)))
            raise WishboneModelError("Unable to write config file: %s" %
                    filename)

    def apply_slave_tags_to_project(self, debug=False):
        """Apply the slave tags to the project tags."""
        # Get all the slaves.
        p_count = self.get_number_of_slaves(SlaveType.PERIPHERAL)
        m_count = self.get_number_of_slaves(SlaveType.MEMORY)
##      bind_dict = self.get_consolodated_master_bind_dict()
        self.project_tags["SLAVES"] = {}
        self.project_tags["MEMORY"] = {}

        for i in range(0, p_count):
            #print "apply slave tags to project: %d:" % i
            sc_slave = self.gm.get_slave_at(SlaveType.PERIPHERAL, i)
            uname = sc_slave.unique_name
            name = sc_slave.name
            if debug:
                print (("name: %s" % str(name)))
            #if debug:
            #    print (("Projct tags: %s" % str(self.project_tags)))
            if name == "DRT":
                continue
            if name not in list(self.project_tags["SLAVES"].keys()):
                self.project_tags["SLAVES"][name] = {}

            pt_slave = self.project_tags["SLAVES"][name]
            if "bind" not in list(pt_slave.keys()):
                pt_slave["bind"] = {}

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
##                      pt_slave["BUS"]

            # Clear the current bindings in the project tags.
            pt_slave["bind"] = {}

            bindings = self.gm.get_node_bindings(uname)
##           bind = sc_slave.bindings
##           print "bind id: " + str(id(bindings))
            #if debug:
            #    print (("bind contents: %s" % str(bindings)))
            pt_slave["bind"] = cu.consolodate_constraints(bindings)
            #for p in bindings:
                #pt_slave["bind"][p] = {}
                #pt_slave["bind"][p]["port"] = bindings[p]["loc"]
                #pt_slave["bind"][p]["direction"] = bindings[p]["direction"]

            # Add filenames.
            module = sc_slave.parameters["module"]
            filename = utils.find_module_filename(module, self.get_user_paths())
            pt_slave["filename"] = filename

      # Memory BUS
        for i in range(0, m_count):
            sc_slave = self.gm.get_slave_at(SlaveType.MEMORY, i)
            uname = sc_slave.unique_name
            name = sc_slave.name
            if debug:
                print (("name: %s" % str(name)))
            if name not in list(self.project_tags["MEMORY"].keys()):
                self.project_tags["MEMORY"][name] = {}

            pt_slave = self.project_tags["MEMORY"][name]
            if "bind" not in list(pt_slave.keys()):
                pt_slave["bind"] = {}

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
##                   pt_slave["BUS"]

            # Clear the current bindings in the project tags.
            pt_slave["bind"] = {}

            bindings = self.gm.get_node_bindings(uname)
##           print "bind id: " + str(id(bindings))
            #if debug:
            #    print (("bind contents: %s" % str(bindings)))
            pt_slave["bind"] = cu.consolodate_constraints(bindings)
            #for p in bindings:
            #    pt_slave["bind"] = cu.consolodate_constraints(bindings)
            #    pt_slave["bind"][p] = {}
            #    pt_slave["bind"][p]["port"] = bindings[p]["loc"]
            #    pt_slave["bind"][p]["direction"] = bindings[p]["direction"]
            module = sc_slave.parameters["module"]
            filename = utils.find_module_filename(module, self.get_user_paths())
            pt_slave["filename"] = filename



    def set_project_location(self, location):
        """Sets the location of the project to output."""
        self.project_tags["BASE_DIR"] = location

    def get_project_location(self):
        return self.project_tags["BASE_DIR"]

    def set_project_name(self, name):
        """Sets the name of the output project."""
        self.project_tags["PROJECT_NAME"] = name

    def get_project_name(self):
        return self.project_tags["PROJECT_NAME"]

##   def set_vendor_tools(self, vendor_tool):
##     """
##     sets the vendor build tool, currently only
##     Xilinx is supported
##     """
##     self.project_tags["BUILD_TOOL"] = vendor_tool

    def get_vendor_tools(self):
##       board_dict = utils.get_board_config(self.project_tags["board"])
##       return board_dict["build_tool"]
        return self.board_dict["build_tool"]

    def set_board_name(self, board_name):
        """Sets the name of the board to use."""
        if "board" not in list(self.project_tags.keys()):
            self.project_tags["board"] = ""

        self.project_tags["board"] = board_name
        self.board_dict = utils.get_board_config(board_name)
        #print "board dict: %s" % str(self.board_dict)

    def get_board_name(self):
        if "board" in list(self.project_tags.keys()):
            return self.project_tags["board"]
        return "undefined"

    def get_constraint_filenames(self):
        board_name = self.project_tags["board"]
        pt = self.project_tags
        if "constraint_files" not in list(pt.keys()):
            pt["constraint_files"] = []

        cfiles = utils.get_constraint_filenames(board_name)
        for cf in pt["constraint_files"]:
            cfiles.append(cf)
        return cfiles

    def add_project_constraint_file(self, constraint_file):
        pt = self.project_tags

        if "constraint_files" not in list(pt.keys()):
            pt["constraint_files"] = []

        cfiles = pt["constraint_files"]
        if constraint_file not in cfiles:
            cfiles.append(constraint_file)

    def remove_project_constraint_file(self, constraint_file):
        pt = self.project_tags
        cfiles = pt["constraint_files"]
        if constraint_file in cfiles:
            cfiles.remove(constraint_file)

    def set_project_constraint_files(self, constraint_files):
        self.project_tags["constraint_files"] = constraint_files

    def get_fpga_part_number(self):
        return self.board_dict["fpga_part_number"]

    def new_design(self):
        self.gm = GraphManager()
        self.bus_type = "wishbone"
        self.tags = {}
        self.filename = ""
        self.project_tags = {}
        self.project_tags["PROJECT_NAME"] = "project"
        self.project_tags["BASE_DIR"] = "~/user_projects"
        self.project_tags["BUILD_TOOL"] = "xilinx"
        self.project_tags["TEMPLATE"] = "wishbone_template.json"
        self.project_tags["INTERFACE"] = {}
        self.project_tags["INTERFACE"]["filename"] = "uart_io_handler.v"
        self.project_tags["SLAVES"] = {}
        self.project_tags["MEMORY"] = {}
        self.project_tags["board"] = "dionysus"
        self.project_tags["bind"] = {}
        self.project_tags["constraint_files"] = []

    def set_bus_type(self, bus_type):
        """Set the bus type to Wishbone or Axie."""
        self.bus_type = bus_type

    def get_bus_type(self):
        return self.bus_type

    def set_host_interface(self, host_interface_name, debug=False):
        """Sets the host interface type. If host_interface_name is not a valid
        module name (or cannot be found for whatever reason), throws a
        ModuleNotFound exception."""
        hi_name = self.get_unique_name("Host Interface",
                                       NodeType.HOST_INTERFACE)
        if debug:
            print (("hi_name: %s" % hi_name))

        node_names = self.gm.get_node_names()
        if hi_name not in node_names:
            self.gm.add_node("Host Interface", NodeType.HOST_INTERFACE)

        # Check if the host interface is valid.
        filename = utils.find_module_filename(host_interface_name, self.get_user_paths())

        #XXX: Should this be the full file name??
        self.project_tags["INTERFACE"]["filename"] = filename
        filename = utils.find_rtl_file_location(filename, self.get_user_paths())

        #print "hi project tags: %s" % str(self.project_tags["INTERFACE"])
        # If the host interface is valid then get all the tags ...
        parameters = vutils.get_module_tags(filename=filename,
                                           bus=self.get_bus_type(),
                                           user_paths = self.get_user_paths())
        # ... and set them up.
        self.gm.set_parameters(hi_name, parameters, debug=debug)
        return True

    def get_expanded_master_bind_dict(self):
        """Create a large dictionary of all the constraints from
            - project
            - host interface
            - peripheral slaves
            - memory slaves
        """
        bind_dict = {}
        bind_dict["project"] = cu.expand_user_constraints(
                                        self.project_tags["bind"])
        bind_dict["host interface"] = self.get_host_interface_bindings()

        #Get Peripheral Slaves
        p_count = self.get_number_of_slaves(SlaveType.PERIPHERAL)
        for i in range(p_count):
            slave = self.gm.get_slave_at(SlaveType.PERIPHERAL, i)
            bind_dict[slave.name] = self.gm.get_node_bindings(slave.unique_name)

        #Get Memory Slaves
        m_count = self.get_number_of_slaves(SlaveType.MEMORY)
        for i in range(m_count):
            slave = self.gm.get_slave_at(SlaveType.MEMORY, i)
            bind_dict[slave.name] = self.gm.get_node_bindings(slave.unique_name)

        return bind_dict

    def get_consolodated_master_bind_dict(self):
        """Combine the dictionary from:
          - project
          - host interface
          - peripheral slaves
          - memory slaves

          The returned dictionary is consolodated in that all the pins are
          not expanded to a unique index, this is good for a project but not
          good for manipulation
          """

        # The dictionary to put the entries in and return.
        bind_dict = {}

        # Get project bindings.
        print "TODO: Need to visualize the board level binds like CLOCK and RESET!"
        bind = self.project_tags["bind"]
        for k in bind:
            bind_dict[k] = bind[k]

        # Get host interface bindings.
        hi_name = self.get_unique_name("Host Interface",
                                       NodeType.HOST_INTERFACE)
        hib = cu.consolodate_constraints(self.gm.get_node_bindings(hi_name))
        for k, v in list(hib.items()):
            bind_dict[k] = v

        # Get all the peripheral slave bindings.
        p_count = self.get_number_of_slaves(SlaveType.PERIPHERAL)
        for i in range(p_count):
            slave = self.gm.get_slave_at(SlaveType.PERIPHERAL, i)
            pb = cu.consolodate_constraints(
                                self.gm.get_node_bindings(slave.unique_name))
            for key in pb:
                bind_dict[key] = pb[key]

        # Get all the memory slave bindings.
        m_count = self.get_number_of_slaves(SlaveType.MEMORY)
        for i in range(m_count):
            slave = self.gm.get_slave_at(SlaveType.MEMORY, i)
            mb = cu.consolodate_constraints(
                                self.gm.get_node_bindings(slave.unique_name))
            for key in mb:
                bind_dict[key] = mb[key]

        return bind_dict

    def get_slave_ports(self, slave_type, slave_index):
        slave_name = self.get_slave_name(slave_type, slave_index)
        uname = self.get_unique_name(slave_name, NodeType.SLAVE, slave_type,
                                     slave_index)
        return self.get_node_ports(uname)

    def get_slave_bindings(self, slave_type, slave_index):
        slave_name = self.get_slave_name(slave_type, slave_index)
        uname = self.get_unique_name(slave_name,
                                     NodeType.SLAVE,
                                     slave_type,
                                     slave_index)
        return self.gm.get_node_bindings(uname)

    def get_host_interface_bindings(self):
        hi_name = self.get_unique_name("Host Interface",
                                       NodeType.HOST_INTERFACE)
        return self.gm.get_node_bindings(hi_name)

    def get_host_interface_ports(self):
        hi_name = self.get_unique_name("Host Interface",
                                       NodeType.HOST_INTERFACE)
        return self.get_node_ports(hi_name)

    def get_node_ports(self, node_name):
        return self.gm.get_node(node_name).parameters["ports"]

    def set_binding(self, node_name, port_name, pin_name, index=None):
        """Add a binding between the port and the pin."""
        un = self.get_unique_from_module_name(node_name)
        self.gm.bind_port(un, port_name, pin_name, index)
        return

    def unbind_port(self, node_name, port_name, index=None):
        """Remove a binding with the port name."""
        #print "node name: %s" % node_name
        #un = self.get_unique_from_module_name(node_name)
        self.gm.unbind_port(node_name, port_name, index=None)
        return

    def unbind_all(self, debug=False):
        if debug:
            print ("unbind all")
        mbd = self.get_consolodated_master_bind_dict()
        if debug:
            print (("Master Bind Dict: %s" % str(mbd)))
        node_names = self.gm.get_node_names()
        for nn in node_names:
            nb = copy.deepcopy(self.gm.get_node_bindings(nn))
            for b in nb:
                if debug:
                    print (("Unbindig %s" % b))
                self.gm.unbind_port(nn, b)

    def get_host_interface_name(self):
        hi_name = self.get_unique_name("Host Interface",
                                       NodeType.HOST_INTERFACE)
        hi = self.gm.get_node(hi_name)
        return hi.parameters["module"]

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
##       tags = self.gm.get_parameters(h_name)
##       print "h_name: " + h_name
##       if arbitor_name not in tags["arbitor_masters"]:
##         return False

        s_name = self.gm.get_slave_name_at(slave_type, slave_index)
##       self.gm.connect_nodes (h_name, s_name)
##       self.gm.set_edge_name(h_name, s_name, arbitor_name)
##       return True
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

        #slaves = self.gm.get_connected_slaves(h_name)

        #if len(slaves.keys()):
        #  raise WishboneModelError(
        #    "host: %s is not connected to anything" % h_name)

        tags = self.gm.get_parameters(h_name)
        #print tags["arbitor_masters"]

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
##        h_node = self.gm.get_node(h_name)
##       print "node: " + str(h_node)
##       print "parameters: " + str(tags)

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

    def rename_slave(self, slave_type, index, new_name):
        """Finds a slave by type and index and renames it."""
        self.gm.rename_slave(slave_type, index, new_name)

    def add_slave(self, name, filename, slave_type, slave_index=-1):
        """Adds a slave to the specified bus at the specified index."""
        # Check if the slave_index makes sense.  If slave index s -1 then add it
        # to the next available location
        s_count = self.gm.get_number_of_slaves(slave_type)
        self.gm.add_node(name, NodeType.SLAVE, slave_type)

        slave = None

        if slave_index == -1:
            slave_index = s_count
        else:  # Add the slave wherever.
            if slave_type == SlaveType.PERIPHERAL:
                if slave_index == 0 and name != "DRT":
                    raise gm.SlaveError("Only the DRT can be at position 0")
                s_count = self.gm.get_number_of_peripheral_slaves()
                uname = self.get_unique_name(name,
                                             NodeType.SLAVE,
                                             slave_type,
                                             s_count - 1)
                slave = self.gm.get_node(uname)
                if slave_index < s_count - 1:
                    self.gm.move_peripheral_slave(slave.slave_index,
                                                  slave_index)
            elif slave_type == SlaveType.MEMORY:
                s_count = self.gm.get_number_of_memory_slaves()
                uname = self.get_unique_name(name,
                                             NodeType.SLAVE,
                                             slave_type,
                                             s_count - 1)
                slave = self.gm.get_node(uname)
                if slave_index < s_count - 1:
                    self.gm.move_slave(slave.slave_index,
                                       slave_index,
                                       SlaveType.MEMORY)

##       print "slave index: " + str(slave_index)

        uname = self.get_unique_name(name,
                                     NodeType.SLAVE,
                                     slave_type,
                                     slave_index)

        slave = self.gm.get_node(uname)
##       print "slave unique name: " + uname

        if filename is not None:
##           print "filename: " + filename
            if len(filename) > 0:
                parameters = vutils.get_module_tags(filename = filename,
                                                   bus = self.bus_type,
                                                   user_paths = self.get_user_paths())
                self.gm.set_parameters(uname, parameters)

                # Check if there are already some parameter declarations
                #within the project tags.
                slaves = {}
                if slave_type == SlaveType.PERIPHERAL:
                    if "SLAVES" in list(self.project_tags.keys()):
                        slaves = self.project_tags["SLAVES"]
                else:
                    if "MEMORY" in list(self.project_tags.keys()):
                        slaves = self.project_tags["MEMORY"]

                if name in list(slaves.keys()):
                    sd = slaves[name]
                    if "PARAMETERS" in list(sd.keys()):
                        pd = sd["PARAMETERS"]
                        for key in pd:
                            if key in list(parameters["parameters"].keys()):
                                parameters["parameters"][key] = pd[key]

        return uname

    def get_slave_parameters(self, slave_type, slave_index):
        sname = self.gm.get_slave_name_at(slave_type, slave_index)
        return self.gm.get_parameters(sname)

    def remove_slave(self, slave_type=SlaveType.PERIPHERAL, slave_index=0):
        """Removes slave from specified index."""
        #Check if there are any bindings to remove
        name = self.get_slave_name(slave_type, slave_index)
        bindings = self.get_slave_bindings(slave_type, slave_index)
        uname = self.get_unique_name(name, NodeType.SLAVE, slave_type, slave_index)
        bnames = bindings.keys()
        for bname in bnames:
            bind = bindings[bname]
        
            if bind["range"]:
                indexes = bind.keys()
                indexes.remove("range")
                for index in indexes:
                    self.gm.unbind_port(uname, bname, index)
                    
                break
            else:
                self.gm.unbind_port(uname, bname)
                break

        self.gm.remove_slave(slave_type, slave_index)
        return

    def move_slave(self,
                   slave_name=None,
                   from_slave_type=SlaveType.PERIPHERAL,
                   from_slave_index=0,
                   to_slave_type=SlaveType.PERIPHERAL,
                   to_slave_index=0):
        """Move slave from one place to another, the slave can be moved from one
        bus to another and the index position can be moved."""
        if to_slave_type == SlaveType.PERIPHERAL and to_slave_index == 0:
            return
        if slave_name is None:
            gm.SlaveError("a slave name must be specified")

        if from_slave_type == to_slave_type:
            # Simple move call.
            self.gm.move_slave(from_slave_index,
                               to_slave_index,
                               from_slave_type)
            return

        sname = self.gm.get_slave_name_at(from_slave_type, from_slave_index)

        #node = self.gm.get_node(sname)
        tags = self.gm.get_parameters(sname)

        # moving to the other bus, need to sever connections.
        self.remove_slave(from_slave_type, from_slave_index)
        filename = utils.find_module_filename(tags["module"], self.get_user_paths())
        filename = utils.find_rtl_file_location(filename, self.get_user_paths())
        self.add_slave(slave_name, filename, to_slave_type, to_slave_index)

    def generate_project(self):
        """Generates the output project that
        can be used to create a bit image."""
        self.save_config_file(self.filename)
        ibuilder.generate_project(self.filename, self.get_user_paths())

    def get_graph_manager(self):
        '''Returns the graph manager.'''
        return self.gm

    def get_unique_from_module_name(self, module_name):
        """Return the unique name associated with the module_name"""
        #Check the host interface
        #print "Checking host interface"
        if module_name == "Host Interface":
            return self.get_host_interface_name()
        #Check the peripherals slaves
        #print "Checking peripherals"
        pcount = self.get_number_of_peripheral_slaves()
        for i in range(pcount):
            name = self.get_slave_name(SlaveType.PERIPHERAL, i)
            if module_name == name:
                return get_unique_name(name, NodeType.SLAVE, SlaveType.PERIPHERAL, i)

        #Check the memory slaves
        #print "Checking memory"
        mcount = self.get_number_of_memory_slaves()
        for i in range(mcount):
            name = self.get_slave_name(SlaveType.MEMORY, i)
            if module_name == name:
                return get_unique_name(name, NodeType.SLAVE, SlaveType.MEMORY, i)


        raise SlaveError("Module with name %s not found" % module_name)


    def _update_module_ports(self, uname, module_name, user_paths = [], fn = None):
        d = self.gm.get_parameters(uname)
        if fn is None:
            fn = utils.find_module_filename(module_name, self.get_user_paths())
            fn = utils.find_rtl_file_location(fn, self.get_user_paths())
        new_d = vutils.get_module_tags(filename = fn,
                                      bus='wishbone',
                                      user_paths = self.get_user_paths())

        ports = cu.expand_ports(new_d["ports"])
        ports = cu.get_only_signal_ports(ports)
        params = self.gm.get_parameters(uname)
        
        bindings = self.gm.get_node_bindings(uname)
        params["ports"] = new_d["ports"]
        self.gm.set_parameters(uname, params)
        #print "\n\n"
        #print "ports: %s" % str(ports)
        #print "\n\n"
        #print "bindings: %s" % str(bindings)
        #print "\n\n"

        bkeys = bindings.keys()
        for b in bkeys:
            #print "Looking at: %s" % b
            if b not in ports.keys():
                #print "\t%s not in new ports" % b
                self.gm.unbind_port(uname, b)
                continue

            if ports[b]["range"] and not bindings[b]["range"]:
                #Used to be one now there is a range
                #print "\tnew port has range, old port doesn't"
                bind = bindings[b]["loc"]
                tk = []
                tk = copy.deepcopy(ports[b].keys())
                tk.remove("range")
                tk.sort()

                self.gm.unbind_port(uname, b)
                self.gm.bind_port(name = uname, 
                                  port_name = b, 
                                  loc = bind,
                                  index = tk[0])

            elif not ports[b]["range"] and bindings[b]["range"]:
                #print "\tnew port doesn't have range, old port does"
                #Used to have a range now there is only one
                tk = []
                tk = copy.deepcopy(bindings[b].keys())
                tk.remove("range")
                tk.sort()
                print "tk: %s" % str(tk)
                bind = bindings[b][tk[0]]["loc"]

                self.gm.unbind_port(name = uname, 
                                    port_name = b)
                #bind the lowest value to the only value
                self.gm.bind_port(name = uname,
                                  port_name = b,
                                  loc = bind)

            
            elif ports[b]["range"] and bindings[b]["range"]:
                #Both have ranges, now I need to adjust
                #print "check if all the values within bindings range are within the new ports"
                ok = copy.deepcopy(bindings[b].keys())
                ok.remove("range")
                nk = copy.deepcopy(ports[b].keys())
                nk.remove("range")
                
                #print "bindings[d].keys() = %s" % str(ok)
                #print "ports[d].keys() = %s" % str(nk)


                good = True
                for a in ok:
                    #print "Checking %s with %s" % (str(a), str(nk))
                    if a not in nk:
                        good = False

                if good:
                    #print "All old items within new items"
                    continue

                #get all the bindings items in a list
                td = {}
                for a in ok:
                    td[a] = {}
                    td[a] = bindings[b][a]["loc"]
                indexes = copy.deepcopy(td.keys())
                indexes.sort()
                self.gm.unbind_port(uname, b)

                new_indexes = copy.deepcopy(ports[b].keys())
                new_indexes.remove("range")
                new_indexes.sort()
                lold = len(indexes)
                #print "Length of old: %d" % lold
                lnew = len(new_indexes)
                #print "Length of new: %d" % lnew
                first = new_indexes[0]
                length = lold
                if lnew < lold:
                    length = lnew
                fin = length + new_indexes[0]
                #print "start: %d" % new_indexes[0]
                #print "length: %d" % fin
                for i in range (length):
                    #print "old: %d" % indexes[i]
                    #print "new index: %d" % new_indexes[i]
                    self.gm.bind_port(name = uname,
                                      port_name = b,
                                      loc = td[indexes[i]],
                                      index = new_indexes[i])


    def update_module_ports(self, module_name, user_paths = [], fn = None):
        #Go through the host interface first
        name = "Host Interface"
        main_dict = self.gm.get_nodes_dict()
        uname = self.get_unique_name(name, NodeType.HOST_INTERFACE)
        d = self.gm.get_parameters(uname)
        #Check if any module in the model has this module name
        if d["module"] == module_name:
            #print "Host Interface needs update"
            #if we do find this name then go through the ports and see if there is any difference
            self._update_module_ports(uname, module_name, user_paths, fn)
            return

        pcount = self.get_number_of_peripheral_slaves()
        for i in range(pcount):
            name = self.get_slave_name(SlaveType.PERIPHERAL, i)
            uname = get_unique_name(name, NodeType.SLAVE, SlaveType.PERIPHERAL, i)
            d = self.gm.get_parameters(uname)
            if d["module"] == module_name:
                #print "found: %s" % name
                #if we do find this name then go through the ports and see if there is any difference
                self._update_module_ports(uname, module_name, user_paths, fn)

        mcount = self.get_number_of_memory_slaves()
        for i in range(mcount):
            name = self.get_slave_name(SlaveType.MEMORY, i)
            uname = get_unique_name(name, NodeType.SLAVE, SlaveType.MEMORY, i)
            d = self.gm.get_parameters(uname)
            if d["module"] == module_name:
                #print "found: %s" % name
                #if we do find this name then go through the ports and see if there is any difference
                self._update_module_ports(uname, module_name, user_paths, fn)

          

