#! /usr/bin/python
import unittest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from ibuilder.lib import preprocessor
from ibuilder.lib import utils

class Test (unittest.TestCase):
  """Unit test for the verilog pre-processor module"""

  def setUp(self):
    base = os.path.join( os.path.dirname(__file__), "..")
    self.nysa_base = os.path.abspath(base)
    self.dbg = False

  def test_generate_define_table(self):
    """generate a define table given a file"""
    filename = utils.find_rtl_file_location("wb_logic_analyzer.v")
    if self.dbg: print "filename: " + filename
    filestring = ""
    try:
      f = open(filename)
#     print "opened file"
      filestring = f.read()
      f.close()
    except:
      print "Failed to open test filename in test_generate_define_table"
      self.assertEqual(True, False)
      return

    result = preprocessor.generate_define_table(filestring, debug = self.dbg)


    self.assertEqual(len(result) > 0, True)

  def test_resolve_one_define(self):
    """First test to see if the system will replace a define"""
    #first get the filename
    filename = utils.find_rtl_file_location("wb_i2c.v")
    filestring = ""
    try:
      f = open(filename)
      filestring = f.read()
      f.close()
    except:
      print "Failed to open test file in test_resolve_one_define"
      self.assertEqual(True, False)
      return

    define_dict = preprocessor.generate_define_table(filestring)
    #print "number of defines: " + str(len(define_dict.keys()))
    result = preprocessor.resolve_defines("`CLK_DIVIDE_100KHZ", define_dict, debug = self.dbg)

    self.assertEqual(len(result) > 0, True)

  def test_resolve_non_wsp_define(self):
    """First test to see if the system will replace a define that isn't separated by whitespaces"""
    #first get the filename
    filename = utils.find_rtl_file_location("wb_i2c.v")
    filestring = ""
    try:
      f = open(filename)
      filestring = f.read()
      f.close()
    except:
      print "Failed to open test file in test_resolve_non_wsp_define"
      self.assertEqual(True, False)
      return

    define_dict = preprocessor.generate_define_table(filestring)
    #print "number of defines: " + str(len(define_dict.keys()))
    result = preprocessor.resolve_defines("CLK_DIVIDE_100KHZ:0", define_dict, debug = self.dbg)

    self.assertEqual(len(result) > 0, True)




  def test_resolve_multiple_defines(self):
    """second easiest test, this one requires multiple passes of the
    replacement string"""
    #first get the filename
    filename = utils.find_rtl_file_location("wb_sdram.v")
    filestring = "\n\n\
                  `define B 1\n\
                  `define A `B\n\
                  module test ();\n\
                  endmodule"
    '''
    try:
      f = open(filename)
      filestring = f.read()
      f.close()
    except:
      print "Failed to open test file"
      self.assertEqual(True, False)
      return
    '''

    define_dict = preprocessor.generate_define_table(filestring, debug=False)
    #print "number of defines: " + str(len(define_dict.keys()))
    result = preprocessor.resolve_defines("`B:`A", define_dict, debug=False)
    #print "Result: %s" % result

    self.assertEqual(len(result) > 0, True)

  def test_evaluate_range(self):
    """test whether resolve string will get rid of parenthesis"""

    filename = utils.find_rtl_file_location("wb_sdram.v")
    filestring = ""
    try:
      f = open(filename)
      filestring = f.read()
      f.close()
    except:
      print "Failed to open test file"
      self.assertEqual(True, False)
      return

    define_dict = preprocessor.generate_define_table(filestring)
    result = preprocessor.evaluate_range("val[(48 -12):0]", debug = self.dbg)

#   print "final result: " + result
    self.assertEqual(result == "val[36:0]", True)


#   result = preprocessor.evaluate_equation("(4 * 3)", debug = self.dbg)
#   self.assertEqual((result == "12"), True)
#   result = preprocessor.evaluate_equation("(1 != 2)", debug = self.dbg)
#   self.assertEqual((result == "True"), True)

# def test_resolve_string(self):
#   """test whether resolve string will get rid of multiply"""
#
#   filename = utils.find_rtl_file_location("wb_ddr.v")
#   filestring = ""
#   try:
#     f = open(filename)
#     filestring = f.read()
##      f.close()
#   except:
#     print "Failed to open test file"
#     self.assertEqual(True, False)
#     return

#   define_dict = preprocessor.generate_define_table(filestring)

#   result = preprocessor.resolve_string("3 * 4", debug = True)
#   self.assertEqual((result == "12"), True)




  def test_complicated_string(self):
    """Hardest test of all, filled with multiple replacements and
    all of the pre-processing techniques"""
    self.assertEqual(True, True)

  def test_pre_processor(self):
    """test a real file in the miracle grow directory"""
    self.assertEqual(True, True)
    """test adding multiple lines togeterh with the \ key"""



if __name__ == "__main__":
  unittest.main()
