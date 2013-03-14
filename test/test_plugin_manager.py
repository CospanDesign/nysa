#! /usr/bin/python

import os
import sys
import wx
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

from nysa.gui import nysa
from nysa.gui.plugins import plugin_manager as pm


class PluginManagerTest (unittest.TestCase):

  def setUp(self):
    pass

  def test_hello (self):
    self.assertEqual(0, 0)

  def test_get_plugin_dict(self):
    print "Getting plugin dictionary"
    p = pm.PluginManager()
    plugin_dict = p.get_plugin_dict()

  def test_get_plugin_class(self):
    p = pm.PluginManager()
    clazz = p.get_plugin_class("cbuilder")
    print "Got class: %s" % str(clazz)
    """
    p = pm.PluginManager()
    plugin_dict = p.get_plugin_dict()
    for key in plugin_dict.keys():
      print "key: %s" % key
      c = plugin_dict[key][1]()
      c = p.get_plugin(plugin_dict[key][1]) 
      print "Got Class: %s" % str(c)
    """

  def test_read_config_file(self):
    print "read the config file"
    p = pm.PluginManager()
    cb = p.get_plugin_class("cbuilder")()
    cb.read_config_file()
 #  p = pm.PluginManager()




if __name__ == "__main__":
  unittest.main()

