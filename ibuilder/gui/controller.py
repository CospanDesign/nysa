#!/usr/bin/env python
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, "lib"))

#Inner package modules
from ibuilder_error import ModuleNotFound
from ibuilder_error import SlaveError

import graph_manager as gm

from graph_manager import GraphManager
from graph_manager import SlaveType
from graph_manager import NodeType
from graph_manager import get_unique_name

import utils


class Controller():
  def __init__(self):
    self.new_design()
    self.filename = ""

    # Add some variable functions for dependency injection.
    self.get_board_config = saputils.get_board_config
    self.get_unique_name = get_unique_name



  def new_design(self):
    self.gm = GraphManager()
    self.bus_type = "wishbone"
    self.tags = {}
    self.file_name = ""
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

  def set_host_interface(self, host_interface_name, debug = False):
    """Sets the host interface type.  If host_interface_name is not a valid
    module name (or cannot be found for whatever reason), throws a
    ModuleNotFound exception."""
    hi_name = self.get_unique_name("Host Interface", NodeType.HOST_INTERFACE)

    node_names = self.gm.get_node_names()
    if hi_name not in node_names:
      self.gm.add_node("Host Interface", NodeType.HOST_INTERFACE)

    # Check if the host interface is valid.
    file_name = saputils.find_module_filename(host_interface_name)
    file_name = saputils.find_rtl_file_location(file_name)

    # If the host interface is valid then get all the tags ...
    parameters = saputils.get_module_tags(filename = file_name,
                                          bus = self.get_bus_type())
    # ... and set them up.
    self.gm.set_parameters(hi_name, parameters)
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
    for k,v in bind:
      bind_dict[k] = v

    # Get host interface bindings.
    hi_name = self.get_unique_name("Host Interface", NodeType.HOST_INTERFACE)
    hib = self.gm.get_node_bindings(hi_name)
    for k,v in hib.iteritems():
      bind_dict[k] = v

    # Get all the peripheral slave bindings.
    p_count = self.get_number_of_slaves(SlaveType.PERIPHERAL)
    for i in xrange(p_count):
      slave = self.gm.get_slave_at(i, SlaveType.PERIPHERAL)
      pb = self.gm.get_node_bindings(slave.unique_name)
      for key in pb.keys():
        bind_dict[key] = pb[key]

    # Get all the memory slave bindings.
    m_count = self.get_number_of_slaves(SlaveType.MEMORY)
    for i in xrange(m_count):
      slave = self.gm.get_slave_at(i, SlaveType.MEMORY)
      mb = self.gm.get_node_bindings(slave.unique_name)
      for key in mb.keys():
        bind_dict[key] = mb[key]

    return bind_dict

  def set_binding(self, node_name, port_name, pin_name):
    """Add a binding between the port and the pin."""
    node = self.gm.get_node(node_name)
    ports = node.parameters["ports"]

    pn = port_name.partition("[")[0]
    if ":" in port_name:
      raise SlaveError("Sorry I don't support vectors yet :( port_name = %s" % port_name)

    if pn not in ports.keys():
      raise SlaveError("port %s is not in node %s" % (port_name, node.name))

#    if pin_name not in pt:
#      raise SlaveError("pin %s is not in the constraints" % (pin_name))

    direction = ports[pn]["direction"]

    bind_dict = self.get_master_bind_dict()
#    print "bind dict keys: " + str(bind_dict.keys())
    for pname in bind_dict.keys():
#    if port_name in bind_dict.keys():
      if port_name == bind_dict[pname]["pin"]:
        raise SlaveError("port %s is already bound")

    # Also check if there is a vector in the binding list and see if I'm in
    # range of that vector.
    for key in bind_dict.keys():
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
          raise SlaveError("Sorry I don't support vectors yet :( port_name = %s" % port_name)

        index = int(index)
      else:
        index = -1

#      print "index: " + str(index)

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
          raise SlaveError("Conflict with the binding %s and the port %s" % (key, port_name))

        if index >= low and index <= high:
          raise SlaveError("Conflict with the binding %s and the port %s" % (key, port_name))

      if key_index == index:
        raise SlaveError("Conflict with the binding %s and the port %s" % (key, port_name))

#    bind_dict = node.bindings
    self.gm.bind_port(node_name, port_name, pin_name)
#    bind_dict[port_name] = {}
#    bind_dict[port_name]["port"] = pin_name
#    bind_dict[port_name]["direction"] = direction
#    print "setting up %s to pin %s as an %s" % (port_name, pin_name, direction)

  def unbind_port(self, node_name, port_name):
    """Remove a binding with the port name."""
#    node = self.gm.get_node(node_name)
#    bind_dict = node.bindings
#    bind_dict[port_name] = {}
#    if port_name not in bind_dict.keys():
#      raise SlaveError("port %s is not in the binding dictionary for node %s" % (port_name, node.name))
    self.gm.unbind_port(node_name, port_name)
#    del bind_dict[port_name]

  def get_host_interface_name(self):
    hi_name = self.get_unique_name("Host Interface", NodeType.HOST_INTERFACE)
    hi = self.gm.get_node(hi_name)
    return hi.parameters["module"]

  def get_slave_name(self, slave_type, slave_index):
    s_name = self.gm.get_slave_name_at(slave_index, slave_type)
    slave = self.gm.get_node(s_name)
    return slave.name

  def is_arb_master_connected(self, slave_name, arb_host):
    slaves = self.gm.get_connected_slaves(slave_name)
    for key in slaves.keys():
      edge_name = self.gm.get_edge_name(slave_name, slaves[key])
      if (arb_host == edge_name):
        return True
    return False

  def add_arbitrator_by_name(self, host_name, arbitrator_name, slave_name):
    tags = self.gm.get_parameters(host_name)
    if arbitrator_name not in tags["arbitrator_masters"]:
      return False

    self.gm.connect_nodes (host_name, slave_name)
    self.gm.set_edge_name(host_name, slave_name, arbitrator_name)
    return True

  def add_arbitrator(self, host_type, host_index,
                     arbitrator_name, slave_type, slave_index):
    """Adds an arbitrator and attaches it between the host and the slave."""
    h_name = self.gm.get_slave_name_at(host_index, host_type)
#    tags = self.gm.get_parameters(h_name)
#    print "h_name: " + h_name
#    if arbitrator_name not in tags["arbitrator_masters"]:
#      return False

    s_name = self.gm.get_slave_name_at(slave_index, slave_type)
#    self.gm.connect_nodes (h_name, s_name)
#    self.gm.set_edge_name(h_name, s_name, arbitrator_name)
#    return True
    return self.add_arbitrator_by_name(h_name, arbitrator_name, s_name)

  def get_connected_arbitrator_slave(self, host_name, arbitrator_name):
    tags = self.gm.get_parameters(host_name)
    if arbitrator_name not in tags["arbitrator_masters"]:
      SlaveError("This slave has no arbitrator masters")

    slaves = self.gm.get_connected_slaves(host_name)
    for arb_name in slaves.keys():
      slave = slaves[arb_name]
      edge_name = self.gm.get_edge_name(host_name, slave)
      if edge_name == arbitrator_name:
        return slave
    return None

  def get_connected_arbitrator_name(self, host_type, host_index,
                                    slave_type, slave_index):
    h_name = self.gm.get_slave_name_at(host_index, host_type)
    tags = self.gm.get_parameters(h_name)
    if arbitrator_name not in tags["arbitrator_masters"]:
      return ""
    s_name = self.gm.get_slave_name_at(slave_index, slave_type)
    return self.get_edge_name(h_name, s_name)

  def remove_arbitrator_by_arb_master(self, host_name, arb_name):
    slave_name = self.get_connected_arbitrator_slave(  host_name, arb_name)
    self.remove_arbitrator_by_name(host_name, slave_name)

  def remove_arbitrator_by_name(self, host_name, slave_name):
    self.gm.disconnect_nodes(host_name, slave_name)

  def remove_arbitrator(self, host_type, host_index, slave_type, slave_index):
    """Finds and removes the arbitrator from the host."""
    h_name = gm.get_slave_name_at(host_index, host_type)
    s_name = gm.get_slave_name_at(slave_index, slave_type)
    remove_arbitrator_by_name(h_name, s_name)

  def is_active_arbitrator_host(self, host_type, host_index):
    h_name = self.gm.get_slave_name_at(host_index, host_type)
    tags = self.gm.get_parameters(h_name)
    h_node = self.gm.get_node(h_name)
#    print "node: " + str(h_node)
#    print "parameters: " + str(tags)

    if h_name not in tags["arbitrator_masters"]:
      if len(tags["arbitrator_masters"]) == 0:
        return False

    if not self.gm.is_slave_connected_to_slave(h_name):
      return False

    return True

  def get_slave_name_by_unique(self, slave_name):
    node = self.gm.get_node(slave_name)
    return node.name

  def get_arbitrator_dict(self, host_type, host_index):
    if not self.is_active_arbitrator_host(host_type, host_index):
      return {}

    h_name = self.gm.get_slave_name_at(host_index, host_type)
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
    else: # Add the slave wherever.
      if slave_type == SlaveType.PERIPHERAL:
        if slave_index == 0 and name != "DRT":
          raise gm.SlaveError("Only the DRT can be at position 0")
        s_count = self.gm.get_number_of_peripheral_slaves()
        uname = self.get_unique_name(name, NodeType.SLAVE, slave_type, s_count - 1)
        slave = self.gm.get_node(uname)
        if slave_index < s_count - 1:
          self.gm.move_peripheral_slave(  slave.slave_index, slave_index)
      elif slave_type == SlaveType.MEMORY:
        s_count = self.gm.get_number_of_memory_slaves()
        uname = self.get_unique_name(name, NodeType.SLAVE, slave_type, s_count - 1)
        slave = self.gm.get_node(uname)
        if slave_index < s_count - 1:
          self.gm.move_slave(slave.slave_index, slave_index, SlaveType.MEMORY)

#    print "slave index: " + str(slave_index)

    uname = self.get_unique_name(name, NodeType.SLAVE, slave_type, slave_index)

    slave = self.gm.get_node(uname)
#    print "slave unique name: " + uname

    if filename is not None:
#      print "filename: " + filename
      if len(filename) > 0:
        parameters = saputils.get_module_tags(filename, self.bus_type)
        self.gm.set_parameters(uname, parameters)

        # Check if there are already some parameter declarations within the
        # project tags.
        slaves = {}
        if slave_type == SlaveType.PERIPHERAL:
          if "SLAVES" in self.project_tags.keys():
            slaves = self.project_tags["SLAVES"]
        else:
          if "MEMORY" in self.project_tags.keys():
            slaves = self.project_tags["MEMORY"]

        if name in slaves.keys():
          sd = slaves[name]
          if "PARAMETERS" in sd.keys():
            pd = sd["PARAMETERS"]
            for key in pd.keys():
              if key in parameters["parameters"].keys():
                parameters["parameters"][key] = pd[key]

    return uname

  def remove_slave(self, slave_type = SlaveType.PERIPHERAL, slave_index=0):
    """Removes slave from specified index."""
    self.gm.remove_slave(slave_index, slave_type)
    return

  def move_slave(self, slave_name = None,
                 from_slave_type = SlaveType.PERIPHERAL,
                 from_slave_index = 0,
                 to_slave_type = SlaveType.PERIPHERAL,
                 to_slave_index = 0):
    """Move slave from one place to another, the slave can be moved from one
    bus to another and the index position can be moved."""
    if to_slave_type == SlaveType.PERIPHERAL and to_slave_index == 0:
      return
    if slave_name is None:
      gm.SlaveError("a slave name must be specified")

    if from_slave_type == to_slave_type:
      # Simple move call.
      self.gm.move_slave(from_slave_index, to_slave_index, from_slave_type)
      return

    sname = self.gm.get_slave_name_at(from_slave_index, from_slave_type)

    node = self.gm.get_node(sname)
    tags = self.gm.get_parameters(sname)

    # moving to the other bus, need to sever connections.
    self.remove_slave(from_slave_type, from_slave_index)
    filename = saputils.find_module_filename(tags["module"])
    filename = saputils.find_rtl_file_location(filename)
    self.add_slave(slave_name, filename, to_slave_type, to_slave_index)

  def generate_project(self):
    """Generates the output project that can be used to create a bit image."""
    self.save_config_file(self.filename)
    try:
      saplib.generate_project(self.filename)
    except IOError as err:
      print "File Error: " + str(err)

  def get_graph_manager(self):
    '''Returns the graph manager.'''
    return self.gm

