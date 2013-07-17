#! /usr/bin/python
import unittest
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "site_scons"))

import utils
import trace_utils

class Test (unittest.TestCase):
    """Unit test for the verilog pre-processor module"""

    def setUp(self):
        self.dbg = False
        self.env = {}
        self.env["CONFIG_FILE"] = "config.json"
        self.config = utils.read_config(self.env)

    def test_get_trace_flags(self):
        config = self.config
        flags = trace_utils.get_trace_flags(config)
        #print "trace flags:"
        #for flag in flags:
        #    if len(flags[flag]["value"]) > 0:
        #        print "\t%s: %s" % (flag, flags[flag]["value"])

    def test_create_trace_dir(self):
        config = self.config
        trace_dir = trace_utils.create_trace_dir(config)
        #print "trace dir: %s" % map_dir
        trace_dir = trace_utils.get_trace_dir(config)
        #print "get trace dir: %s" % map_dir

    def test_get_output_trace_file(self):
        config = self.config
        trace_fn = trace_utils.get_trace_filename(config, absolute = True)
        #print "Trace Filename: %s" % trace_fn

    def test_get_build_flags_string(self):
        config = self.config
        flag_string = trace_utils.get_build_flags_string(config)
        #print "trace flag string: %s" % flag_string

    def test_get_trace_xml_filename(self):
        config = self.config
        xml_filename = trace_utils.get_trace_xml_filename(config)
        #print "trace xml filename: %s" % xml_filename

if __name__ == "__main__":
  unittest.main()

