#! /usr/bin/python

import os
import sys
import wx
import json
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

from nysa.gui.main.wizard_interpreter import WizardInterpreter as wic
from nysa.gui.main.wizard_interpreter import WizardPage as wpc
from nysa.gui.plugins.plugin_manager  import PluginManager
from nysa.gui.plugins.example1.example_project1 import example_project1


dbg = False


class WizardInterpreterTest (unittest.TestCase):

  parent = None
  project = None
  wizard_dict = None
  pm          = None

  def setUp(self):
    self.pm = PluginManager()
    self.pm.load_plugin_projects("example1")
    clazz = self.pm.get_project_class("example1", "example_project1")
    self.project = clazz(output = None, name = "Wizard Example", dbg = True)
    self.wizard_dict = self.project.get_new_project_wizard()

    self.parent = wx.PySimpleApp()  # Start the application


  def test_start (self):
    #print "Wizard Dict: %s" % str(self.wizard_dict)
    wi = wic(wizard_dict = self.wizard_dict, output = None, project = self.project, dbg=True)
    wi.run()
    wi.Destroy()
    self.parent.MainLoop()






if __name__ == "__main__":
  unittest.main()

