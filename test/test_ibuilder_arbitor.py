#!/usr/bin/python

import unittest
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from ibuilder.lib import utils
from ibuilder.lib import arbitor

class Test (unittest.TestCase):
  """Unit test for arbitor"""

  def setUp(self):
    base = os.path.join( os.path.dirname(__file__),
                         os.pardir)
    self.nysa_base = os.path.abspath(base)
    self.dbg = False

  def test_get_number_of_arbitor_hosts(self):
    #the first test should fail
    file_name = "wb_gpio.v"
    file_name = utils.find_rtl_file_location(file_name)
    m_tags = utils.get_module_tags(file_name, "wishbone")
    result = arbitor.get_number_of_arbitor_hosts(m_tags, debug = self.dbg)

    self.assertEqual(len(result), 0)

    #the second test should pass
    file_name = "wb_console.v"
    file_name = utils.find_rtl_file_location(file_name)
    m_tags = utils.get_module_tags(file_name, "wishbone")
    result = arbitor.get_number_of_arbitor_hosts(m_tags, debug = self.dbg)

    self.assertEqual(len(result), 2)


  def test_is_arbitor_host(self):
    """
    test if the slave is an arbitor host
    """

    #the first test should fail
    file_name = "wb_gpio.v"
    file_name = utils.find_rtl_file_location(file_name)
    m_tags = utils.get_module_tags(file_name, "wishbone")
    result = arbitor.is_arbitor_host(m_tags, debug = self.dbg)

    self.assertEqual(result, False)

    #the second test should pass
    file_name = "wb_console.v"
    file_name = utils.find_rtl_file_location(file_name)
    m_tags = utils.get_module_tags(file_name, "wishbone")
    result = arbitor.is_arbitor_host(m_tags, debug = self.dbg)

    self.assertEqual(result, True)

  def test_is_arbitor_not_requried(self):
    """test if the project_tags have been modified to show arbitor"""
    result = False
    tags = {}
    #get the example project data
    try:
      filename = os.path.join(  self.nysa_base,
                                "ibuilder",
                                "example_projects",
                                "gpio_example.json")

      filein = open(filename)
      filestr = filein.read()
      tags = json.loads(filestr)

    except IOError as err:
      print "File Error: " + str(err)
      self.assertEqual(False, True)

    result = arbitor.is_arbitor_required(tags, debug = self.dbg)

    self.assertEqual(result, False)

  def test_is_arbitor_requried(self):
    """test if the project_tags have been modified to show arbitor"""
    result = False
    tags = {}
    #get the example project data
    try:
      filename = os.path.join(  self.nysa_base,
                                "ibuilder",
                                "example_projects",
                                "arb_example.json")
      filein = open(filename)
      filestr = filein.read()
      tags = json.loads(filestr)

    except IOError as err:
      print "File Error: " + str(err)
      self.assertEqual(False, True)

    result = arbitor.is_arbitor_required(tags, debug = self.dbg)


    self.assertEqual(result, True)

  def test_generate_arbitor_tags(self):
    """test if arbitor correctly determins if an arbitor is requried"""
    result = {}
    tags = {}
    #get the example project data
    try:
      filename = os.path.join(  self.nysa_base,
                                "ibuilder",
                                "example_projects",
                                "arb_example.json")

      filein = open(filename)
      filestr = filein.read()
      tags = json.loads(filestr)

    except IOError as err:
      print "File Error: " + str(err)
      self.assertEqual(False, True)

    result = arbitor.generate_arbitor_tags(tags, debug = self.dbg)

    if (self.dbg):
      for aslave in result.keys():
        print "arbitrated slave: " + aslave

        for master in result[aslave]:
          print "\tmaster: " + master + " bus: " + result[aslave][master]


    self.assertEqual((len(result.keys()) > 0), True)


  def test_generate_arbitor_buffer (self):
    """generate an arbitor buffer"""
    result = arbitor.generate_arbitor_buffer(2, debug = self.dbg)
    if (self.dbg):
      print "generated arbitor buffer: \n" + result
    self.assertEqual((len(result) > 0), True)

if __name__ == "__main__":
  unittest.main()
