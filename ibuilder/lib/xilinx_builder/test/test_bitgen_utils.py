#! /usr/bin/python
import unittest
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "site_scons"))

import utils
import bitgen_utils

class Test (unittest.TestCase):
    """Unit test for the verilog pre-processor module"""

    def setUp(self):
        self.dbg = False
        self.env = {}
        self.env["CONFIG_FILE"] = "config.json"
        self.config = utils.read_config(self.env)

    def test_get_flags(self):
        config = self.config
        flags = bitgen_utils.get_flags(config)
        #print "bitgen flags:"
        #for flag in flags:
        #    if flag == "configuration":
        #        continue
        #    if flags[flag] == "_true":
        #        print "\t%s" % flag
        #        continue

        #    if len(flags[flag]["value"]) > 0:
        #        print "\t%s: %s" % (flag, flags[flag]["value"])
        #        pass
                
        #for c in flags["configuration"]:
        #    print "\t%s" % c
        #    pass

    def test_create_bitgen_dir(self):
        config = self.config
        bitgen_dir = bitgen_utils.create_bitgen_dir(config)
        #print "bitgen dir: %s" % map_dir
        bitgen_dir = bitgen_utils.get_bitgen_dir(config)
        #print "get bitgen dir: %s" % map_dir

    def test_get_output_bitgen_file(self):
        config = self.config
        bitgen_fn = bitgen_utils.get_bitgen_filename(config, absolute = True)
        #print "Bitgen Filename: %s" % bitgen_fn

    def test_create_script(self):
        config = self.config
        script_fn = bitgen_utils.create_script(config)
        script = open(script_fn, "r")
        #print "Bitgen Script Contents:"
        #print script.read()
        script.close()


if __name__ == "__main__":
  unittest.main()

