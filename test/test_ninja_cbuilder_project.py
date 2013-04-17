#! /usr/bin/python

import os
import sys
import wx
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

dbg = False

class PluginManagerTest (unittest.TestCase):

  def setUp(self):
    pass

  def test_hello (self):
    cbuilder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 
      os.pardir, "cbuilder"))
    print "CBuilder Path: %s" % cbuilder_path
    cbuilder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 
      os.pardir, "gui"))
    self.assertEqual(0, 0)

  def test_generate_cbuilder_project(self):
    #Create a valid dictionary
    cpd = {}



if __name__ == '__main__':
  unittest.main()
