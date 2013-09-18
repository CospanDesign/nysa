#! /usr/bin/python

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, 'nysa'))

from ibuilder.lib import module_builder as mb
from ibuilder.lib import utils
from ibuilder.lib.ibuilder_error import IBuilderError


test_module_tags = {
    "module":"test_module",
    "defines":{
        "USER_DEFINE":"1",
        "DEFINE_THING":"(USER_DEFINE * 4)"
    },
    "parameters":{
        "PARAMETER1":"1",
        "PARAMETER2":"4"
    },
    "submodules":{
        "module1":{
            "filename":"wb_gpio.v",
            "parameters":{
                "DEFAULT_INTERRUPT_MASK":"1",
                "DEFAULT_INTERRUPT_EDGE":"2"
            },
            "bind":{
                "gpio_out[1:0]":{
                    "loc":"led[1:0]",
                    "direction":"output"
                },
                "gpio_in[3:2]":{
                    "loc":"button[1:0]",
                    "direction":"input"
                }
            }
        }
    },
    "ports":{
        "input":{
            "clk":{
                "size":1
            },
            "rst":{
                "size":1
            },
            "stimulus":{
                "size":1
            },
            "array":{
                "size":31,
                "max_val":31,
                "min_val":0
            },
            "button":{
                "size":4,
                "max_val":3,
                "min_val":0
            }
        },
        "output":{
            "out1":{
                "size":1
            },
            "led":{
                "size":4,
                "max_val":3,
                "min_val":0
            }
        },
        "inout":{
            "inout_test":{
                "size":1
            },
            "inout":{
                "size":5,
                "max_val":5,
                "min_val":1
            }
        }
    }
}

class Test (unittest.TestCase):
    """Unit test for verilog_utils"""

    def setUp(self):
        base = os.path.join( os.path.dirname(__file__),
                             os.pardir)
        self.nysa_base = os.path.abspath(base)
        self.dbg = False

    def test_module_port_generator(self):
        module_name = test_module_tags["module"]
        port_dict = test_module_tags["ports"]
        param_dict = {}
        prev_dbg = self.dbg
        #self.dbg = True
        buf = mb.generate_module_ports(module_name,
                                       port_dict,
                                       param_dict,
                                       debug = self.dbg)
        if self.dbg:
            print "Module Port Buffer\n%s" % buf
        self.dbg = prev_dbg

    def test_module_port_and_parameters_generator(self):
        module_name = test_module_tags["module"]
        port_dict = test_module_tags["ports"]
        param_dict = test_module_tags["parameters"]
        prev_dbg = self.dbg
        #self.dbg = True
        buf = mb.generate_module_ports(module_name,
                                       port_dict,
                                       param_dict,
                                       debug = self.dbg)
        if self.dbg:
            print "Module Port Buffer\n%s" % buf
        self.dbg = prev_dbg

    def test_timestep_buffer(self):
        prev_dbg = self.dbg
        #self.dbg = True
        buf = mb.generate_timespec_buf()
        if self.dbg:
            print "Module Timespec buffer\n%s" % buf
        self.dbg = prev_dbg

    def test_generate_define_buffer(self):
        defines_dict = test_module_tags["defines"]
        prev_dbg = self.dbg
        #self.dbg = True
        buf = mb.generate_defines_buf(defines_dict)
        if self.dbg:
            print "Defines buffer\n%s" % buf
        self.dbg = prev_dbg
 
    def test_generate_sub_module(self):
        prev_dbg = self.dbg
        #self.dbg = True
        MB = mb.ModuleBuilder(test_module_tags)
        buf = MB.generate_sub_module(False,
                                     instance_name = "module1",
                                     config_tags = test_module_tags["submodules"]["module1"],
                                     debug = self.dbg)
        if self.dbg:
            print "Submodule buffer\n%s" % buf
        self.dbg = prev_dbg

    def test_generate_module(self):
        prev_dbg = self.dbg
        self.dbg = True
        MB = mb.ModuleBuilder(test_module_tags)
        buf = MB.generate_module("test_module",
                                 test_module_tags,
                                 True,
                                 debug = self.dbg)
        if self.dbg:
            print "Module buffer\n%s" % buf
        self.dbg = prev_dbg



