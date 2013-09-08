#! /usr/bin/python

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from ibuilder.lib import cocotb_utils

class Test (unittest.TestCase):
  """Unit test for saputils"""

  def setUp(self):
      self.dbg = False
      pass

  def test_find_cocotb(self):
      """
      Locats the Xilinx Base directory
      """
      base = cocotb_utils.find_cocotb_base(debug = self.dbg)
      if self.dbg: "Base: %s" % base
      self.assertIsNotNone(base)

