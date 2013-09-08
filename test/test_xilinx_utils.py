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


  def test_locate_xilinx_default(self):
      """
      Locats the Xilinx Base directory
      """
      base = xilinx_utils.find_xilinx_base(debug = self.dbg)
      if self.dbg: "Base: %s" % base
      self.assertIsNotNone(base)


if __name__ == "__main__":
      sys.path.append (sys.path[0] + "/../")
      unittest.main()
