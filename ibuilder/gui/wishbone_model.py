#!/usr/bin/env python
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, "lib"))
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

#Inner package modules
from lib import ibuilder

from ibuilder_error import ModuleNotFound
from ibuilder_error import SlaveError

from .gui_error import WishboneModelError

from . import graph_manager as gm

from .graph_manager import GraphManager
from .graph_manager import SlaveType
from .graph_manager import NodeType
from .graph_manager import get_unique_name

import utils


class WishboneModel():
    def __init__(self, board_name=None, config_file=None):
        self.project_tags = {}
        self.new_design()
        self.filename = ""

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
            filename = utils.find_rtl_file_location("device_rom_table.v")
        except ModuleNotFound:
            if debug:
                print ("device_rom_table.v not found")
            raise WishboneModelError("DRT module was not found")

        parameters = utils.get_module_tags(filename=filename,
                                           bus=self.get_bus_type())
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
                    filename = utils.find_rtl_file_location(filename)

                uname = self.add_slave(slave_name,
                                       filename,
                                       SlaveType.PERIPHERAL)

                # Add the bindings from the config file.
                skeys = list(self.project_tags["SLAVES"][slave_name].keys())
##               print "adding bindings"
##               if "bind" not in skeys:
##                 self.project_tags["SLAVES"][slave_name]["bind"] = {}

                if "bind" in skeys:
##                  print "found binding"
                    bindings = {}
                    bindings = self.project_tags["SLAVES"][slave_name]["bind"]
                    self.gm.set_config_bindings(uname, bindings)
                else:
                    self.project_tags["SLAVES"][slave_name]["bind"] = {}

        # Load all the memory slaves.
        sm_count = self.gm.get_number_of_memory_slaves()
        if debug:
            print(("loading %d memory slaves" % sm_count))

        if "MEMORY" in self.project_tags:
            for slave_name in self.project_tags["MEMORY"]:

                filename = self.project_tags["MEMORY"][slave_name]["filename"]
                filename = utils.find_rtl_file_location(filename)
                uname = self.add_slave(slave_name,
                                        filename,
                                        SlaveType.MEMORY,
                                        slave_index=-1)

                # Add the bindings from the config file.
                mkeys = list(self.project_tags["MEMORY"][slave_name].keys())
                if "bind" in mkeys:
                    bindings = self.project_tags["MEMORY"][slave_name]["bind"]
                    self.gm.set_config_bindings(uname, bindings)
                else:
                    self.project_tags["MEMORY"][slave_name]["bind"] = {}

        # Check if there is a host interface defined.
        if "INTERFACE" in self.project_tags:
            filename = utils.find_rtl_file_location(
                            self.project_tags["INTERFACE"]["filename"])
            if debug:
                print (("Loading interface: %s" % filename))
            parameters = utils.get_module_tags(
                            filename=filename, bus=self.get_bus_type())
            self.set_host_interface(parameters["module"])
            if "bind" in list(self.project_tags["INTERFACE"].keys()):
                self.gm.set_config_bindings(hi_name,
                    self.project_tags["INTERFACE"]["bind"])
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
##      bind_dict = self.get_master_bind_dict()

        for i in range(0, p_count):
            #print "apply slave tags to project: %d:" % i
            sc_slave = self.gm.get_slave_at(i, SlaveType.PERIPHERAL)
            uname = sc_slave.unique_name
            name = sc_slave.name
            if debug:
                print (("name: %s" % str(name)))
            if debug:
                print (("Projct tags: %s" % str(self.project_tags)))
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
            if debug:
                print (("bind contents: %s" % str(bindings)))
            for p in bindings:
                pt_slave["bind"][p] = {}
                pt_slave["bind"][p]["port"] = bindings[p]["pin"]
                pt_slave["bind"][p]["direction"] = bindings[p]["direction"]

            # Add filenames.
            module = sc_slave.parameters["module"]
            filename = utils.find_module_filename(module)
            pt_slave["filename"] = filename

      # Memory BUS
        for i in range(0, m_count):
            sc_slave = self.gm.get_slave_at(i, SlaveType.MEMORY)
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
            if debug:
                print (("bind contents: %s" % str(bindings)))
            for p in bindings:
                pt_slave["bind"][p] = {}
                pt_slave["bind"][p]["port"] = bindings[p]["pin"]
                pt_slave["bind"][p]["direction"] = bindings[p]["direction"]

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
        filename = utils.find_module_filename(host_interface_name)

        #XXX: Should this be the full file name??
        self.project_tags["INTERFACE"]["filename"] = filename
        filename = utils.find_rtl_file_location(filename)

        #print "hi project tags: %s" % str(self.project_tags["INTERFACE"])
        # If the host interface is valid then get all the tags ...
        parameters = utils.get_module_tags(filename=filename,
                                              bus=self.get_bus_type())
        # ... and set them up.
        self.gm.set_parameters(hi_name, parameters, debug=debug)
        return True

    def get_master_bind_dict(self):
        """Combine the dictionary from:
          - project
          - host interface
          - peripheral slaves
          - memory slaves"""

        # The dictionary to put the entries in and return.
        bind_dict = {}

        # Get project bindings.
        bind = self.project_tags["bind"]
        for k, v in bind:
            bind_dict[k] = v

        # Get host interface bindings.
        hi_name = self.get_unique_name("Host Interface",
                                       NodeType.HOST_INTERFACE)
        hib = self.gm.get_node_bindings(hi_name)
        for k, v in list(hib.items()):
            bind_dict[k] = v

        # Get all the peripheral slave bindings.
        p_count = self.get_number_of_slaves(SlaveType.PERIPHERAL)
        for i in range(p_count):
            slave = self.gm.get_slave_at(i, SlaveType.PERIPHERAL)
            pb = self.gm.get_node_bindings(slave.unique_name)
            for key in pb:
                bind_dict[key] = pb[key]

        # Get all the memory slave bindings.
        m_count = self.get_number_of_slaves(SlaveType.MEMORY)
        for i in range(m_count):
            slave = self.gm.get_slave_at(i, SlaveType.MEMORY)
            mb = self.gm.get_node_bindings(slave.unique_name)
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

    def set_binding(self, node_name, port_name, pin_name):
        """Add a binding between the port and the pin."""
        node = self.gm.get_node(node_name)
        ports = node.parameters["ports"]

        pn = port_name.partition("[")[0]
        if ":" in port_name:
            raise SlaveError(
                "Sorry I don't support vectors yet :( port_name = %s" %
                port_name)

        if pn not in ports:
            raise SlaveError("port %s is not in node %s" %
                (port_name, node.name))

##       if pin_name not in pt:
##         raise SlaveError("pin %s is not in the constraints" % (pin_name))

        #direction = ports[pn]["direction"]

        bind_dict = self.get_master_bind_dict()
##       print "bind dict keys: " + str(bind_dict.keys())
        for pname in bind_dict:
##       if port_name in bind_dict.keys():
            if port_name == bind_dict[pname]["pin"]:
                raise SlaveError("port %s is already bound")

        # Also check if there is a vector in the binding list and see if I'm in
        # range of that vector.
        for key in bind_dict:
            low = -1
            high = -1
            index = -1
            key_index = -1

            if pn not in key:
                continue

            index = port_name.partition("[")[2]
            if len(index) > 0:

                index = index.partition("]")[0]
                if ":" in index:
                    raise SlaveError(
                        "Sorry I don't support vectors yet :( port_name = %s" %
                        port_name)

                index = int(index)
            else:
                index = -1

##              print "index: " + str(index)

            if "[" in key:
                key_index = key.partition("[")[2]
                key_index = key_index.partition("]")[0]
                if ":" in key_index:
                    low, nothing, high = key_index.partition(":")
                    low = int(low)
                    high = int(high)
                    key_index = -1
                else:
                    key_index = int(key_index)

            # Either the binding has no [] (index) or it is a range.
            if key_index == -1:
                # If the index has no [] (no index) or it is a range.
                if index == -1:
                    # bad
                    raise SlaveError(
                        "Conflict with the binding %s and the port %s" %
                        (key, port_name))

                if index >= low and index <= high:
                    raise SlaveError(
                        "Conflict with the binding %s and the port %s" %
                        (key, port_name))

                if key_index == index:
                    raise SlaveError(
                        "Conflict with the binding %s and the port %s" %
                        (key, port_name))

##       bind_dict = node.bindings
        self.gm.bind_port(node_name, port_name, pin_name)
##       bind_dict[port_name] = {}
##       bind_dict[port_name]["port"] = pin_name
##       bind_dict[port_name]["direction"] = direction
##       print "setting up %s to pin %s as an %s" % (port_name,
##                                                   pin_name,
##                                                   direction)

    def unbind_port(self, node_name, port_name):
        """Remove a binding with the port name."""
##      node = self.gm.get_node(node_name)
##      bind_dict = node.bindings
##      bind_dict[port_name] = {}
##      if port_name not in bind_dict.keys():
##        raise SlaveError(
##            "port %s is not in the binding dictionary for node %s" %
##                 (port_name, node.name))
        self.gm.unbind_port(node_name, port_name)
##      del bind_dict[port_name]

    def unbind_all(self, debug=False):
        if debug:
            print ("unbind all")
        mbd = self.get_master_bind_dict()
        if debug:
            print (("Master Bind Dict: %s" % str(mbd)))
        node_names = self.gm.get_node_names()
        for nn in node_names:
            nb = self.gm.get_node_bindings(nn)
            for b in nb:
                if debug:
                    print (("Unbindig %s" % b))
                self.unbind_port(nn, b)

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
                parameters = utils.get_module_tags(filename, self.bus_type)
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
        self.gm.remove_slave(slave_index, slave_type)
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
        filename = utils.find_module_filename(tags["module"])
        filename = utils.find_rtl_file_location(filename)
        self.add_slave(slave_name, filename, to_slave_type, to_slave_index)

    def generate_project(self):
        """Generates the output project that
        can be used to create a bit image."""
        self.save_config_file(self.filename)
        ibuilder.generate_project(self.filename)

    def get_graph_manager(self):
        '''Returns the graph manager.'''
        return self.gm
