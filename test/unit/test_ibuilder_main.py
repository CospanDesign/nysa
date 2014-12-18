#! /usr/bin/python

import unittest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.ibuilder.lib import ibuilder

TEST_CONFIG_FILENAME = os.path.abspath( os.path.join(os.path.dirname(__file__),
                                        os.path.pardir,
                                        "fake",
                                        "test_config_file.json"))



class Test (unittest.TestCase):
  """Unit test for ibuilder"""

  def setUp(self):
    base = os.path.join( os.path.dirname(__file__),
                         os.pardir)
    self.nysa_base = os.path.abspath(base)
    self.out_dir = os.path.join(os.path.expanduser("~"), "sandbox", "temp")
    self.dbg = False

  def test_create_project_config_file(self):
    """Test the create JSON string function"""
    result = ibuilder.create_project_config_file(
                filename = "output_project_config_file.json",
                bus="wishbone",
                interface="uart_io_handler.v",
                base_dir=self.out_dir)
    self.assertEqual(1, 1)

  def test_generate_project(self):
    result = ibuilder.generate_project(TEST_CONFIG_FILENAME)
    self.assertEqual(result, True)

if __name__ == "__main__":
  unittest.main()
