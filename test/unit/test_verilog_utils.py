#! /usr/bin/python

import unittest
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.ibuilder import verilog_utils as vutils

TEST_MODULE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       os.pardir,
                                       "fake",
                                       "test_wb_slave.v"))
#print "test module location: %s" % TEST_MODULE_LOCATION

GPIO_FILENAME = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         os.pardir,
                                         "mock",
                                         "gpio_module_tags.txt"))

CAMERA_FILENAME = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         os.pardir,
                                         "mock",
                                         "sf_camera_module_tags.txt"))

class Test (unittest.TestCase):
    """Unit test for verilog_utils"""

    def setUp(self):
        base = os.path.join( os.path.dirname(__file__),
                             os.pardir)
        self.nysa_base = os.path.abspath(base)
        f = open(GPIO_FILENAME, "r")
        self.gpio_tags = json.load(f)
        f.close()

        f = open(CAMERA_FILENAME, "r")
        self.camera_tags = json.load(f)
        f.close()

        self.dbg = False

    def test_get_module_buffer_tags(self):
        f = open(TEST_MODULE_LOCATION, "r")
        module_buffer = f.read()
        f.close()
        tags = vutils.get_module_buffer_tags(module_buffer)
        #print "tags: %s" % str(tags)
        assert "parameters" in tags
        assert "keywords" in tags
        assert "arbiter_masters" in tags
        assert "module" in tags
        assert tags["module"] == "wb_test"
        assert "ports" in tags

    def test_get_module_tags(self):
        tags = vutils.get_module_tags(TEST_MODULE_LOCATION)
        #print "tags: %s" % str(tags)
        assert "parameters" in tags
        assert "keywords" in tags
        assert "arbiter_masters" in tags
        assert "module" in tags
        assert tags["module"] == "wb_test"
        assert "ports" in tags

    def test_remove_comments(self):
        """try and remove all comments from a buffer"""
        bufin = "not comment/*comment\n*/\n//comment\n/*\nabc\n*/something//comment"
        output_buffer = vutils.remove_comments(bufin)
        good = "not comment\n\nsomething\n"
        self.assertEqual(output_buffer, good)

    def test_generate_module_port_signals(self):
        buf = vutils.generate_module_port_signals(invert_reset = False,
                                                  name = "gpio_device",
                                                  prename = "test",
                                                  module_tags = self.gpio_tags)

        test_str = ""\
        "wb_gpio #(\n"\
        "  .DEFAULT_INTERRUPT_MASK(0                 ),\n"\
        "  .DEFAULT_INTERRUPT_EDGE(0                 )\n"\
        ")gpio_device (\n"\
        "  .clk                 (clk                 ),\n"\
        "  .rst                 (rst                 ),\n"\
        "\n" \
        "  //inputs\n"\
        "  .gpio_in             (test_gpio_in        ),\n"\
        "  .i_wbs_adr           (test_i_wbs_adr      ),\n"\
        "  .i_wbs_cyc           (test_i_wbs_cyc      ),\n"\
        "  .i_wbs_dat           (test_i_wbs_dat      ),\n"\
        "  .i_wbs_sel           (test_i_wbs_sel      ),\n"\
        "  .i_wbs_stb           (test_i_wbs_stb      ),\n"\
        "  .i_wbs_we            (test_i_wbs_we       ),\n"\
        "\n" \
        "  //outputs\n"\
        "  .debug               (test_debug          ),\n"\
        "  .gpio_out            (test_gpio_out       ),\n"\
        "  .o_wbs_ack           (test_o_wbs_ack      ),\n"\
        "  .o_wbs_dat           (test_o_wbs_dat      ),\n"\
        "  .o_wbs_int           (test_o_wbs_int      )\n"\
        ");"

        #print "signals: %s" % str(buf)
        #signals = vutils.generate_module_port_signals(invert_reset = False,
        #                                              name = "camera_device",
        #                                              prename = "test_camera",
        #                                              module_tags = self.camera_tags)
        #print "signals: %s" % str(signals)
        assert test_str in buf



    def test_get_port_count(self):
        port_count = vutils.get_port_count(self.gpio_tags)
        assert port_count == 14

    def test_create_reg_buf_from_dict_single(self):
        buf = vutils.create_reg_buf_from_dict("test", {"size":1})
        assert "reg                     test;" in buf

    def test_create_reg_buf_from_dict_array(self):
        d = {"size":2, "max_val":1, "min_val":0}
        buf = vutils.create_reg_buf_from_dict("test", d)
        assert "reg [1:0]               test;" in buf

    def test_create_reg_buf_single(self):
        buf = vutils.create_reg_buf("test", size = 1, max_val = 0, min_val = 0)
        assert "reg                     test;" in buf

    def test_create_reg_buf_array(self):
        buf = vutils.create_reg_buf("test", size = 2, max_val = 1, min_val = 0)
        assert "reg [1:0]               test;" in buf

    def test_create_wire_buf_from_dict_single(self):
        buf = vutils.create_wire_buf_from_dict("test", {"size":1})
        assert "wire                    test;" in buf

    def test_create_wire_buf_from_dict_array(self):
        d = {"size":2, "max_val":1, "min_val":0}
        buf = vutils.create_wire_buf_from_dict("test", d)
        assert "wire  [1:0]             test;" in buf

    def test_create_wire_buf_single(self):
        d = {"size":2, "max_val":1, "min_val":0}
        buf = vutils.create_wire_buf("test", size = 1, max_val = 0, min_val = 0)
        assert "wire                    test;" in buf

    def test_create_wire_buf_single(self):
        d = {"size":2, "max_val":1, "min_val":0}
        buf = vutils.create_wire_buf("test", size = 2, max_val = 1, min_val = 0)
        assert "wire  [1:0]             test;" in buf

    def test_generate_assigns_buffer(self):
	bind = {"test1":{"direction":"input", "loc":"clk"}, "test2":{"direction":"input","loc":"rst"}}
	ibind = {"a":{"signal":"test1"}}

        buf = vutils.generate_assigns_buffer(invert_reset = False,
                                             bindings = bind,
                                             internal_bindings = ibind)
        #print "buf: %s" % buf
        #f = open("/home/cospan/sandbox/register_buf.txt", "w")
        bind_str = ""\
            "//Internal Bindings\n"\
            "assign  a                   = test1;\n"\
            "\n"\
            "\n"\
            "//Bindings\n"\
            "assign  test1               = clk;\n"\
            "assign  test2               = rst;\n"

        assert bind_str in buf

    def test_port_cmp(self):
        assert vutils.port_cmp("p[0]", "p[1]") == -1
        assert vutils.port_cmp("p[1]", "p[1]") == 0
        assert vutils.port_cmp("p[10]", "p[1]") == -1

if __name__ == "__main__":
    unittest.main()

