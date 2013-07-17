#! /usr/bin/python

import unittest
import os
import sys
from inspect import isclass
import json

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from ibuilder.lib import utils
from ibuilder.lib.gen_scripts.gen import Gen
from ibuilder.lib.gen_scripts import gen_project_config

import utils


class Test (unittest.TestCase):
    """Unit test for the gen_top.v"""

    def setUp(self):
        base = os.path.join( os.path.dirname(__file__),
                             os.pardir)
        self.nysa_base = os.path.abspath(base)
        self.dbg = False


    def test_gen_project(self):
        self.gen = gen_project_config.GenProjectConfig()

        tags = {}

        fn = os.path.join(self.nysa_base,
                          "ibuilder",
                          "example_projects",
                          "dionysus_default.json")

        fp = open(fn, "r")
        tags = json.load(fp)
        fp.close()
        
        fn = os.path.join(self.nysa_base,
                          "ibuilder",
                          "xilinx_builder",
                          "config.json")
        fp = open(fn, "r")
        buf = fp.read()
        fp.close()

        result = self.gen.gen_script(tags, buf = buf, debug=self.dbg)

        config = json.loads(result)
        #print "config: %s" % json.dumps(config, sort_keys = True, indent = 4, separators = [',', ':'])

