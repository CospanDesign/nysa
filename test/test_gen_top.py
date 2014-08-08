#! /usr/bin/python

import unittest
import os
import sys
from inspect import isclass
import json

sys.path.append(os.path.join(os.path.dirname(__file__),
                os.pardir),
                "nysa")

from ibuilder.lib import utils
from ibuilder.lib.gen_scripts.gen import Gen
from ibuilder.lib.gen_scripts import gen_top


import utils
class Test (unittest.TestCase):
  """Unit test for the gen_top.py"""

  def setUp(self):
    base = os.path.join( os.path.dirname(__file__),
                         os.pardir,
                         "nysa")
    self.nysa_base = os.path.abspath(base)
    self.dbg = False
    self.gen = gen_top.GenTop()


  def test_gen_top_mem(self):
    """generate a top.v file with memory bus"""
    tags = {}
    top_buffer = ""
    #get the example project data
    filename = os.path.join(  self.nysa_base,
                              "ibuilder",
                              "example_projects",
                              "dionysus_internal_lax_example.json")
    filein = open(filename)
    filestr = filein.read()
    tags = json.loads(filestr)


    filename = os.path.join(  self.nysa_base,
                              "cbuilder",
                              "template",
                              "top",
                              "top.v")

    filein = open(filename)
    top_buffer = filein.read()
    filein.close()

    #print "buf: " + top_buffer

    result = self.gen.gen_script(tags, buf = top_buffer, debug=self.dbg)
    #if (self.dbg):
    print "Top file: \n" + result

    outfile = os.path.join( os.path.expanduser("~"), "sandbox", "top.v")
    f = open(outfile, "w")
    f.write(result)
    f.close()

    self.assertEqual(len(result) > 0, True)


  def test_is_not_wishbone_port(self):
    result = False
    result = self.gen.is_wishbone_port("gpio")
    self.assertEqual(result, False)

  def test_is_wishbone_port(self):
    result = False
    result = self.gen.is_wishbone_port("i_wbs_stb")
    self.assertEqual(result, True)

  def test_invert_reset(self):
    result = False
    #generate a top file
    tags = {}
    top_buffer = ""
    filename = os.path.join(  self.nysa_base,
                              "ibuilder",
                              "example_projects",
                              "dionysus_gpio_mem.json")

    filein = open(filename)
    filestr = filein.read()
    tags = json.loads(filestr)

    filename = os.path.join(  self.nysa_base,
                              "cbuilder",
                              "template",
                              "top",
                              "top.v")

    filein = open(filename)
    top_buffer = filein.read()
    filein.close()

    result = self.gen.gen_script(tags, buf = top_buffer, debug= self.dbg)
    if (self.dbg):
      print "Top File: \n" + result

    self.assertEqual(len(result) > 0, True)

  def test_gen_top(self):
    """generate a top.v file"""

    tags = {}
    top_buffer = ""
    filename = os.path.join(  self.nysa_base,
                              "ibuilder",
                              "example_projects",
                              "dionysus_gpio_mem.json")

    filein = open(filename)
    filestr = filein.read()
    tags = json.loads(filestr)

    filename = os.path.join(  self.nysa_base,
                              "cbuilder",
                              "template",
                              "top",
                              "top.v")

    filein = open(filename)
    top_buffer = filein.read()
    filein.close()

    result = self.gen.gen_script(tags, buf = top_buffer, debug=False)
    #if (self.dbg):
    print "Top file: \n" + result

    self.assertEqual(len(result) > 0, True)


  def test_generate_top_with_internal_bindings(self):

    tags = {}
    top_buffer = ""
    filename = os.path.join(  self.nysa_base,
                              "ibuilder",
                              "example_projects",
                              "dionysus_internal_lax_example.json")

    filein = open(filename)
    filestr = filein.read()
    tags = json.loads(filestr)

    filename = os.path.join(  self.nysa_base,
                              "cbuilder",
                              "template",
                              "top",
                              "top.v")

    filein = open(filename)
    top_buffer = filein.read()
    filein.close()


    result = self.gen.gen_script(tags, buf = top_buffer, debug=self.dbg)
    if (self.dbg):
      print "Top file: \n" + result

    self.assertEqual(len(result) > 0, True)


  def test_generate_buffer_slave_with_inout(self):
#   print "generate slave with inout port"
    absfilepath = utils.find_rtl_file_location("wb_sdram.v")
    slave_keywords = [
      "DRT_ID",
      "DRT_FLAGS",
      "DRT_SIZE"
    ]
    mtags = utils.get_module_tags(  filename = absfilepath,
                                    bus="wishbone",
                                    keywords = slave_keywords)
    self.gen.wires = [
      "clk",
      "rst"
    ]
    tags = {}
    filename = os.path.join(  self.nysa_base,
                              "ibuilder",
                              "example_projects",
                              "dionysus_gpio_mem.json")

    filein = open(filename)
    filestr = filein.read()
    tags = json.loads(filestr)

    self.gen.tags = tags
    self.gen.bindings = self.gen.tags["bind"]

    result = self.gen.generate_buffer(  name="mem1",
                                        index=2,
                                        module_tags = mtags,
                                        debug=self.dbg)

    buf = result
    self.assertEqual(len(buf) > 0, True)


  def test_generate_buffer_slave(self):

    absfilepath = utils.find_rtl_file_location("wb_gpio.v")
    slave_keywords = [
      "DRT_ID",
      "DRT_FLAGS",
      "DRT_SIZE"
    ]
    mtags = utils.get_module_tags(  filename = absfilepath,
                                    bus="wishbone",
                                    keywords = slave_keywords)
    self.gen.wires = [
      "clk",
      "rst"
    ]
    tags = {}

    filename = os.path.join(  self.nysa_base,
                              "ibuilder",
                              "example_projects",
                              "mem_example.json")


    filein = open(filename)
    filestr = filein.read()
    tags = json.loads(filestr)

    self.gen.tags = tags
    result = self.gen.generate_buffer(name="wbs", index=0, module_tags = mtags)

    buf = result
    #print "out:\n" + buf
    self.assertEqual(len(buf) > 0, True)



  def test_generate_buffer_io_handler(self):

    absfilepath = utils.find_rtl_file_location("uart_io_handler.v")
    #print "uart_io_handler.v location: " + absfilepath
    tags = {}
    filename = os.path.join(  self.nysa_base,
                              "ibuilder",
                              "example_projects",
                              "mem_example.json")


    filein = open(filename)
    filestr = filein.read()
    tags = json.loads(filestr)

    filename = os.path.join(  self.nysa_base,
                              "cbuilder",
                              "template",
                              "top",
                              "top.v")

    filein = open(filename)
    top_buffer = filein.read()
    filein.close()

    self.gen.tags = tags


    tags = utils.get_module_tags(filename = absfilepath, bus="wishbone")
    self.gen.wires=[
      "clk",
      "rst"
    ]

    result = self.gen.generate_buffer(name = "uio", module_tags = tags, io_module = True)

    buf = result
    #print "out:\n" + buf
    self.assertEqual(len(buf) > 0, True)


  def test_generate_buffer_ftdi_io_handler(self):

    absfilepath = utils.find_rtl_file_location("ft_master_interface.v")
    slave_keywords = [
      "DRT_ID",
      "DRT_FLAGS",
      "DRT_SIZE"
    ]
    mtags = utils.get_module_tags(filename = absfilepath, bus="wishbone", keywords = slave_keywords)
    self.gen.wires = [
      "clk",
      "rst"
    ]
    tags = {}

    filename = os.path.join(  self.nysa_base,
                              "ibuilder",
                              "example_projects",
                              "dionysus_gpio_mem.json")

    filein = open(filename)
    filestr = filein.read()
    tags = json.loads(filestr)


    self.gen.tags = tags
    self.gen.bindings = self.gen.tags["bind"]

    result = self.gen.generate_buffer(name = "uio", module_tags = mtags, io_module = True, debug=self.dbg)
    buf = result
#   print "out:\n" + buf
    self.assertEqual(len(buf) > 0, True)


  def test_generate_arbitor_buffer_not_needed(self):
    """test if the generate arbitor buffer will successfully generate a buffer"""
    arb_buf = ""
    tags = {}
    filename = os.path.join(  self.nysa_base,
                              "ibuilder",
                              "example_projects",
                              "mem_example.json")
    filein = open(filename)
    filestr = filein.read()
    tags = json.loads(filestr)


    self.gen.tags = tags
    arb_buf = self.gen.generate_arbitor_buffer(debug = self.dbg)
    self.assertEqual(len(arb_buf), 0)

  def test_generate_arbitor_buffer_simple(self):
    """test if the generate arbitor buffer will successfully generate a buffer"""
    arb_buf = ""
    tags = {}
    filename = os.path.join(  self.nysa_base,
                              "ibuilder",
                              "example_projects",
                              "arb_example.json")

    filein = open(filename)
    filestr = filein.read()
    tags = json.loads(filestr)

    self.gen.tags = tags
    arb_buf = self.gen.generate_arbitor_buffer(debug = self.dbg)
    if self.dbg:
      print "arbitor buffer: \n" + arb_buf
    self.assertEqual(len(arb_buf) > 0, True)

  def test_generate_with_paramters(self):
    """test the capability to set paramters within the top.v file"""
    buf = ""
    tags = {}

    #load the configuration tags from the json file
    filename = os.path.join(  self.nysa_base,
                              "ibuilder",
                              "example_projects",
                              "lx9_parameter_example.json")
    filein = open(filename)
    filestr = filein.read()
    tags = json.loads(filestr)

    #project tags
    self.gen.tags = tags

    #module tags
    slave_keywords = [
      "DRT_ID",
      "DRT_FLAGS",
      "DRT_SIZE"
    ]

    #get the name of the first slave from the configuration file
    slave_name = tags["SLAVES"].keys()[0]


    #get the module tags from the slave
    absfilepath = utils.find_rtl_file_location(tags["SLAVES"][slave_name]["filename"])
    module_tags = utils.get_module_tags(  filename = absfilepath,
                                          bus="wishbone",
                                          keywords = slave_keywords)

    #now we have all the data from the
    buf = self.gen.generate_parameters( slave_name,
                                        module_tags,
                                        debug = self.dbg)

#   print buf

    self.assertEqual(len(buf) > 0, True)

    result = self.gen.generate_buffer(  slave_name,
                                        index = 0,
                                        module_tags = module_tags)

    if (self.dbg):
      print result

    #there are parameters, generate a slave
    self.assertEqual(len(result) > 0, True)

# def test_generate_arbitor_buffer_difficult(self):
#   """test if the generate arbitor buffer will successfully generate a complex arbitor entry buffer"""
#   self.assertEqual(False, False)



if __name__ == "__main__":
  unittest.main()
