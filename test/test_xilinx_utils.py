#! /usr/bin/python

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from ibuilder.lib import xilinx_utils
from ibuilder.lib.ibuilder_error import XilinxToolchainError

class Test (unittest.TestCase):
  """Unit test for saputils"""

  def setUp(self):
    self.dbg = True
    pass

  def test_get_version_list(self):
    """
    returns a list of the version on this computer
    """
    #get a list of the version on this computer
    versions = xilinx_utils.get_version_list(base_directory = None, 
                        debug = self.dbg)
    if self.dbg: print "List: %s" % str(versions)
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



  def test_locate_xilinx_default(self):
    """
    Locats the Xilinx Base directory
    """
    base = xilinx_utils.locate_xilinx_base(debug = self.dbg)
    if self.dbg: "Base: %s" % base
    self.assertIsNotNone(base)

  def test_locate_xilinx_with_base(self):
    base = None
    if os.name == "nt":
      base = xilinx_utils.locate_xilinx_base("C:\\Xilinx", debug = self.dbg)
    elif os.name == "posix":
      base = xilinx_utils.locate_xilinx_base("/opt", debug = self.dbg)

    self.assertIsNotNone(base)

  def test_locate_xilinx_with_base_fail(self):
    d = None
    if os.name == "nt":
      d = "C:\\temp"
    elif os.name == "posix":
      d = "/var"

    self.assertRaises(XilinxToolchainError, xilinx_utils.locate_xilinx_base, d, debug=self.dbg)

  def test_locate_xilinx_with_base_fail_version(self):
    self.assertRaises(XilinxToolchainError, xilinx_utils.locate_xilinx_base, version=1.0, debug = self.dbg)


  def test_locate_xilinx_sim_files(self):
    """
    Locates the Xilnx simulation files
    """
    base = xilinx_utils.locate_xilinx_sim_files(debug=self.dbg)
    self.assertIsNotNone(base)

if __name__ == "__main__":
  sys.path.append (sys.path[0] + "/../")
  unittest.main()
