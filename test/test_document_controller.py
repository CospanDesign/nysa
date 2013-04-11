#! /usr/bin/python

import os
import sys
import wx
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

from nysa.gui.main import document_controller
from nysa.gui.plugins import document_plugin_manager

dbg = False

class DocumentControllerTest (unittest.TestCase):

  def setUp(self):
    pass


  def test_document_manager(self):
    dc = document_controller.DocumentController(dbg=False)

  def test_get_document_types(self):
    dc = document_controller.DocumentController(dbg=False)
    types = dc.get_types()
    print "Types: %s" % str(types)

  def test_new_document(self):
    dc = document_controller.DocumentController(dbg=True)
    types = dc.get_types()
    doc = dc.new_document(document_type = types[0], name = "Test")


if __name__ == "__main__":
  unittest.main()

