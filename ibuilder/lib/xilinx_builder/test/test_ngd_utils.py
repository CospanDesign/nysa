#! /usr/bin/python
import unittest
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "site_scons"))

import utils
import ngd_utils

class Test (unittest.TestCase):
    """Unit test for the verilog pre-processor module"""

    def setUp(self):
        self.dbg = False
        self.env = {}
        self.env["CONFIG_FILE"] = "config.json"
        self.config = utils.read_config(self.env)

    def test_get_ngd_flags(self):
        config = self.config
        flags = ngd_utils.get_ngd_flags(config)
        #print "ngd flags:"
        #for flag in flags:
        #    if len(flags[flag]["value"]) > 0:
        #        print "\t%s: %s" % (flag, flags[flag]["value"])

    def test_create_ngd_dir(self):
        config = self.config
        ngd_dir = ngd_utils.create_ngd_dir(config)
        #print "ngd dir: %s" % ngd_dir
        ngd_dir = ngd_utils.get_ngd_dir(config)
        #print "get ngd dir: %s" % ngd_dir

    def test_get_build_flags_string(self):
        config = self.config
        flag_string = ngd_utils.get_build_flags_string(config)
        #print "flag string: %s" % flag_string

    def test_create_ucf_filename(self):
        config = self.config
        ucf_filename = ngd_utils.create_ucf_filename(config)
        #print "ucf_filename: %s" % ucf_filename

if __name__ == "__main__":
  unittest.main()

