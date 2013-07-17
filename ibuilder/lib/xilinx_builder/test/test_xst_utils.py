#! /usr/bin/python
import unittest
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "site_scons"))

import utils
import xst_utils

class Test (unittest.TestCase):
    """Unit test for the verilog pre-processor module"""

    def setUp(self):
        self.dbg = False
        self.env = {}
        self.env["CONFIG_FILE"] = "config.json"

    def test_get_xst_flags(self):
        """generate a define table given a file"""
        config_fn = os.path.join(utils.get_project_base(), "config.json")
        config = json.load(open(config_fn, "r"))
        flags = xst_utils.get_xst_flags(config)
        #print "Flags"
        #for flag in flags:
        #    print "\t%s: %s" % (flag, flags[flag]["value"])

        self.assertIn("-iob", flags.keys())

    def test_create_xst_project_file(self):
        config = utils.read_config(self.env)
        xst_utils.create_xst_project_file(config)

    def test_create_xst_script(self):
        config = utils.read_config(self.env)
        xst_utils.create_xst_script(config)

    def test_create_lso_file(self):
        config = utils.read_config(self.env)
        xst_utils.create_xst_dir(config)
        xst_utils.create_lso_file(config)



if __name__ == "__main__":
  unittest.main()

