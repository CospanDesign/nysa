#! /usr/bin/python
import unittest
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "site_scons"))

import utils
import map_utils

class Test (unittest.TestCase):
    """Unit test for the verilog pre-processor module"""

    def setUp(self):
        self.dbg = False
        self.env = {}
        self.env["CONFIG_FILE"] = "config.json"
        self.config = utils.read_config(self.env)

    def test_get_map_flags(self):
        config = self.config
        flags = map_utils.get_map_flags(config)
        #print "map flags:"
        #for flag in flags:
        #    if len(flags[flag]["value"]) > 0:
        #        print "\t%s: %s" % (flag, flags[flag]["value"])

    def test_create_map_dir(self):
        config = self.config
        map_dir = map_utils.create_map_dir(config)
        #print "map dir: %s" % map_dir
        map_dir = map_utils.get_map_dir(config)
        #print "get map dir: %s" % map_dir

    def test_get_output_map_file(self):
        config = self.config
        map_fn = map_utils.get_map_filename(config, absolute = True)
        #print "Map Filename: %s" % map_fn

    def test_get_build_flags_string(self):
        config = self.config
        flag_string = map_utils.get_build_flags_string(config)
        #print "flag string: %s" % flag_string

    def test_smartguide_available(self):
        config = self.config
        if map_utils.smartguide_available(config):
            #print "Smartguide available"
            pass
        else:
            #print "Smartguide not available"
            pass

if __name__ == "__main__":
  unittest.main()

