#! /usr/bin/python

import unittest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from ibuilder.lib import ibuilder

class Test (unittest.TestCase):
  """Unit test for ibuilder"""

  def setUp(self):
    base = os.path.join( os.path.dirname(__file__),
                         os.pardir)
    self.nysa_base = os.path.abspath(base)
    self.out_dir = os.path.join(os.path.expanduser("~"), "sandbox", "temp")
    self.dbg = False

  def test_get_interface_list(self):
    """test the query handler function"""
    result = ibuilder.get_interface_list(bus = "wishbone")
    self.assertEqual(len(result) > 0, False)

  def test_create_project_config_file(self):
    """Test the create JSON string function"""
    result = ibuilder.create_project_config_file(
                filename = "output_project_config_file.json",
                bus="wishbone",
                interface="uart_io_handler.v",
                base_dir=self.out_dir)
    self.assertEqual(1, 1)

  def test_generate_project(self):
    filename = os.path.join(self.nysa_base, "ibuilder", "example_projects", "dionysus_gpio_mem.json")
    result = ibuilder.generate_project(filename)
    self.assertEqual(result, True)



if __name__ == "__main__":
  unittest.main()
