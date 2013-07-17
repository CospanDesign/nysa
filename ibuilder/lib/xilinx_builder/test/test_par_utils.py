#! /usr/bin/python
import unittest
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "site_scons"))

import utils
import par_utils

class Test (unittest.TestCase):
    """Unit test for the verilog pre-processor module"""

    def setUp(self):
        self.dbg = False
        self.env = {}
        self.env["CONFIG_FILE"] = "config.json"
        self.config = utils.read_config(self.env)

    def test_get_par_flags(self):
        config = self.config
        flags = par_utils.get_par_flags(config)
        #print "par flags:"
        #for flag in flags:
        #    if len(flags[flag]["value"]) > 0:
        #        print "\t%s: %s" % (flag, flags[flag]["value"])

    def test_create_par_dir(self):
        config = self.config
        par_dir = par_utils.create_par_dir(config)
        #print "par dir: %s" % map_dir
        par_dir = par_utils.get_par_dir(config)
        #print "get par dir: %s" % map_dir

    def test_get_output_par_file(self):
        config = self.config
        par_fn = par_utils.get_par_filename(config, absolute = True)
        #print "Map Filename: %s" % par_fn

    def test_get_build_flags_string(self):
        config = self.config
        flag_string = par_utils.get_build_flags_string(config)
        #print "flag string: %s" % flag_string

    def test_smartguide(self):
        config = self.config
        if par_utils.smartguide_available(config):
            #print "Smartguide Available"
            pass
        else:
            #print "Smartguide Not Available"
            pass


if __name__ == "__main__":
  unittest.main()

