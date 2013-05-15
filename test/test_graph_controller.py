#! /usr/bin/python
import unittest
import os
import sys
import json
import mock

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from ibuilder.gui import controller
from ibuilder.gui import graph_manager

class GraphControllerTest (unittest.TestCase):


  # Data found in saplib/example_project/gpio_example.json
  EXAMPLE_CONFIG = {
    "BASE_DIR": "~/projects/sycamore_projects",
    "board": "xilinx-s3esk",
    "PROJECT_NAME": "example_project",
    "TEMPLATE": "wishbone_template.json",
    "INTERFACE": {
      "filename": "uart_io_handler.v",
      "bind": {
        "phy_uart_in": {
          "port": "RX",
          "direction": "input"
        },
        "phy_uart_out": {
          "port": "TX",
          "direction": "output"
        }
      }
    },
    "SLAVES": {
      "gpio1": {
        "filename":"wb_gpio.v",
        "bind": {
          "gpio_out[7:0]": {
            "port":"led[7:0]",
            "direction":"output"
          },
          "gpio_in[3:0]": {
            "port":"switch[3:0]",
            "direction":"input"
          }
        }
      }
    },
    "bind": {},
    "constraint_files": []
  }

  # Data found in saplib/hdl/boards/xilinx-s3esk/config.json
  BOARD_CONFIG = {
    "board_name": "Spartan 3 Starter Board",
    "vendor": "Digilent",
    "fpga_part_number": "xc3s500efg320",
    "build_tool": "xilinx",
    "default_constraint_files": [
      "s3esk_sycamore.ucf"
    ],
    "invert_reset": False
  }



  def setUp(self):
    """Creates a Controller for each test"""
    print "Graph Controller Test"
    self.c = controller.Controller()

  def test_load_config_file(self):
    """Loads the config file and compares it to EXAMPLE_CONFIG"""
    self.c.get_board_config = (lambda x: self.BOARD_CONFIG)
    self.c.get_project_constraint_files = (
      lambda: self.BOARD_CONFIG['default_constraint_files'])

    # Load the example file from the example dir
    fname = os.path.join(os.path.dirname(__file__), os.pardir, "ibuilder",
      "example_projects", "gpio_example.json")
    self.assertTrue(self.c.load_config_file(fname),
      'Could not get file %s. Please ensure that is exists\n' +
      '(re-checkout from the git repos if necessary)')

    #Check that the state of the controller is as it should be.
    self.assertEqual(self.c.project_tags, self.EXAMPLE_CONFIG)
    self.assertEqual(self.c.filename, fname)
    self.assertEqual(self.c.build_tool, {})
    self.assertEqual(self.c.board_dict, self.BOARD_DICT)



if __name__ == "__main__":
  unittest.main()

