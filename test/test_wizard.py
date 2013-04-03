#! /usr/bin/python

import os
import sys
import wx
import json
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

from nysa.gui.main.wizard_interpreter import WizardInterpreter as wic
from nysa.gui.main.wizard_interpreter import WizardPage as wpc
from nysa.gui.plugins.example1.example_project1 import example_project1


dbg = False


class WizardInterpreterTest (unittest.TestCase):

  parent = None
  project = None
  config_dict = None
  wizard_dict = None

  def setUp(self):
    self.parent = wx.PySimpleApp()  # Start the application
    self.config_dict = {}
    path = "nysa/gui/plugins/example1/example_project1"
    path = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, path)
    path = os.path.abspath(path)
    config_path = os.path.join(path, "config.json")
    try:
      filein = open(config_path)
      self.config_dict = json.load(filein)
    except IOError as err:
      print "Error: %s" % str(err)

    self.wizard_dict = self.config_dict["new_project_wizard"]
    example_project1.PluginExample1.class_config_dict = self.config_dict
    example_project1.PluginExample1.path = path
    self.project = example_project1.PluginExample1(name="Wizard Example", dbg=True)
    self.config_dict = self.project.config_dict

    #setup the pointers (plugin manager should fix this later)
    self.setup_config_dictionary()

  def setup_config_dictionary(self):
    #setup the images to point to the right places
    self.wizard_dict = self.config_dict["new_project_wizard"]
    image_dir = ""
    if "image" in self.wizard_dict.keys():
      print "remap the image directory"
      #print "project file == %s" % os.path.dirname(example_project1.__file__)
      image_dir = os.path.dirname(example_project1.__file__)
      image_dir = os.path.join(image_dir, "images", self.wizard_dict["image"])
      print "image file: %s" % image_dir



  def test_start (self):
    wi = wic(wizard_dict = self.wizard_dict, output = None, project = self.project, dbg=True)


  def test_parser(self):
    pass




if __name__ == "__main__":
  unittest.main()

