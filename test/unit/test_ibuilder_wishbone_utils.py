#! /usr/bin/python

import unittest
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))
from tutils import save_file

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.ibuilder import wishbone_utils as wu
from nysa.ibuilder.wishbone_utils import WishboneTopGenerator


GPIO_FILENAME = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         os.pardir,
                                         "mock",
                                         "gpio_module_tags.txt"))

TEST_CONFIG_FILENAME = os.path.abspath( os.path.join(os.path.dirname(__file__),
                                        os.path.pardir,
                                        "fake",
                                        "test_config_file.json"))

SIMPLE_TOP_FILENAME = os.path.abspath(  os.path.join(os.path.dirname(__file__),
                                        os.path.pardir,
                                        "fake",
                                        "simple_top.txt"))



WISHBONE_SIGNALS = ["i_wbs_we",
                    "i_wbs_stb",
                    "i_wbs_cyc",
                    "i_wbs_sel",
                    "i_wbs_adr",
                    "i_wbs_dat",
                    "o_wbs_dat",
                    "o_wbs_ack",
                    "o_wbs_int"]

WISHBONE_BUS_SIGNALS = [
                    "o_%s_we",
                    "o_%s_stb",
                    "o_%s_cyc",
                    "o_%s_sel",
                    "o_%s_adr",
                    "o_%s_dat",
                    "i_%s_dat",
                    "i_%s_ack",
                    "i_%s_int"]


STARTUP_BUFFER = ""\
                 "//Startup reset\n"\
                 "\n"\
                 "wire                 startup_rst;\n"\
                 "\n"\
                 "startup start(\n"\
                 "  .clk                 (clk                 ),\n"\
                 "  .startup_rst         (startup_rst         )\n"\
                 ");"

PERIPHERAL_INTERCONNECT = ""\
                                   "//Wishbone Memory Interconnect\n" \
                                   "\n" \
                                   "wishbone_interconnect wi (\n" \
                                   "  .clk                 (clk                 ),\n" \
                                   "  .rst                 (rst | startup_rst   ),\n" \
                                   "\n" \
                                   "  //master\n" \
                                   "  .i_m_we              (w_wbm_we_o          ),\n" \
                                   "  .i_m_cyc             (w_wbm_cyc_o         ),\n" \
                                   "  .i_m_stb             (w_wbm_stb_o         ),\n" \
                                   "  .i_m_sel             (w_wbm_sel_o         ),\n" \
                                   "  .o_m_ack             (w_wbm_ack_i         ),\n" \
                                   "  .i_m_dat             (w_wbm_dat_o         ),\n" \
                                   "  .o_m_dat             (w_wbm_dat_i         ),\n" \
                                   "  .i_m_adr             (w_wbm_adr_o         ),\n" \
                                   "  .o_m_int             (w_wbm_int_i         ),\n" \
                                   "\n" \
                                   "  //slave 0\n" \
                                   "  .o_s0_we             (w_s0_i_wbs_we       ),\n" \
                                   "  .o_s0_cyc            (w_s0_i_wbs_cyc      ),\n" \
                                   "  .o_s0_stb            (w_s0_i_wbs_stb      ),\n" \
                                   "  .o_s0_sel            (w_s0_i_wbs_sel      ),\n" \
                                   "  .i_s0_ack            (w_s0_o_wbs_ack      ),\n" \
                                   "  .o_s0_dat            (w_s0_i_wbs_dat      ),\n" \
                                   "  .i_s0_dat            (w_s0_o_wbs_dat      ),\n" \
                                   "  .o_s0_adr            (w_s0_i_wbs_adr      ),\n" \
                                   "  .i_s0_int            (w_s0_o_wbs_int      )\n" \
                                   ");"

MEMORY_INTERCONNECT = ""\
                                   "//Wishbone Memory Interconnect\n" \
                                   "\n" \
                                   "wishbone_mem_interconnect wmi (\n" \
                                   "  .clk                 (clk                 ),\n" \
                                   "  .rst                 (rst | startup_rst   ),\n" \
                                   "\n" \
                                   "  //master\n" \
                                   "  .i_m_we              (w_mem_we_o          ),\n" \
                                   "  .i_m_cyc             (w_mem_cyc_o         ),\n" \
                                   "  .i_m_stb             (w_mem_stb_o         ),\n" \
                                   "  .i_m_sel             (w_mem_sel_o         ),\n" \
                                   "  .o_m_ack             (w_mem_ack_i         ),\n" \
                                   "  .i_m_dat             (w_mem_dat_o         ),\n" \
                                   "  .o_m_dat             (w_mem_dat_i         ),\n" \
                                   "  .i_m_adr             (w_mem_adr_o         ),\n" \
                                   "  .o_m_int             (w_mem_int_i         ),\n" \
                                   "\n" \
                                   "\n" \
                                   "  //slave 0\n" \
                                   "  .o_s0_we             (w_sm0_i_wbs_we      ),\n" \
                                   "  .o_s0_cyc            (w_sm0_i_wbs_cyc     ),\n" \
                                   "  .o_s0_stb            (w_sm0_i_wbs_stb     ),\n" \
                                   "  .o_s0_sel            (w_sm0_i_wbs_sel     ),\n" \
                                   "  .i_s0_ack            (w_sm0_o_wbs_ack     ),\n" \
                                   "  .o_s0_dat            (w_sm0_i_wbs_dat     ),\n" \
                                   "  .i_s0_dat            (w_sm0_o_wbs_dat     ),\n" \
                                   "  .o_s0_adr            (w_sm0_i_wbs_adr     ),\n" \
                                   "  .i_s0_int            (w_sm0_o_wbs_int     )\n" \
                                   ");"

MASTER_BUFFER = ""\
                                   "//Wishbone Master\n" \
                                   "\n" \
                                   "wishbone_master wm (\n" \
                                   "  .clk                 (clk                 ),\n" \
                                   "  .rst                 (rst | startup_rst   ),\n" \
                                   "\n" \
                                   "  //input handler signals\n" \
                                   "  .i_ready             (ih_ready            ),\n" \
                                   "  .i_ih_rst            (ih_reset            ),\n" \
                                   "  .i_command           (in_command          ),\n" \
                                   "  .i_address           (in_address          ),\n" \
                                   "  .i_data              (in_data             ),\n" \
                                   "  .i_data_count        (in_data_count       ),\n" \
                                   "\n" \
                                   "  //output handler signals\n" \
                                   "  .i_out_ready         (oh_ready            ),\n" \
                                   "  .o_en                (oh_en               ),\n" \
                                   "  .o_status            (out_status          ),\n" \
                                   "  .o_address           (out_address         ),\n" \
                                   "  .o_data              (out_data            ),\n" \
                                   "  .o_data_count        (out_data_count      ),\n" \
                                   "  .o_master_ready      (master_ready        ),\n" \
                                   "\n" \
                                   "  //interconnect signals\n" \
                                   "  .o_per_we            (w_wbm_we_o          ),\n" \
                                   "  .o_per_adr           (w_wbm_adr_o         ),\n" \
                                   "  .o_per_dat           (w_wbm_dat_o         ),\n" \
                                   "  .i_per_dat           (w_wbm_dat_i         ),\n" \
                                   "  .o_per_stb           (w_wbm_stb_o         ),\n" \
                                   "  .o_per_cyc           (w_wbm_cyc_o         ),\n" \
                                   "  .o_per_msk           (w_wbm_msk_o         ),\n" \
                                   "  .o_per_sel           (w_wbm_sel_o         ),\n" \
                                   "  .i_per_ack           (w_wbm_ack_i         ),\n" \
                                   "  .i_per_int           (w_wbm_int_i         ),\n" \
                                   "\n" \
                                   "  //memory interconnect signals\n" \
                                   "  .o_mem_we            (w_mem_we_o          ),\n" \
                                   "  .o_mem_adr           (w_mem_adr_o         ),\n" \
                                   "  .o_mem_dat           (w_mem_dat_o         ),\n" \
                                   "  .i_mem_dat           (w_mem_dat_i         ),\n" \
                                   "  .o_mem_stb           (w_mem_stb_o         ),\n" \
                                   "  .o_mem_cyc           (w_mem_cyc_o         ),\n" \
                                   "  .o_mem_msk           (w_mem_msk_o         ),\n" \
                                   "  .o_mem_sel           (w_mem_sel_o         ),\n" \
                                   "  .i_mem_ack           (w_mem_ack_i         ),\n" \
                                   "  .i_mem_int           (w_mem_int_i         ),\n" \
                                   "\n" \
                                   "  .o_debug             (wbm_debug_out       )\n" \
                                   "\n" \
                                   ");"

MODULE_PORT_SIGNALS = ""\
                                   "(\n" \
                                   "  .clk                 (clk                 ),\n" \
                                   "  .rst                 (rst | startup_rst   ),\n" \
                                   "  .i_wbs_cyc           (w_prenamei_wbs_cyc  ),\n" \
                                   "  .i_wbs_stb           (w_prenamei_wbs_stb  ),\n" \
                                   "  .i_wbs_adr           (w_prenamei_wbs_adr  ),\n" \
                                   "  .i_wbs_we            (w_prenamei_wbs_we   ),\n" \
                                   "  .i_wbs_dat           (w_prenamei_wbs_dat  ),\n" \
                                   "  .gpio_in             (gpio1_gpio_in       ),\n" \
                                   "  .i_wbs_sel           (w_prenamei_wbs_sel  ),\n" \
                                   "  .debug               (gpio1_debug         ),\n" \
                                   "  .o_wbs_int           (w_prenameo_wbs_int  ),\n" \
                                   "  .gpio_out            (gpio1_gpio_out      ),\n" \
                                   "  .o_wbs_ack           (w_prenameo_wbs_ack  ),\n" \
                                   "  .o_wbs_dat           (w_prenameo_wbs_dat  )\n" \
                                   ");"

ASSIGN_BUFFER = ""\
                                   "//Internal Bindings\n" \
                                   "assign  ib1                 = test1;\n" \
                                   "assign  ib2                 = test2;\n" \
                                   "\n" \
                                   "\n" \
                                   "//Bindings\n" \
                                   "assign  b1                  = test3;\n" \
                                   "assign  test4               = b3;\n"


class Test (unittest.TestCase):
    """Unit test for wishbone_utils"""
    def setUp(self):
        base = os.path.join( os.path.dirname(__file__),
                             os.path.pardir,
                             os.path.pardir)
        self.nysa_base = os.path.abspath(base)
        f = open(GPIO_FILENAME, "r")
        self.gpio_tags = json.load(f)
        f.close()

        f = open(TEST_CONFIG_FILENAME, "r")
        self.test_config = json.load(f)
        f.close()

        f = open(SIMPLE_TOP_FILENAME, "r")
        self.simple_top = f.read()
        f.close()


        self.dbg = False

    def test_is_wishbone_slave_signal(self):
        for s in WISHBONE_SIGNALS:
            signal = "%s %s" % (s, "test")
            assert wu.is_wishbone_slave_signal(signal)

    def test_is_wishbone_slave_signal_fail(self):
        assert not wu.is_wishbone_slave_signal("not a wishbone signal")

    def test_is_wishbone_bus_signal(self):
        for s in WISHBONE_SIGNALS:
            signal = "%s %s" % (s, "test")
            assert wu.is_wishbone_bus_signal(signal)

        for s in WISHBONE_BUS_SIGNALS:
            signal = s % "test"
            #print "signal: %s" % signal
            assert wu.is_wishbone_bus_signal(signal)

    def test_is_wishbone_bus_signal_fail(self):
        assert not wu.is_wishbone_bus_signal("not a wishbone signal")

    def test_generate_startup(self):
        startup_buffer = wu.generate_startup()
        assert STARTUP_BUFFER in startup_buffer

    def test_generate_peripheral_wishbone_interconnect_buffer(self):
        buf = wu.generate_peripheral_wishbone_interconnect_buffer(1, False)
        assert PERIPHERAL_INTERCONNECT in buf
        #save_file("temp", buf)

    def test_generate_memory_wishbone_interconnect_buffer(self):
        buf = wu.generate_memory_wishbone_interconnect_buffer(1, False)
        assert MEMORY_INTERCONNECT in buf

    def test_generate_master_buffer(self):
        buf = wu.generate_master_buffer(False)
        assert MASTER_BUFFER in buf

    def test_create_wire_buf_single_port(self):
        assert wu.create_wire_buf("test", 1, 0, 0) == "wire                 test;\n"

    def test_create_wire_buf_array_port(self):
        assert wu.create_wire_buf("test", 4, 3, 0) == "wire  [3:0]          test;\n"
        #save_file("temp", buf)

    def test_get_port_count(self):
        module_tags = {"ports":{
                                "inout":{
                                    "p1":{},
                                    "p2":{}
                                },
                                "input":{
                                    "p3":{},
                                    "p4":{}
                                },
                                "output":{
                                     "p5":{},
                                     "p6":{}
                                }
                            }
                        }
        assert wu.get_port_count(module_tags) == 6

    def test_generate_module_port_signals(self):
        buf = wu.generate_module_port_signals(invert_reset = False,
                                        wishbone_prename = "prename",
                                        instance_name = "gpio1",
                                        slave_tags = self.test_config["SLAVES"]["gpio1"],
                                        module_tags = self.gpio_tags,
                                        debug = True)
        #save_file("temp", buf)
        assert MODULE_PORT_SIGNALS in buf

    def test_generate_assigns_buffer(self):
        internal_bindings = {
                                "ib1":{"signal":"test1"},
                                "ib2":{"signal":"test2"}
                            }
        bindings =          {
                                "b1":{
                                    "direction":"input",
                                    "loc":"test3"
                                },
                                "b2":{
                                    "direction":"inout",
                                    "loc":"shouldnt_connect"
                                },
                                "b3":{
                                    "direction":"output",
                                    "loc":"test4"
                                }
                            }


        buf = wu.generate_assigns_buffer(invert_reset = False,
                                         bindings = bindings,
                                         internal_bindings = internal_bindings,
                                         debug = False)
        save_file("temp", buf)

        assert ASSIGN_BUFFER in buf

    def test_generate_simple_top(self):
        wt = WishboneTopGenerator()
        buf = wt.generate_simple_top(self.test_config)
        buf = buf.strip()
        self.simple_top = self.simple_top.strip()
        self.assertEqual(self.simple_top, buf)

if __name__ == "__main__":
  unittest.main()

