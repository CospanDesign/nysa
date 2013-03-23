#! /usr/bin/python

import os
import sys
import wx
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

from nysa.gui import nysa_gui
from nysa.gui.plugins import plugin_manager as pm
from nysa.gui.main import workspace_manager as wm

dbg = True

class WorkspaceManagerTest (unittest.TestCase):

  def setUp(self):
    pass

  def test_get_workspace_manager(self):
    if dbg: print "Getting workspace manager"
    w = wm.WorkspaceManager(dbg=True)
    self.assertEqual(0, 0)


if __name__ == "__main__":
  unittest.main()

