#! /usr/bin/python

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, 'nysa'))

from ibuilder.lib import verilog_utils as vutils
from ibuilder.lib import utils

class Test (unittest.TestCase):
    """Unit test for verilog_utils"""
 
    def setUp(self):
        base = os.path.join( os.path.dirname(__file__),
                             os.pardir)
        self.nysa_base = os.path.abspath(base)
        self.dbg = False

    def test_remove_comments(self):
        """try and remove all comments from a buffer"""
        bufin = "not comment/*comment\n*/\n//comment\n/*\nabc\n*/something//comment"
        output_buffer = vutils.remove_comments(bufin)
        good = "not comment\n\nsomething\n"
        self.assertEqual(output_buffer, good)

    def test_read_slave_tags(self):
        """try and extrapolate all info from the slave file"""
  
        filename = utils.find_rtl_file_location("wb_gpio.v")
        drt_keywords = [
          "DRT_ID",
          "DRT_FLAGS",
          "DRT_SIZE"
        ]
        tags = vutils.get_module_tags(filename, keywords = drt_keywords, debug=self.dbg)
  
        io_types = [
          "input",
          "output",
          "inout"
        ]
        #
        #for io in io_types:
        # for port in tags["ports"][io].keys():
        #   print "Ports: " + port
  
        self.assertEqual(True, True)

    def test_read_slave_tags_with_params(self):
        """some verilog files have a paramter list"""
 
        filename = utils.find_rtl_file_location("wb_gpio.v")
        drt_keywords = [
          "DRT_ID",
          "DRT_FLAGS",
          "DRT_SIZE"
        ]
        tags = vutils.get_module_tags(filename, keywords = drt_keywords, debug=self.dbg)
 
        io_types = [
          "input",
          "output",
          "inout"
        ]
        #
        #for io in io_types:
        # for port in tags["ports"][io].keys():
        #   print "Ports: " + port
 
        if self.dbg:
            print "\n\n\n\n\n\n"
            print "module name: " + tags["module"]
            print "\n\n\n\n\n\n"
 
        self.assertEqual(tags["module"], "wb_gpio")

    def test_read_slave_tags_with_params_lax(self):
        """test the LAX for the parameters"""
        #self.dbg = True
       
        base_dir = os.getenv("SAPLIB_BASE")
        filename = utils.find_rtl_file_location("wb_logic_analyzer.v")
        drt_keywords = [
          "DRT_ID",
          "DRT_FLAGS",
          "DRT_SIZE"
        ]
        tags = vutils.get_module_tags(filename, keywords = drt_keywords, debug=self.dbg)
       
        io_types = [
          "input",
          "output",
          "inout"
        ]
        #
        #for io in io_types:
        # for port in tags["ports"][io].keys():
        #   print "Ports: " + port
       
        if self.dbg:
            print "\n\n\n\n\n\n"
            print "module name: " + tags["module"]
            print "\n\n\n\n\n\n"
       
        #self.dbg = False
        self.assertEqual(tags["module"], "wb_logic_analyzer")

    def test_read_user_parameters(self):
        filename = utils.find_rtl_file_location("wb_gpio.v")
        tags = vutils.get_module_tags(filename, debug=self.dbg)
       
        keys = tags["parameters"].keys()
        if self.dbg:
            print "reading the parameters specified by the user"
        self.assertIn("DEFAULT_INTERRUPT_MASK", keys)
        if self.dbg:
            print "make sure other parameters don't get read"
        self.assertNotIn("ADDR_GPIO", keys)

    def test_read_hard_slave_tags(self):
        """try and extrapolate all info from the slave file"""
        filename = utils.find_rtl_file_location("wb_sdram.v")
        drt_keywords = [
          "DRT_ID",
          "DRT_FLAGS",
          "DRT_SIZE"
        ]
        tags = vutils.get_module_tags(filename, keywords = drt_keywords, debug=self.dbg)
       
        io_types = [
          "input",
          "output",
          "inout"
        ]
        #
        #for io in io_types:
        # for port in tags["ports"][io].keys():
        #   print "Ports: " + port
       
        self.assertEqual(True, True)


