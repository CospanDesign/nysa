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

class Test (unittest.TestCase):
    """Unit test for verilog_utils"""

    def setUp(self):
        base = os.path.join( os.path.dirname(__file__),
                             os.pardir)
        self.nysa_base = os.path.abspath(base)
        self.dbg = False

    def test_get_sim_module_dict_pass(self):
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

        self.dbg = prev_dbg
        self.assertIsNotNone(sdict)




    def test_generate_sim_module_buf(self):
        """Test generate sim moulde buf"""

        module_name = "wb_sdram"
        user_paths = []
        prev_dbg = self.dbg
        #self.dbg = True
        buf = sutils.generate_sim_module_buf(False,
                                             test_dict["name"],
                                             test_dict,
                                             debug = self.dbg)
        if self.dbg:
            print "sim module buffer:\n%s" % buf
        self.dbg = prev_dbg

    def test_generate_tb_module_port(self):
        sutils.generate_tb_module_ports()

