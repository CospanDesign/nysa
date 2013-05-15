#! /usr/bin/python

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from ibuilder.lib import xilinx_utils

class Test (unittest.TestCase):
  """Unit test for saputils"""

  def setUp(self):
    self.dbg = False
    pass

  def test_get_version_list(self):
    """
    returns a list of the version on this computer
    """
    #get a list of the version on this computer
    versions = xilinx_utils.get_version_list(base_directory = None, 
                        debug = self.dbg)
    print "List: %s" % str(versions)
    self.assertIsNotNone(versions)  

  def test_get_supported_version(self):
    """
    gets the correct version of the Xilnx toolchain to use
    """

    #give two different versions of the toolchain
    versions = [14.1, 13.4]
    v = xilinx_utils.get_supported_version( "xc6slx9csg324-2", 
                        versions, 
                        debug = self.dbg)

    if self.dbg:
      print "Version for Spartan/Virtex 6: %f" % v
    self.assertEqual(v, 14.1)
    v = xilinx_utils.get_supported_version( "xc3s500efg320", 
                        versions, 
                        debug = self.dbg)
    if self.dbg:
      print "Version for Spartan 3: %f" % v
    self.assertEqual(v, 13.4)

if __name__ == "__main__":
  sys.path.append (sys.path[0] + "/../")
  unittest.main()
