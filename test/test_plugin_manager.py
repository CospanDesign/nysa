#! /usr/bin/python

import os
import sys
import wx
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

from nysa.gui.plugins import plugin_manager as pm

dbg = False

class PluginManagerTest (unittest.TestCase):

  def setUp(self):
    pass

  def test_hello (self):
    self.assertEqual(0, 0)

  def test_get_plugin_class(self):
    p = pm.PluginManager()
    clazz = p.get_plugin_class("cbuilder")
    if dbg: print "Got class: %s" % str(clazz)

    clazz = p.get_plugin_class("example1")
    if dbg: print "Got class: %s" % str(clazz)

  def test_read_config_file(self):
    if dbg: print "read the config file"
    p = pm.PluginManager()
    cb = p.get_plugin_class("cbuilder")()
    cb.read_config_file()

    ep = p.get_plugin_class("example1")()
    if dbg: print "Got class: %s" % str(ep)
    ep.read_config_file()

  def test_map_config_functions(self):
    p = pm.PluginManager(dbg=False)

  def test_get_persistent_gui_menu_items(self):
    p = pm.PluginManager(dbg=False)
    p.get_persistent_gui_menu_items()

  def test_get_persistent_gui_toolbar_items(self):
    p = pm.PluginManager(dbg=False)
    p.get_persistent_gui_toolbar_items()


if __name__ == "__main__":
  unittest.main()

