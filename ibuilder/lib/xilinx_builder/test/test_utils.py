#! /usr/bin/python
import unittest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "site_scons"))

import utils

class Test (unittest.TestCase):
    """Unit test for the verilog pre-processor module"""

    def setUp(self):
        self.dbg = False
        self.env = {}
        self.env["CONFIG_FILE"] = "config.json"
        self.env["ENV"] = {}


    def test_get_xilinx_tool_types(self):
        """generate a define table given a file"""
        #print "Xilinx tool: %s" % str(utils.get_xilinx_tool_types())
        self.assertGreater(len(utils.get_xilinx_tool_types()), 0)

    def test_read_config(self):
        cfg = utils.read_config(self.env)
        self.assertIn("device", cfg.keys())

    def test_find_xilinx_path(self):
        path = utils.find_xilinx_path()
        if path is None:
            print "Note: A Xilinx toolchain is required for this test"
        #print "Path: %s" % path
        self.assertIsNotNone(path)

        #Testing Vivado path
        path = utils.find_xilinx_path(build_tool="Vivado")
        #print "Path: %s" % path
        self.assertIsNotNone(path)

    def test_find_license_dir(self):
        path = utils.find_license_dir()
        #print "License File Location: %s" % path

    def test_create_build_directory(self):
        cfg = utils.read_config(self.env)
        build_dir = "temp"
        cfg["build_dir"] = build_dir
        utils.create_build_directory(cfg)
        build_dir = os.path.join(utils.get_project_base(), build_dir)
        self.assertTrue(os.path.exists(build_dir))
        os.rmdir(build_dir)

    def test_get_device(self):
        config = utils.read_config(self.env)
        config["device"] = "xc6slx9-tqg144-3"
        device = utils.get_device(config)
        self.assertEqual("xc6slx9", device)

    def test_get_family(self):
        config = utils.read_config(self.env)
        config["device"] = "xc6slx9-tqg144-3"
        family = utils.get_family(config)
        self.assertEqual("spartan6", family)

    def test_get_speed_grade(self):
        config = utils.read_config(self.env)
        config["device"] = "xc6slx9-tqg144-3"
        speed = utils.get_speed_grade(config)
        self.assertEqual("-3", speed)

    def test_get_package(self):
        config = utils.read_config(self.env)
        config["device"] = "xc6slx9-tqg144-3"
        package = utils.get_package(config)
        self.assertEqual("tqg144", package)



if __name__ == "__main__":
  unittest.main()
