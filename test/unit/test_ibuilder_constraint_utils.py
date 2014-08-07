#! /usr/bin/python

import unittest
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))


#from ibuilder.lib import utils
from nysa.ibuilder.lib import constraint_utils as cu
from nysa.ibuilder.gui.wishbone_model import SlaveType
from nysa.ibuilder.gui import wishbone_model

TEST_CONSTRAINT = ""\
        "NET \"clk\"           LOC = C10 | IOSTANDARD = LVCMOS33;\n" \
        "NET \"clk\" TNM_NET       = \"clk\";\n" \
        "TIMESPEC \"TS_clk\"       = PERIOD \"clk\" 100000 kHz;\n" \
        "\n" \
        "NET \"gpio<0>\"       LOC = B3  | IOSTANDARD = LVCMOS33 | PULLDOWN;\n" \
        "\n" \
        "\n" \
        "NET \"rst\"           LOC = V4  | IOSTANDARD = LVCMOS33 | PULLDOWN;\n" \
        "NET \"rst\"           TIG;\n" \
        "\n" \
        "NET \"uart_rx\"       LOC = R7  | IOSTANDARD = LVCMOS33;\n" \
        "NET \"uart_tx\"       LOC = T7  | IOSTANDARD = LVCMOS33;\n" \
        "\n" \
        "\n" \
        "CONFIG VCCAUX = \"3.3\" ;"


EXPANDED_CONSTRAINTS_STR = ""\
        "{\n"\
        "  \"io_ftdi_data\": {  \"0\": {\"loc\": \"d[0]\", \"direction\": \"inout\"},\n"\
        "                       \"1\": {\"loc\": \"d[1]\", \"direction\": \"inout\"},\n"\
        "                       \"range\": true\n"\
        "                    },\n"\
        "  \"i_ftdi_clk\":  {   \"loc\": \"ftdi_clk\", \"direction\": \"input\", \"range\": false}\n"\
        "}"
EXPANDED_CONSTRAINTS = json.loads(EXPANDED_CONSTRAINTS_STR)

CONSOLODATED_CONSTRAINTS_STR = ""\
        "{ \n" \
        "\"i_ftdi_clk\": {\"loc\": \"ftdi_clk\", \"direction\": \"input\"}, \n" \
        "\"io_ftdi_data[1:0]\": {\"loc\": \"d[1:0]\", \"direction\": \"inout\"} \n" \
        "}"

CONSOLODATED_CONSTRAINTS = json.loads(CONSOLODATED_CONSTRAINTS_STR)

TEST_CONFIG_FILENAME = os.path.abspath( os.path.join(os.path.dirname(__file__),
                                        os.path.pardir,
                                        "fake",
                                        "test_config_file.json"))

TEST_CCONSTRAINTS_FNAME = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        os.path.pardir,
                                        "mock",
                                        "consolodated_constraints.txt"))

class Test (unittest.TestCase):
    """Unit test for utils"""

    def setUp(self):
        base = os.path.join(os.path.dirname(__file__),
                            os.pardir,
                            os.pardir)

        self.nysa_base = os.path.abspath(base)
        f = open(TEST_CONFIG_FILENAME, "r")
        self.test_config = json.load(f)
        f.close()

        #f = open(TEST_CCONSTRAINTS_FNAME, "r")
        #self.consolodated_constraints = json.load(f)
        #f.close()

        self.dbg = False

    def test_get_net_names(self):
        """gets the module tags and detects if there is any arbitor hosts"""
        constraints = cu.get_net_names_from_buffer(TEST_CONSTRAINT, self.dbg)
        test_result = ["clk", "rst", "gpio[0]", "uart_rx", "uart_tx"]
        assert len(test_result) == len(constraints)
        for r in test_result:
            assert r in constraints

    def test_get_net_names_from_file(self):
        filename = os.path.join(self.nysa_base, "test", "fake", "lx9.ucf")
        constraints = cu.get_net_names(filename, self.dbg)
        test_result = [ "clk",
                        "rst",
                        "gpio[0]",
                        "gpio[1]",
                        "gpio[2]",
                        "gpio[3]",
                        "led[0]",
                        "led[1]",
                        "led[2]",
                        "led[3]",
                        "uart_rx",
                        "uart_tx"]

        assert len(test_result) == len(constraints)
        for r in test_result:
            assert r in constraints

    def test_read_clock_rate_from_buffer(self):
        test_ucf = ""\
            "NET \"clk\"     LOC = P51;\n" \
            "TIMESPEC \"ts_clk\" = PERIOD \"clk\" 20 ns HIGH 50%;\n"

        rate = cu.read_clock_rate_from_buffer(test_ucf)
        self.assertEquals(rate, '50000000')

    def test_read_clock_rate(self):
        filename = os.path.join(self.nysa_base, "test", "fake", "test_board", "test.ucf")

        rate = cu.read_clock_rate(filename)
        self.assertEquals(rate, '50000000')


    def test_parse_signal_range(self):
        name, maximum, minimum = cu.parse_signal_range("signal[31:0]")
        #print "name: %s [%d:%d]" % (name, maximum, minimum)
        self.assertEqual(name, "signal")
        self.assertEqual(maximum, 31)
        self.assertEqual(minimum, 0)

    def test_has_range(self):
        has_range = cu.has_range("signal")
        self.assertFalse(has_range)
        has_range = cu.has_range("signal[1:0]")
        self.assertTrue(has_range)

    def test_expand_user_constraints(self):
        uc = cu.expand_user_constraints(CONSOLODATED_CONSTRAINTS)
        self.assertIn("io_ftdi_data", uc)

    def test_consolodate_constraints(self):
        print "uc: %s" % str(EXPANDED_CONSTRAINTS)
        ud = cu.consolodate_constraints(EXPANDED_CONSTRAINTS, debug = True)
        self.assertIn("io_ftdi_data[1:0]", ud)

'''
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
        filename = os.path.join(self.nysa_base, "nysa", "ibuilder", "example_projects", "lx9_default.json")
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


'''


if __name__ == "__main__":
    unittest.main()

