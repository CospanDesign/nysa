#! /usr/bin/python
import unittest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.ibuilder.lib import preprocessor
from nysa.ibuilder.lib import utils

TEST_MODULE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       os.pardir,
                                       "fake",
                                       "test_wb_slave.v"))
#print "test module location: %s" % TEST_MODULE_LOCATION



class Test (unittest.TestCase):
    """Unit test for the verilog pre-processor module"""

    def setUp(self):
        base = os.path.join( os.path.dirname(__file__), "..")
        self.nysa_base = os.path.abspath(base)
        self.dbg = False
        f = open(TEST_MODULE_LOCATION, "r")
        self.module_buffer = f.read()
        f.close()

    def test_generate_define_table(self):
        """generate a define table given a file"""
        self.module_buffer = "`define TEST_DEFINE 1"
        result = preprocessor.generate_define_table(self.module_buffer, debug = self.dbg)
        self.assertEqual(result["TEST_DEFINE"], '1')

    def test_resolve_one_define(self):
        """First test to see if the system will replace a define"""
        define_dict = {'TEST_DEFINE':1}
        result = preprocessor.resolve_defines("`TEST_DEFINE", define_dict, debug = self.dbg)
        self.assertEqual(int(result, 10), 1)

    def test_resolve_non_wsp_define(self):
        """First test to see if the system will replace a define that isn't separated by whitespaces"""
        define_dict = {'TEST_DEFINE':1}
        result = preprocessor.resolve_defines("`TEST_DEFINE:0", define_dict, debug = self.dbg)
        self.assertEqual(result, '1:0')

    def test_resolve_multiple_defines(self):
        """second easiest test, this one requires multiple passes of the
        replacement string"""
        buf = "\n\n\
              `define B 1\n\
              `define A `B\n\
              module test ();\n\
              endmodule"

        define_dict = preprocessor.generate_define_table(buf, debug=False)
        result = preprocessor.resolve_defines("`B:`A", define_dict, debug=False)
        self.assertEqual(result, '1:1')

    def test_evaluate_range(self):
        """test whether resolve string will get rid of parenthesis"""
        result = preprocessor.evaluate_range("val[(48 -12):0]", debug = self.dbg)
        self.assertEqual(result == "val[36:0]", True)

    def test_complicated_string(self):
        """Hardest test of all, filled with multiple replacements and
        all of the pre-processing techniques"""
        buf = "\n\n\
              `define B 2 \n\
              `define A `B \n\
              `define C 4 \n\
              module test ();\n\
              endmodule"

        define_dict = preprocessor.generate_define_table(buf, debug=False)
        result = preprocessor.resolve_defines("val[(`A * `B * `C):((`C)-(`A))]", define_dict, debug = self.dbg)
        result = preprocessor.evaluate_range(result, define_dict, debug=False)
        #print "result: %s" % result

        self.assertEqual(result, "val[16:2]")

if __name__ == "__main__":
  unittest.main()
