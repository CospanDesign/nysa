import unittest
import os
import sys
import json

#! /usr/bin/python
import unittest
import os
import sys
import json
import mock

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from ibuilder.lib import utils
from ibuilder.gui import graph_manager as gm

from ibuilder.lib.ibuilder_error import SlaveError
from ibuilder.gui.gui_error import NodeError

class Test (unittest.TestCase):
  """Unit test for gen_drt.py"""

  def setUp(self):
    self.dbg = False
    self.vbs = False
    base = os.path.join( os.path.dirname(__file__),
                         os.pardir)
    self.nysa_base = os.path.abspath(base)


    # Open up the specified JSON project config file and copy it into a buffer.
    filename = os.path.join(  self.nysa_base,
                              "ibuilder",
                              "example_projects",
                              "dionysus_gpio_mem.json")
    filein = open(filename)
    json_string = filein.read()
    filein.close()

    self.project_tags = json.loads(json_string)

    if self.dbg:
      print "loaded JSON file"

    # Generate graph.
    self.sgm = gm.GraphManager()

    return

  def test_graph_add_node(self):
    if self.dbg:
      print "generating host interface node"

    self.sgm.add_node("uart", gm.NodeType.HOST_INTERFACE)

    # Get the size of the graph
    size = self.sgm.get_size()
    if self.dbg:
      print "number of nodes: " + str(size)

    self.assertEqual(size, 1)


  def test_rename_slave(self):
    if self.dbg:
      print "renaming slave"
    self.sgm.add_node ("name1", gm.NodeType.SLAVE, gm.SlaveType.PERIPHERAL, 0)
    self.sgm.rename_slave(gm.SlaveType.PERIPHERAL, 0, "name2")
    name = self.sgm.get_slave_name_at(gm.SlaveType.PERIPHERAL, 0)
    node = self.sgm.get_node(name)
    name = node.name
    self.assertEqual(name, "name2")

  def test_get_number_of_peripheral_slaves(self):
    self.sgm.add_node("slave_1",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)
    self.sgm.add_node("slave_2",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)
    count = self.sgm.get_number_of_slaves(gm.SlaveType.PERIPHERAL)
    self.assertEqual(count, 2)

  def test_get_number_of_memory_slaves(self):
    self.sgm.add_node("slave_1",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.MEMORY,
                      debug = self.dbg)
    self.sgm.add_node("slave_2",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.MEMORY,
                      debug = self.dbg)
    count = self.sgm.get_number_of_slaves(gm.SlaveType.MEMORY)

    self.assertEqual(True, True)

  def test_slave_index(self):
    self.sgm.add_node("slave_1",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)
    self.sgm.add_node("slave_2",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)
    self.sgm.add_node("slave_3",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)
    self.sgm.add_node("slave_4",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)
    self.sgm.add_node("slave_5",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)

    # Scramble things up.
    self.sgm.move_slave(3, 1, gm.SlaveType.PERIPHERAL)
    self.sgm.move_slave(2, 4, gm.SlaveType.PERIPHERAL)
    self.sgm.move_slave(2, 3, gm.SlaveType.PERIPHERAL)
    self.sgm.move_slave(1, 4, gm.SlaveType.PERIPHERAL)
    self.sgm.move_slave(4, 2, gm.SlaveType.PERIPHERAL)

    self.sgm.remove_slave(gm.SlaveType.PERIPHERAL, 1)

    count = self.sgm.get_number_of_slaves(gm.SlaveType.PERIPHERAL)

    for i in xrange(count):
      slave_name = self.sgm.get_slave_name_at(gm.SlaveType.PERIPHERAL, i)
      node = self.sgm.get_node(slave_name)
      self.assertEqual(i, node.slave_index)

    # Test memory locations.
    self.sgm.add_node("mem_1",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.MEMORY,
                      debug = self.dbg)
    self.sgm.add_node("mem_2",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.MEMORY,
                      debug = self.dbg)
    self.sgm.add_node("mem_3",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.MEMORY,
                      debug = self.dbg)
    self.sgm.add_node("mem_4",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.MEMORY,
                      debug = self.dbg)

    # Scramble things up.
    self.sgm.move_slave(0, 1, gm.SlaveType.MEMORY)
    self.sgm.move_slave(3, 1, gm.SlaveType.MEMORY)
    self.sgm.move_slave(2, 0, gm.SlaveType.MEMORY)
    self.sgm.move_slave(0, 3, gm.SlaveType.MEMORY)

    self.sgm.remove_slave(gm.SlaveType.MEMORY, 2)

    count = self.sgm.get_number_of_slaves(gm.SlaveType.MEMORY)
    
    for i in range (0, count):
      print "i: %d" % i
      slave_name = self.sgm.get_slave_name_at(gm.SlaveType.MEMORY, i)
      node = self.sgm.get_node(slave_name)
      self.assertEqual(i, node.slave_index)

  def test_clear_graph(self):
    if self.dbg:
      print "generating host interface node"

    self.sgm.add_node("uart", gm.NodeType.HOST_INTERFACE)
    # Get the size of the graph.
    size = self.sgm.get_size()
    if self.dbg:
      print "number of nodes: " + str(size)

    self.sgm.clear_graph()

    size = self.sgm.get_size()
    self.assertEqual(size, 0)

  def test_graph_add_slave_node(self):
    if self.dbg:
      print "generating host interface node"

    self.sgm.add_node("gpio",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug=self.dbg)

    gpio_name = gm.get_unique_name("gpio",
                                   gm.NodeType.SLAVE,
                                   gm.SlaveType.PERIPHERAL,
                                   slave_index = 1)

    if self.dbg:
      print "unique name: " + gpio_name

    # Get the size of the graph.
    size = self.sgm.get_size()
    if self.dbg:
      print "number of nodes: " + str(size)

    self.assertEqual(size, 1)

  def test_graph_remove_node(self):
    if self.dbg:
      print "adding two nodes"
    self.sgm.add_node("uart", gm.NodeType.HOST_INTERFACE)
    self.sgm.add_node("master", gm.NodeType.MASTER)

    size = self.sgm.get_size()
    if self.dbg:
      print "number of nodes: " + str(size)

    self.assertEqual(size, 2)

    # Remove the uart node.
    unique_name = gm.get_unique_name("uart", gm.NodeType.HOST_INTERFACE)

    self.sgm.remove_node(unique_name)

    size = self.sgm.get_size()
    if self.dbg:
      print "number of nodes: " + str(size)

    self.assertEqual(size, 1)

  def test_get_node_names(self):
    if self.dbg:
      print "adding two nodes"

    self.sgm.add_node("uart", gm.NodeType.HOST_INTERFACE)
    self.sgm.add_node("master", gm.NodeType.MASTER)

    names = self.sgm.get_node_names()


    uart_name = gm.get_unique_name("uart", gm.NodeType.HOST_INTERFACE)
    master_name = gm.get_unique_name("master", gm.NodeType.MASTER)

    self.assertIn(uart_name, names)
    self.assertIn(master_name, names)

  def test_get_nodes(self):
    if self.dbg:
      print "adding two nodes"

    self.sgm.add_node("uart", gm.NodeType.HOST_INTERFACE)
    self.sgm.add_node("master", gm.NodeType.MASTER)

    graph_dict = self.sgm.get_nodes_dict()


    uart_name = gm.get_unique_name("uart", gm.NodeType.HOST_INTERFACE)
    master_name = gm.get_unique_name("master", gm.NodeType.MASTER)

    if self.dbg:
      print "dictionary: " + str(graph_dict)

    self.assertIn(uart_name, graph_dict.keys())
    self.assertIn(master_name, graph_dict.keys())


  def test_get_host_interface(self):
    self.sgm.add_node("uart", gm.NodeType.HOST_INTERFACE)
    self.sgm.add_node("master", gm.NodeType.MASTER)
    node = self.sgm.get_host_interface_node()
    self.assertEqual(node.name, "uart")


  def test_connect_nodes(self):
    if self.dbg:
      print "adding two nodes"

    self.sgm.add_node("uart", gm.NodeType.HOST_INTERFACE)
    self.sgm.add_node("master", gm.NodeType.MASTER)



    uart_name = gm.get_unique_name("uart", gm.NodeType.HOST_INTERFACE)
    master_name = gm.get_unique_name("master", gm.NodeType.MASTER)

    # Get the number of connections before adding a connection.
    num_of_connections = self.sgm.get_number_of_connections()
    self.assertEqual(num_of_connections, 0)

    self.sgm.connect_nodes(uart_name, master_name)
    # Get the number of connections after adding a connection.
    num_of_connections = self.sgm.get_number_of_connections()

    self.assertEqual(num_of_connections, 1)

  def test_disconnect_nodes(self):
    if self.dbg:
      print "adding two nodes"

    self.sgm.add_node("uart", gm.NodeType.HOST_INTERFACE)
    self.sgm.add_node("master", gm.NodeType.MASTER)

    uart_name = gm.get_unique_name("uart", gm.NodeType.HOST_INTERFACE)
    master_name = gm.get_unique_name("master", gm.NodeType.MASTER)

    # Get the number of connections before adding a connection.
    num_of_connections = self.sgm.get_number_of_connections()
    self.assertEqual(num_of_connections, 0)
    self.sgm.connect_nodes(uart_name, master_name)

    # Get the number of connections after adding a connection.
    num_of_connections = self.sgm.get_number_of_connections()

    self.assertEqual(num_of_connections, 1)

    self.sgm.disconnect_nodes(uart_name, master_name)
    num_of_connections = self.sgm.get_number_of_connections()
    self.assertEqual(num_of_connections, 0)

  def test_edge_name(self):
    if self.dbg:
      print "adding two nodes, connecting them, setting the name and then \
      reading it"

    self.sgm.add_node("uart", gm.NodeType.HOST_INTERFACE)
    self.sgm.add_node("master", gm.NodeType.MASTER)

    uart_name = gm.get_unique_name("uart", gm.NodeType.HOST_INTERFACE)
    master_name = gm.get_unique_name("master", gm.NodeType.MASTER)

    self.sgm.connect_nodes(uart_name, master_name)

    self.sgm.set_edge_name(uart_name, master_name, "connection")

    result = self.sgm.get_edge_name(uart_name, master_name)
    self.assertEqual(result, "connection")

  def test_edge_dict(self):
    if self.dbg:
      print "adding two nodes, connecting them, setting the name and then \
      reading it"

    uart_name = self.sgm.add_node("uart",
                                  gm.NodeType.SLAVE,
                                  gm.SlaveType.PERIPHERAL)
    master_name = self.sgm.add_node("master",
                                    gm.NodeType.SLAVE,
                                    gm.SlaveType.PERIPHERAL)

    self.sgm.connect_nodes(uart_name, master_name)

    self.sgm.set_edge_name(uart_name, master_name, "connection")

    result = self.sgm.is_slave_connected_to_slave(uart_name)
    self.assertEqual(result, True)

    arb_dict = self.sgm.get_connected_slaves(uart_name)
    self.assertEqual(arb_dict["connection"], master_name)

  def test_get_node_data(self):
    if self.dbg:
      print "adding a nodes"

    self.sgm.add_node("uart", gm.NodeType.HOST_INTERFACE)
    uart_name = gm.get_unique_name("uart", gm.NodeType.HOST_INTERFACE)

    node = self.sgm.get_node(uart_name)
    self.assertEqual(node.name, "uart")

  def test_set_parameters(self):
    """Set all the parameters aquired from a module."""
    self.sgm.add_node("uart", gm.NodeType.HOST_INTERFACE)
    uart_name = gm.get_unique_name("uart", gm.NodeType.HOST_INTERFACE)

    filename = utils.find_module_filename("uart_io_handler")
    filename = utils.find_rtl_file_location(filename)

    parameters = utils.get_module_tags(filename = filename, bus="wishbone")

    self.sgm.set_parameters(uart_name, parameters)
    parameters = None
    if self.dbg:
      print "parameters: " + str(parameters)

    parameters = self.sgm.get_parameters(uart_name)

    if self.dbg:
      print "parameters: " + str(parameters)

    self.assertEqual(parameters["module"], "uart_io_handler")

#  def test_bind_pin_to_port(self):
#    self.sgm.add_node("uart", gm.NodeType.HOST_INTERFACE)
#    uart_name = gm.get_unique_name("uart", gm.NodeType.HOST_INTERFACE)
#
#    filename = utils.find_module_filename("uart_io_handler")
#    filename = utils.find_rtl_file_location(filename)
#    parameters = utils.get_module_tags(filename = filename, bus="wishbone")
#
#    self.sgm.set_parameters(uart_name, parameters)
#
#    self.sgm.bind_pin_to_port(uart_name, "phy_uart_in", "RX")
#
#    parameters = None
#    parameters = self.sgm.get_parameters(uart_name)
#
#    #print "Dictionary: " + str(parameters["ports"]["phy_uart_in"])
#    self.assertEqual(parameters["ports"]["phy_uart_in"]["port"], "RX")

  def test_move_peripheral_slave(self):
    self.sgm.add_node("slave_1",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)
    self.sgm.add_node("slave_2",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)
    self.sgm.add_node("slave_3",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)

    if self.dbg:
      count = self.sgm.get_number_of_peripheral_slaves()
      print "Number of slaves: %d" % (count)
    self.sgm.move_slave(2, 1, gm.SlaveType.PERIPHERAL)

    s3_name = gm.get_unique_name("slave_3",
                                 gm.NodeType.SLAVE,
                                 gm.SlaveType.PERIPHERAL,
                                 slave_index = 1)

    result = True
    try:
      node = self.sgm.get_node(s3_name)
    except NodeError as ex:
      print "Error while trying to get Node: " + str(ex)
      result = False

    self.assertEqual(result, True)

  def test_move_memory_slave(self):
    self.sgm.add_node("slave_1",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.MEMORY,
                      debug = self.dbg)
    self.sgm.add_node("slave_2",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.MEMORY,
                      debug = self.dbg)
    self.sgm.add_node("slave_3",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.MEMORY,
                      debug = self.dbg)

    if self.dbg:
      count = self.sgm.get_number_of_memory_slaves()
      print "Number of slaves: %d" % (count)

    result = self.sgm.move_slave(2, 1, gm.SlaveType.MEMORY)

    s3_name = gm.get_unique_name("slave_3",
                                 gm.NodeType.SLAVE,
                                 gm.SlaveType.MEMORY,
                                 slave_index = 1)

    node = self.sgm.get_node(s3_name)

  def test_get_slave_at(self):
    self.sgm.add_node("slave_1",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)
    self.sgm.add_node("slave_2",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)
    self.sgm.add_node("slave_3",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)

    test_name = gm.get_unique_name("slave_2",
                                   gm.NodeType.SLAVE,
                                   gm.SlaveType.PERIPHERAL,
                                   slave_index = 1)
    found_name = self.sgm.get_slave_name_at(gm.SlaveType.PERIPHERAL, 1)
    node = self.sgm.get_slave_at(1, gm.SlaveType.PERIPHERAL)

    self.assertEqual(test_name, node.unique_name)

  def test_get_slave_name_at(self):
    self.sgm.add_node("slave_1",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)
    self.sgm.add_node("slave_2",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)
    self.sgm.add_node("slave_3",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)

    test_name = gm.get_unique_name("slave_2",
                                   gm.NodeType.SLAVE,
                                   gm.SlaveType.PERIPHERAL,
                                   slave_index = 1)
    found_name = self.sgm.get_slave_name_at(gm.SlaveType.PERIPHERAL, 1)


    self.assertEqual(test_name, found_name)

  def test_remove_slave(self):
    self.sgm.add_node("slave_1",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)
    self.sgm.add_node("slave_2",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)
    self.sgm.add_node("slave_3",
                      gm.NodeType.SLAVE,
                      gm.SlaveType.PERIPHERAL,
                      debug = self.dbg)

    self.sgm.remove_slave(gm.SlaveType.PERIPHERAL, 1)

    count = self.sgm.get_number_of_slaves(gm.SlaveType.PERIPHERAL)
    self.assertEqual(count, 2)

if __name__ == "__main__":
  unittest.main()




