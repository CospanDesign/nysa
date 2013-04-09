#! /usr/bin/python

import os
import sys
import wx
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

from nysa.gui.plugins import document_plugin_manager

dbg = False

class DocumentPluginManagerTest (unittest.TestCase):

  def setUp(self):
    pass

  def test_hello(self):
    self.assertEqual(0, 0)

  def test_load_docuemnt_types(self):
    print "Testing load_document_types"
    dpm = document_plugin_manager.DocumentPluginManager(dbg=True)


if __name__ == "__main__":
  unittest.main()

