#! /usr/bin/python

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, 'nysa'))

from ibuilder.lib import sim_utils as sutils
from ibuilder.lib import utils
from ibuilder.lib.ibuilder_error import IBuilderError

test_dict = {
  "name":"mt48lc4m16",
  "aux_files":[
    "mt48lc4m16.ftmv",
    "mt48lc4m16.mem"
  ],
  "bind":{
    "A11"     : "o_sdram_addr[11]",
    "A10"     : "o_sdram_addr[10]",
    "A9"      : "o_sdram_addr[9]",
    "A8"      : "o_sdram_addr[8]",
    "A7"      : "o_sdram_addr[7]",
    "A6"      : "o_sdram_addr[6]",
    "A5"      : "o_sdram_addr[5]",
    "A4"      : "o_sdram_addr[4]",
    "A3"      : "o_sdram_addr[3]",
    "A2"      : "o_sdram_addr[2]",
    "A1"      : "o_sdram_addr[1]",
    "A0"      : "o_sdram_addr[0]",

    "DQ15"    : "io_sdram_data[15]",
    "DQ14"    : "io_sdram_data[14]",
    "DQ13"    : "io_sdram_data[13]",
    "DQ12"    : "io_sdram_data[12]",
    "DQ11"    : "io_sdram_data[11]",
    "DQ10"    : "io_sdram_data[10]",
    "DQ9"     : "io_sdram_data[9]",
    "DQ8"     : "io_sdram_data[8]",
    "DQ7"     : "io_sdram_data[7]",
    "DQ6"     : "io_sdram_data[6]",
    "DQ5"     : "io_sdram_data[5]",
    "DQ4"     : "io_sdram_data[4]",
    "DQ3"     : "io_sdram_data[3]",
    "DQ2"     : "io_sdram_data[2]",
    "DQ1"     : "io_sdram_data[1]",
    "DQ0"     : "io_sdram_data[0]",

    "CLK"     : "o_sdram_clk",
    "CKE"     : "o_sdram_cke",
    "CASeg"   : "o_sdram_cs_n",
    "RASNeg"  : "o_sdram_ras",
    "CASNeg"  : "o_sdram_cas",
    "WENeg"   : "o_sdram_we",
    "BA1"     : "o_sdram_bank[1]",
    "BA0"     : "o_sdram_bank[0]",
    "DQMH"    : "o_sdram_data_mask[1]",
    "DQML"    : "o_sdram_data_mask[0]"
  }
}

top_buffer = " "\
    "module top (\n"\
    "  input                 sim_in_ready,\n"\
    "  output      [27:0]    sim_out_data_count,\n"\
    "  output                cas,\n"\
    "  input       [31:0]    sim_in_command,\n"\
    "  output                sim_out_en,\n"\
    "  output                we,\n"\
    "  output                dqmh,\n"\
    "  input                 s1,\n"\
    "  output                sim_master_ready,\n"\
    "  input                 sim_out_ready,\n"\
    "  output                cke,\n"\
    "  output      [11:0]    a,\n"\
    "  output                ras,\n"\
    "  input       [1:0]     button,\n"\
    "  inout       [15:0]    dq,\n"\
    "  input       [31:0]    sim_in_data,\n"\
    "  output      [1:0]     ba,\n"\
    "  output      [31:0]    sim_out_data,\n"\
    "  input       [31:0]    sim_in_address,\n"\
    "  output      [1:0]     led,\n"\
    "  output                dqml,\n"\
    "  output      [31:0]    sim_out_address,\n"\
    "  output                s0,\n"\
    "  input       [31:0]    sim_in_data_count,\n"\
    "  output      [31:0]    sim_out_status,\n"\
    "  input                 sim_in_reset,\n"\
    "  output                cs_n,\n"\
    "  output                sdram_clk\n"\
    ");\n"\
    "endmodule"

tb_tags = {
}

tags = {
	"BASE_DIR":"~/projects/ibuilder_project",
	"board":"dionysus",
	"PROJECT_NAME":"example_project",
	"TEMPLATE":"wishbone_template.json",
	"INTERFACE":{},
    "SLAVES":{},
    "MEMORY":{
        "mem1":{
            "filename":"wb_sdram.v",
            "sim":True
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

    def test_get_sim_module_dic(self):
        """
        Test the function to get the dictionary of the interface to the test
        module of the specified module (Sorry this is confusing)
        """
        module_name = "wb_sdram"
        user_paths = []
        prev_dbg = self.dbg
        #self.dbg = True
        sdict = sutils.get_sim_module_dict(module_name,
                                           user_paths,
                                           debug = self.dbg)

        if self.dbg:
            utils.pretty_print_dict(sdict)
        self.dbg = prev_dbg
        self.assertIsNotNone(sdict)

    def test_generate_sub_slave_dict(self):
        user_paths = []
        prev_dbg = self.dbg
        #self.dbg = True
        module_name = "wb_sdram"
        sdict = sutils.get_sim_module_dict(module_name,
                                           user_paths)

        module_tags = sutils.generate_sub_slave_dict(sdict,
                                                     debug = self.dbg)

        if self.dbg:
            utils.pretty_print_dict(module_tags)

        self.dbg = prev_dbg

    def test_generate_tb_module(self):
        user_paths = []
        prev_dbg = self.dbg
        #self.dbg = True
        tb = sutils.generate_tb_module(tags,
                                       top_buffer,
                                       user_paths = [],
                                       debug = self.dbg)
        if self.dbg:
            #print "tb\n"
            #print  tb
            f = open("/home/cospan/sandbox/tb.v", "w")
            f.write(tb)
            f.close()
        self.dbg = prev_dbg

