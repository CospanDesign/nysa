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
        self.dbg = False

    def test_get_net_names(self):
        """gets the module tags and detects if there is any arbiter hosts"""
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
        filename = os.path.join(self.nysa_base, "test", "fake", "test_board", "board", "test.ucf")

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

