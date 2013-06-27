#! /usr/bin/python

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from ibuilder.lib import wishbone_utils

class Test (unittest.TestCase):
    """Unit test for wishbone_utils"""
    def setUp(self):
        base = os.path.join( os.path.dirname(__file__),
                         os.pardir)
        self.nysa_base = os.path.abspath(base)
        self.dbg = False

    def test_is_wishbone_bus_signal(self):
        retval = wishbone_utils.is_wishbone_bus_signal("blah")
        self.assertFalse(retval)
        #Test a normal Slave signal
        retval = wishbone_utils.is_wishbone_bus_signal("i_wbs_we")
        self.assertTrue(retval)
        #Test an arbitor master signal
        retval = wishbone_utils.is_wishbone_bus_signal("o_fb_stb")
        self.assertTrue(retval)



if __name__ == "__main__":
  unittest.main()

