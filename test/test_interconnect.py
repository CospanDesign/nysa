#! /usr/bin/python
import unittest
import os
import sys
from inspect import isclass

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__),
                "..",
                "cbuilder",
                "scripts"))
import wishbone_interconnect_cbuilder as wic

class Test (unittest.TestCase):
  """Unit test for sapfile"""

  def setUp(self):
    """open up a sapfile class"""
    self.dbg = False

  def test_gen_interconnect (self):
    """Generate an actual interconnect file"""
    buf = wic.generate_wb_interconnect(num_slaves = 1)

    print "Wishbone interconnect: \n\n"
    print buf

    self.assertEqual(len(buf) > 0, True)



if __name__ == "__main__":
  unittest.main()
