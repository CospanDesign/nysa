#! /usr/bin/python

import unittest
import os
import sys
from inspect import isclass
import json

sys.path.append(os.path.join(os.path.dirname(__file__),
                os.pardir,
                "nysa"))

from ibuilder.lib import utils
from ibuilder.lib.gen_scripts.gen import Gen
from ibuilder.lib.gen_scripts import gen_sim_top


import utils
class Test (unittest.TestCase):
    """Unit test for the gen_sim_top.py"""

    def setUp(self):
        base = os.path.join( os.path.dirname(__file__),
                           os.pardir,
                           "nysa")
        self.nysa_base = os.path.abspath(base)
        self.dbg = False
        self.gen = gen_sim_top.GenSimTop()


    def test_gen_sim_top(self):
        tags = {}
        top_buffer = ""
        filename = os.path.join(  self.nysa_base,
                                  "ibuilder",
                                  "example_projects",
                                  "dionysus_gpio_mem.json")

        filein = open(filename)
        filestr = filein.read()
        tags = json.loads(filestr)

        result = self.gen.gen_script(tags, buf = "", debug=False)
        if self.dbg:
          print "Top file: \n" + result
        self.assertEqual(len(result) > 0, True)




if __name__ == "__main__":
  unittest.main()
