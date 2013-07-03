#! /usr/bin/python

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from ibuilder.lib import utils
from ibuilder.lib import constraint_utils as cu
from ibuilder.gui import wishbone_model

from ibuilder.gui.wishbone_model import SlaveType

class Test (unittest.TestCase):
    """Unit test for utils"""

    def setUp(self):
        base = os.path.join(os.path.dirname(__file__),
                            os.pardir)
        self.nysa_base = os.path.abspath(base)
        self.dbg = False


    def test_get_net_names(self):
        """gets the module tags and detects if there is any arbitor hosts"""
        filename = os.path.join(self.nysa_base, "ibuilder", "boards", "dionysus", "dionysus.ucf")
        #print "filename: %s" % filename
        constraints = cu.get_net_names(filename, self.dbg)
        #print "constraints: %s" % str(constraints)
        self.assertIn("clk", constraints)

    def test_read_clock_rate(self):
        filename = os.path.join(self.nysa_base, "ibuilder", "boards", "dionysus", "dionysus.ucf")
        rate = cu.read_clock_rate(filename)
        self.assertEquals(rate, '50000000')

    def test_has_range(self):
        has_range = cu.has_range("signal")
        self.assertFalse(has_range)
        has_range = cu.has_range("signal[1:0]")
        self.assertTrue(has_range)

    def test_parse_signal_range(self):
        name, maximum, minimum = cu.parse_signal_range("signal[31:0]")
        #print "name: %s [%d:%d]" % (name, maximum, minimum)
        self.assertEqual(name, "signal")
        self.assertEqual(maximum, 31)
        self.assertEqual(minimum, 0)

    def test_expand_user_constraints(self):
        filename = os.path.join(self.nysa_base, "ibuilder", "example_projects", "dionysus_default.json")
        self.c = wishbone_model.WishboneModel(config_file=filename)
        hib = self.c.get_host_interface_bindings()

        uc = cu.expand_user_constraints(hib)
        #print "uc: %s" % str(uc)
        #print ""
        self.assertIn("io_ftdi_data", uc.keys())

    def test_consolodate_constraints(self):
        filename = os.path.join(self.nysa_base, "ibuilder", "example_projects", "dionysus_default.json")
        self.c = wishbone_model.WishboneModel(config_file=filename)
        hib = self.c.get_host_interface_bindings()

        uc = cu.expand_user_constraints(hib)
        self.assertIn("io_ftdi_data", uc.keys())

        #print "user_dict: %s" %  str(uc)
        ud = cu.consolodate_constraints(uc, debug = self.dbg)
        self.assertIn("io_ftdi_data[7:0]", ud)

        sdram = self.c.get_slave_bindings(SlaveType.MEMORY, 0)
        #print "Pre SDRAM: %s" % str(sdram)
        sdram = cu.expand_user_constraints(sdram, debug=self.dbg)
        self.assertIn("io_sdram_data_mask", sdram)
        #print "Expanded SDRAM: %s" % str(sdram)
        ud = cu.consolodate_constraints(sdram, debug=self.dbg)
        #print "Post SDRAM: %s" % str(ud)
        self.assertIn("io_sdram_data[15:0]", ud)

        #Test the peripheral interface
        gpio = self.c.get_slave_bindings(SlaveType.PERIPHERAL, 2)
        #print "Pre GPIO: %s" % str(gpio)
        gpio = cu.expand_user_constraints(gpio, debug=self.dbg)
        self.assertIn("gpio_out", gpio)
        #print "Expanded GPIO: %s" % str(gpio)
        ud = cu.consolodate_constraints(gpio, debug=self.dbg)
        #print "Post GPIO: %s" % str(ud)
        self.assertIn("gpio_in[3:2]", ud)

        #Test another constraint file
        filename = os.path.join(self.nysa_base, "ibuilder", "example_projects", "lx9_default.json")
        self.c = wishbone_model.WishboneModel(config_file=filename)
        hib = self.c.get_host_interface_bindings()

        uc = cu.expand_user_constraints(hib)
        #print "uc: %s" % str(uc)
        self.assertIn("o_phy_uart_out", uc.keys())

        #print "user_dict: %s" %  str(uc)
        ud = cu.consolodate_constraints(uc, debug = self.dbg)
        self.assertIn("o_phy_uart_out", ud)

    def test_expand_ports(self):

        f = utils.find_rtl_file_location("wb_sdram.v")
        parameters = utils.get_module_tags(filename=f,
                                           bus="wishbone")
        c_ports = parameters["ports"]
        #print "c_ports: %s" % str(c_ports)
        e_ports = cu.expand_ports(c_ports)
        #e_ports = cu.get_only_signal_ports(e_ports)
        #print ""
        #print "e_ports: %s" % str(e_ports)
        #print ""
        self.assertFalse(e_ports["o_sdram_clk"]["range"])
        self.assertTrue(e_ports["io_sdram_data"]["range"])

        f = utils.find_rtl_file_location("wb_logic_analyzer.v")
        parameters = utils.get_module_tags(filename=f,
                                           bus="wishbone")
        c_ports = parameters["ports"]
        #print "c_ports: %s" % str(c_ports)
        e_ports = cu.expand_ports(c_ports)
        e_ports = cu.get_only_signal_ports(e_ports)
        #print ""
        #print "c_ports: %s" % str(e_ports)
        #print ""
        self.assertFalse(e_ports["o_la_uart_tx"]["range"])
        self.assertFalse(e_ports["i_la_uart_rx"]["range"])

        f = utils.find_rtl_file_location("wb_gpio.v")
        parameters = utils.get_module_tags(filename=f,
                                           bus="wishbone")
        c_ports = parameters["ports"]
        #print "c_ports: %s" % str(c_ports)
        e_ports = cu.expand_ports(c_ports)
        e_ports = cu.get_only_signal_ports(e_ports)
        #print ""
        #print "c_ports: %s" % str(e_ports)
        #print ""
        self.assertTrue(e_ports["gpio_out"]["range"])
        self.assertTrue(e_ports["gpio_in"]["range"])



    def test_get_only_signal_ports(self):
        f = utils.find_rtl_file_location("wb_sdram.v")
        parameters = utils.get_module_tags(filename=f,
                                           bus="wishbone")
        c_ports = parameters["ports"]
        e_ports = cu.expand_ports(c_ports)
        #print "e_ports: %s" % str(e_ports)
        #print ""
        ports = cu.get_only_signal_ports(e_ports)
        #print "ports: %s" % str(ports)
        #print ""
 
    def test_consolodate_ports(self):
        f = utils.find_rtl_file_location("wb_sdram.v")
        parameters = utils.get_module_tags(filename=f,
                                           bus="wishbone")
        c_ports = parameters["ports"]
        #print "c_ports: %s" % str(c_ports)
        e_ports = cu.expand_ports(c_ports)
        ports = cu.consolodate_ports(e_ports)

        for direction in ports:
            #print "Direction: %s" % direction
            for port in ports[direction]:
                #print "port: %s" % port
                self.assertIn(port, c_ports[direction].keys())
                self.assertDictEqual(ports[direction][port], c_ports[direction][port])




if __name__ == "__main__":
    unittest.main()

