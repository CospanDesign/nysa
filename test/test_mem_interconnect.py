#! /usr/bin/python
import unittest
import os
import sys
import json
from inspect import isclass

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__),
                "..",
                "cbuilder",
                "scripts"))
import wishbone_mem_interconnect_cbuilder as wic

class Test (unittest.TestCase):
  """Unit test for sapfile"""

  def setUp(self):
    """open up a sapfile class"""
    base = os.path.join( os.path.dirname(__file__),
                              "..")
    self.nysa_base = os.path.abspath(base)
    self.dbg = False

  def test_gen_interconnect (self):
    """Generate an actual interconnect file"""
    tag_file = os.path.join(  self.nysa_base,
                              "ibuilder",
                              "example_projects",
                              "dionysus_gpio_mem.json")
    filein = open(tag_file)
    tags = json.load(filein)
    filein.close()

    print "Tags: %s" % str(tags)

    buf = wic.generate_wb_mem_interconnect(tags = tags, debug = True)


    print "Wishbone interconnect: \n\n"
    print buf
    out_file = os.path.join(os.path.expanduser("~"), "sandbox", "mem_interconnect.v")
    f = open(out_file, "w")
    f.write(buf)
    f.close()

    self.assertEqual(len(buf) > 0, True)




if __name__ == "__main__":
  unittest.main()
