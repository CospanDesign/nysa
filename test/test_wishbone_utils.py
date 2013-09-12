#! /usr/bin/python

import unittest
import os
import sys
from inspect import isclass
import json

sys.path.append(os.path.join(os.path.dirname(__file__),
                os.pardir,
                "nysa"))


from ibuilder.lib import wishbone_utils
from ibuilder.lib import utils


class Test (unittest.TestCase):
    """Unit test for wishbone_utils"""

    def setUp(self):
        self.dbg = False
        base = os.path.join(os.path.dirname(__file__),
                            os.pardir,
                            "nysa")
        self.nysa_base = os.path.abspath(base)

    def test_wishbone_top_generator(self):
        wtg = wishbone_utils.WishboneTopGenerator()
        self.assertTrue(True)

    def test_generate_wishbone_interconnect(self):
        buf = wishbone_utils.generate_peripheral_wishbone_interconnect_buffer(3, False)
        prev = self.dbg
        #self.dbg = True
        if self.dbg:
            print "Wishbone interconnect:\n%s" % buf
        self.dbg = prev
        self.assertTrue(True)

    def test_generate_wishbone_mem_interconnect(self):
        buf = wishbone_utils.generate_memory_wishbone_interconnect_buffer(3, False)
        prev = self.dbg
        #self.dbg = True
        if self.dbg:
            print "Wishbone mem interconnect:\n%s" % buf
        self.dbg = prev
        self.assertTrue(True)

    def test_generate_master(self):
        buf = wishbone_utils.generate_master_buffer(False)
        prev = self.dbg
        #self.dbg = True
        if self.dbg:
            print "Master:\n%s" % buf
        self.dbg = prev
        self.assertTrue(True)

    def test_generate_boilerplate_wires(self):
        tags = {}
        top_buffer = ""
        #get the example project data
        filename = os.path.join(  self.nysa_base,
                                  "ibuilder",
                                  "example_projects",
                                  "dionysus_default.json")
        filein = open(filename)
        filestr = filein.read()
        tags = json.loads(filestr)

        wtg = wishbone_utils.WishboneTopGenerator()
        wtg.tags = tags
        buf = wtg.generate_boilerplate_wires(False, 2, 1)
        prev = self.dbg
        #self.dbg = True
        if self.dbg:
            print "Master:\n%s" % buf
        self.dbg = prev
        self.assertTrue(True)

    def test_generate_internal_bindings(self):
        tags = {}
        top_buffer = ""
        #get the example project data
        filename = os.path.join(  self.nysa_base,
                                  "ibuilder",
                                  "example_projects",
                                  "dionysus_default.json")
        filein = open(filename)
        filestr = filein.read()
        tags = json.loads(filestr)

        wtg = wishbone_utils.WishboneTopGenerator()
        wtg.tags = tags
        wtg.internal_bindings = tags["internal_bind"]
        buf = wtg.generate_internal_bindings()
        prev = self.dbg
        #self.dbg = True
        if self.dbg:
            print "Internal Bindings:\n%s" % buf
        self.dbg = prev
        self.assertTrue(True)

    def test_generate_external_bindings(self):
        tags = {}
        top_buffer = ""
        #get the example project data
        filename = os.path.join(  self.nysa_base,
                                  "ibuilder",
                                  "example_projects",
                                  "dionysus_default.json")
        filein = open(filename)
        filestr = filein.read()
        tags = json.loads(filestr)

        wtg = wishbone_utils.WishboneTopGenerator()
        wtg.tags = tags
        wtg.bindings = tags["bind"]
        buf = wtg.generate_external_bindings(True)
        prev = self.dbg
        #self.dbg = True
        if self.dbg:
            print "External Bindings:\n%s" % buf
        self.dbg = prev
        self.assertTrue(True)


    def test_generate_ports(self):
        tags = {}
        top_buffer = ""
        #get the example project data
        filename = os.path.join(  self.nysa_base,
                                  "ibuilder",
                                  "example_projects",
                                  "dionysus_default.json")
        filein = open(filename)
        filestr = filein.read()
        tags = json.loads(filestr)

        wtg = wishbone_utils.WishboneTopGenerator()
        wtg.tags = tags
        wtg.bindings = tags["bind"]
        prev = self.dbg
        #self.dbg = True
        buf = wtg.generate_ports(self.dbg)
        self.dbg = prev
        self.assertTrue(True)


    def test_create_wire_buf(self):
        single_buf = wishbone_utils.create_wire_buf("single_wire", 1, 3, 0)
        range_buf = wishbone_utils.create_wire_buf("single_wire", 2, 63, 32)

        prev = self.dbg
        #self.dbg = True
        if self.dbg:
            print "wire:\n%s%s" % (single_buf, range_buf)
        self.dbg = prev
        self.assertTrue(True)


    def test_get_port_count(self):
        filename = utils.find_rtl_file_location("wb_sdram.v")
        module_tags = utils.get_module_tags(filename)
        port_count = wishbone_utils.get_port_count(module_tags)

        prev = self.dbg
        #self.dbg = True
        if self.dbg:
            print "port count: %d" % port_count
        self.dbg = prev
        self.assertTrue(True)

    def test_generate_ports(self):
        tags = {}
        top_buffer = ""
        #get the example project data
        filename = os.path.join(  self.nysa_base,
                                  "ibuilder",
                                  "example_projects",
                                  "dionysus_default.json")
        filein = open(filename)
        filestr = filein.read()
        tags = json.loads(filestr)

        filename = utils.find_rtl_file_location("wb_sdram.v")
        module_tags = utils.get_module_tags(filename)

        wtg = wishbone_utils.WishboneTopGenerator()
        wtg.tags = tags
        wtg.bindings = tags["bind"]
        prev = self.dbg
        #self.dbg = True
        slave_tags = tags["MEMORY"]["mem1"]

        buf = wtg.generate_module_port_signals("pre_test_",
                                               "name",
                                               slave_tags,
                                               module_tags,
                                               self.dbg)
        if self.dbg:
            print "generate port buf:\n%s" % buf

        self.dbg = prev
        self.assertTrue(True)


    def test_generate_host_interface(self):
        tags = {}
        top_buffer = ""
        #get the example project data
        filename = os.path.join(  self.nysa_base,
                                  "ibuilder",
                                  "example_projects",
                                  "dionysus_default.json")
        filein = open(filename)
        filestr = filein.read()
        tags = json.loads(filestr)

        filename = utils.find_rtl_file_location("wb_sdram.v")
        module_tags = utils.get_module_tags(filename)

        wtg = wishbone_utils.WishboneTopGenerator()
        wtg.tags = tags
        wtg.bindings = tags["bind"]
        prev = self.dbg
        #self.dbg = True

        buf = wtg.generate_host_interface_buffer(self.dbg)
        if self.dbg:
            print "generate host interface buf:\n%s" % buf

        self.dbg = prev
        self.assertTrue(True)

    def test_generate_wishbone_slave(self):
        tags = {}
        top_buffer = ""
        #get the example project data
        filename = os.path.join(  self.nysa_base,
                                  "ibuilder",
                                  "example_projects",
                                  "dionysus_default.json")
        filein = open(filename)
        filestr = filein.read()
        tags = json.loads(filestr)
        slave_tags = tags["SLAVES"]["gpio1"]

        filename = utils.find_rtl_file_location("wb_gpio.v")
        module_tags = utils.get_module_tags(filename)

        wtg = wishbone_utils.WishboneTopGenerator()
        wtg.tags = tags
        wtg.bindings = tags["bind"]
        prev = self.dbg
        #self.dbg = True

        buf = wtg.generate_wishbone_buffer("gpio1",
                                           index = 1,
                                           slave_tags = slave_tags,
                                           module_tags = module_tags,
                                           debug = self.dbg)
        if self.dbg:
            print "generate wishbone buf:\n%s" % buf

        self.dbg = prev
        self.assertTrue(True)

    def test_generate_wishbone_mem_slave(self):
        tags = {}
        top_buffer = ""
        #get the example project data
        filename = os.path.join(  self.nysa_base,
                                  "ibuilder",
                                  "example_projects",
                                  "dionysus_default.json")
        filein = open(filename)
        filestr = filein.read()
        tags = json.loads(filestr)
        slave_tags = tags["MEMORY"]["mem1"]

        filename = utils.find_rtl_file_location("wb_sdram.v")
        module_tags = utils.get_module_tags(filename)

        wtg = wishbone_utils.WishboneTopGenerator()
        wtg.tags = tags
        wtg.bindings = tags["bind"]
        prev = self.dbg
        #self.dbg = True

        buf = wtg.generate_wishbone_buffer("mem1",
                                           index = 1,
                                           slave_tags = slave_tags,
                                           module_tags = module_tags,
                                           mem_slave = True,
                                           debug = self.dbg)
        if self.dbg:
            print "generate wishbone buf:\n%s" % buf

        self.dbg = prev
        self.assertTrue(True)


    def test_get_parameters(self):
        tags = {}
        top_buffer = ""
        #get the example project data
        filename = os.path.join(  self.nysa_base,
                                  "ibuilder",
                                  "example_projects",
                                  "dionysus_parameter_example.json")
        filein = open(filename)
        filestr = filein.read()
        tags = json.loads(filestr)

        filename = utils.find_rtl_file_location("wb_gpio.v")
        slave_tags = tags["SLAVES"]["gpio1"]

        wtg = wishbone_utils.WishboneTopGenerator()
        wtg.tags = tags
        wtg.bindings = tags["bind"]
        prev = self.dbg
        #self.dbg = True

        buf = wtg.generate_parameters("gpio1",
                                      slave_tags = slave_tags,
                                      debug = self.dbg)
        if self.dbg:
            print "parameter buf:\n%s" % buf

        self.dbg = prev
        self.assertTrue(True)


    def test_generate_wishbone_slave_params(self):
        tags = {}
        top_buffer = ""
        #get the example project data
        filename = os.path.join(  self.nysa_base,
                                  "ibuilder",
                                  "example_projects",
                                  "dionysus_parameter_example.json")
        filein = open(filename)
        filestr = filein.read()
        tags = json.loads(filestr)
        slave_tags = tags["SLAVES"]["gpio1"]

        filename = utils.find_rtl_file_location("wb_gpio.v")
        module_tags = utils.get_module_tags(filename)

        wtg = wishbone_utils.WishboneTopGenerator()
        wtg.tags = tags
        wtg.bindings = tags["bind"]
        prev = self.dbg
        #self.dbg = True

        buf = wtg.generate_wishbone_buffer("gpio1",
                                           index = 1,
                                           slave_tags = slave_tags,
                                           module_tags = module_tags,
                                           debug = self.dbg)
        if self.dbg:
            print "generate wishbone buf:\n%s" % buf

        self.dbg = prev
        self.assertTrue(True)

    def test_generate_assigns(self):
        tags = {}
        top_buffer = ""
        #get the example project data
        filename = os.path.join(  self.nysa_base,
                                  "ibuilder",
                                  "example_projects",
                                  "dionysus_parameter_example.json")
        filein = open(filename)
        filestr = filein.read()
        tags = json.loads(filestr)
        slave_tags = tags["SLAVES"]["gpio1"]

        filename = utils.find_rtl_file_location("wb_gpio.v")
        module_tags = utils.get_module_tags(filename)

        wtg = wishbone_utils.WishboneTopGenerator()
        wtg.tags = tags
        wtg.bindings = tags["bind"]
        prev = self.dbg
        #self.dbg = True

        buf = wtg.generate_assigns_buffer(debug = self.dbg)
        if self.dbg:
            print "generate assign buf:\n%s" % buf

        self.dbg = prev
        self.assertTrue(True)


    def test_generate_arbitor_buffer(self):
        tags = {}
        top_buffer = ""
        #get the example project data
        filename = os.path.join(  self.nysa_base,
                                  "ibuilder",
                                  "example_projects",
                                  "dionysus_arb_example.json")
        filein = open(filename)
        filestr = filein.read()
        tags = json.loads(filestr)

        wtg = wishbone_utils.WishboneTopGenerator()
        wtg.tags = tags
        wtg.bindings = tags["bind"]
        prev = self.dbg
        #self.dbg = True

        buf = wtg.generate_arbitor_buffer(debug = self.dbg)
        if self.dbg:
            print "generate arbitor buf:\n%s" % buf

        self.dbg = prev
        self.assertTrue(True)

    def test_generate_simple_top(self):
        tags = {}
        top_buffer = ""
        #get the example project data
        filename = os.path.join(  self.nysa_base,
                                  "ibuilder",
                                  "example_projects",
                                  "dionysus_default.json")
        filein = open(filename)
        filestr = filein.read()
        filein.close()
        tags = json.loads(filestr)

        wtg = wishbone_utils.WishboneTopGenerator()
        prev = self.dbg
        self.dbg = True
        buf = wtg.generate_simple_top(tags,
                                      [],
                                      debug = self.dbg)
        if self.dbg:
            print "generate simple top buf:\n%s" % buf
            f = open("/home/cospan/sandbox/sample_top.v", 'w')
            f.write(buf)
            f.close()

        self.dbg = prev
        self.assertTrue(True)

