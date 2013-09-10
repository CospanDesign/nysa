#! /usr/bin/python

import unittest
import os
import sys
from inspect import isclass
import json

sys.path.append(os.path.join(os.path.dirname(__file__),
                os.pardir,
                "nysa"))


from ibuilder.lib import wishbone_utils

class Test (unittest.TestCase):
    """Unit test for wishbone_utils"""

    def setUp(self):
        self.dbg = False

    def test_wishbone_top_generator(self):
        wtg = wishbone_utils.WishboneTopGenerator()
        self.assertTrue(True)

