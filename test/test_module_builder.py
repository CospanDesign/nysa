#! /usr/bin/python

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, 'nysa'))

from ibuilder.lib import module_builder as mb
from ibuilder.lib import utils
from ibuilder.lib.ibuilder_error import IBuilderError

test_ports = {
    "input":{
        "clk",
        "rst",
        "stimulus",
        "array[31:0]"
    },
    "output":{
        "out1",
        "out[3:0]"
    },
    "inout":{
        "inout_test",
        "inout[5:1]"
    }
}

class Test (unittest.TestCase):
    """Unit test for verilog_utils"""

    def setUp(self):
        base = os.path.join( os.path.dirname(__file__),
                             os.pardir)
        self.nysa_base = os.path.abspath(base)
        self.dbg = False

    def test_module_port_generator(self):
        prev_dbg = self.dbg
        self.dbg = True
        buf = mb.generate_module_ports("test", test_ports, debug = self.dbg)
        if self.dbg:
            print "Module Port Buffer\n%s" % buf
        self.dbg = prev_dbg

