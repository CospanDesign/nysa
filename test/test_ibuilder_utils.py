#! /usr/bin/python
import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from ibuilder.lib import utils

class Test (unittest.TestCase):
  """Unit test for utils"""

  def setUp(self):
    self.dbg = False

    '''
  def test_arbitor_count(self):
    """gets the module tags and detects if there is any arbitor hosts"""
    filename = utils.find_rtl_file_location("wb_gpio.v")
    tags = utils.get_module_tags(filename, debug=self.dbg)
    self.assertEqual(len(tags["arbitor_masters"]), 0)

    filename = utils.find_rtl_file_location("wb_console.v")
    tags = utils.get_module_tags(filename, debug=self.dbg)
    self.assertEqual(len(tags["arbitor_masters"]), 2)
    '''

  def test_create_dir(self):
    """create a directory"""
    result = utils.create_dir("~/sandbox/temp")
    self.assertEqual(result, True)

  def test_remove_comments(self):
    """try and remove all comments from a buffer"""
    bufin = "not comment/*comment\n*/\n//comment\n/*\nabc\n*/something//comment"
    output_buffer = utils.remove_comments(bufin)
    good = "not comment\n\nsomething\n"
    self.assertEqual(output_buffer, good)

  def test_get_constraint_filenames(self):
    cfiles = utils.get_constraint_filenames("dionysus")
    self.assertIn("dionysus.ucf", cfiles)

  def test_get_board_config(self):
    """
    gets the board configuration dictionary given the board
    name
    """
    boardname = "dionysus"
    board_dict = utils.get_board_config(boardname)
    self.assertEqual(board_dict["board_name"], "Dionysus")

  def test_get_board_names(self):
    """
    gets all the board names
    """
    boards = utils.get_board_names()
    self.assertIn("dionysus", boards)


  def test_find_rtl_file_location(self):
    """give a filename that should be in the RTL"""
    result = utils.find_rtl_file_location("wb_gpio.v", debug=False)
    #print "file location: " + result
    try:
      testfile = open(result)
      result = True
      testfile.close()
    except:
      result = False

    self.assertEqual(result, True)

  def test_find_rtl_file_location_user_cbuilder(self):
    """give a filename that should be in the RTL"""
    utils.create_dir("~/sandbox/temp")
    try:
      fname = os.path.expanduser("~/sandbox/temp/temp.v")
      f = open(fname, 'w')
      f.write("module m ()\n\nendmodule")
      f.close()
    except IOError, err:
      print "Failed to write file" + str(err)
      return

    result = utils.find_rtl_file_location(  "temp.v", 
                                            [os.path.expanduser("~/sandbox")],  
                                            debug=False)
    #print "file location: " + result
    try:
      testfile = open(result)
      result = True
      testfile.close()
    except:
      result = False

    self.assertEqual(result, True)



  def test_resolve_path(self):
    """given a filename with or without the ~ return a filename with the ~ expanded"""
    
    filename1 = "/filename1"
    filename = utils.resolve_path(filename1)
    #print "first test: " + filename
    #if (filename == filename1):
  #   print "test1: they are equal!"
    self.assertEqual(filename, "/filename1")

    filename2 = "~/filename2"
    filename = utils.resolve_path(filename2)
    correct_result = os.path.expanduser("~") + "/filename2"
    #print "second test: " + filename + " should equal to: " + correct_result
    #if (correct_result == filename):
  #   print "test2: they are equal!"
    self.assertEqual(correct_result, filename)
    filename = filename.strip()

  def test_read_slave_tags(self):
    """try and extrapolate all info from the slave file"""
    
    filename = utils.find_rtl_file_location("wb_gpio.v")
    drt_keywords = [
      "DRT_ID",
      "DRT_FLAGS",
      "DRT_SIZE"
    ]
    tags = utils.get_module_tags(filename, keywords = drt_keywords, debug=self.dbg)

    io_types = [
      "input",
      "output",
      "inout"
    ]
    #
    #for io in io_types:
    # for port in tags["ports"][io].keys():
    #   print "Ports: " + port

    self.assertEqual(True, True)

    '''
  def test_read_slave_tags_with_params(self):
    """some verilog files have a paramter list"""
    
    base_dir = os.getenv("SAPLIB_BASE")
    filename = base_dir + "/hdl/rtl/wishbone/slave/ddr/wb_ddr.v"
    drt_keywords = [
      "DRT_ID",
      "DRT_FLAGS",
      "DRT_SIZE"
    ]
    tags = utils.get_module_tags(filename, keywords = drt_keywords, debug=self.dbg)

    io_types = [
      "input",
      "output",
      "inout"
    ]
    #
    #for io in io_types:
    # for port in tags["ports"][io].keys():
    #   print "Ports: " + port

    if self.dbg:
      print "\n\n\n\n\n\n"
      print "module name: " + tags["module"]
      print "\n\n\n\n\n\n"

    self.assertEqual(tags["module"], "wb_ddr")
    '''

    '''
  def test_read_slave_tags_with_params_lax(self):
    """test the LAX for the parameters"""
    #self.dbg = True
    
    base_dir = os.getenv("SAPLIB_BASE")
    filename = base_dir + "/hdl/rtl/wishbone/slave/wb_logic_analyzer/wb_logic_analyzer.v"
    drt_keywords = [
      "DRT_ID",
      "DRT_FLAGS",
      "DRT_SIZE"
    ]
    tags = utils.get_module_tags(filename, keywords = drt_keywords, debug=self.dbg)

    io_types = [
      "input",
      "output",
      "inout"
    ]
    #
    #for io in io_types:
    # for port in tags["ports"][io].keys():
    #   print "Ports: " + port

    if self.dbg:
      print "\n\n\n\n\n\n"
      print "module name: " + tags["module"]
      print "\n\n\n\n\n\n"

    #self.dbg = False
    self.assertEqual(tags["module"], "wb_logic_analyzer")

  def test_read_user_parameters(self):
    filename = utils.find_rtl_file_location("wb_gpio.v")
    tags = utils.get_module_tags(filename, debug=self.dbg)

    keys = tags["parameters"].keys()
    if self.dbg:
      print "reading the parameters specified by the user"
    self.assertIn("DEFAULT_INTERRUPT_MASK", keys)
    if self.dbg:
      print "make sure other parameters don't get read"
    self.assertNotIn("ADDR_GPIO", keys)

    '''

    '''
  def test_read_hard_slave_tags(self):
    """try and extrapolate all info from the slave file"""
    
    base_dir = os.getenv("SAPLIB_BASE") 
    filename = base_dir + "/hdl/rtl/wishbone/slave/ddr/wb_ddr.v"
    base_dir = get_nysa_base()
    drt_keywords = [
      "DRT_ID",
      "DRT_FLAGS",
      "DRT_SIZE"
    ]
    tags = utils.get_module_tags(filename, keywords = drt_keywords, debug=self.dbg)

    io_types = [
      "input",
      "output",
      "inout"
    ]
    #
    #for io in io_types:
    # for port in tags["ports"][io].keys():
    #   print "Ports: " + port

    self.assertEqual(True, True)
    '''

  def test_get_net_names(self):
    filename = "lx9.ucf" 
    netnames = utils.get_net_names(filename, debug = self.dbg)
    if self.dbg:
      print "net names: "
      for name in netnames:
        print "\t%s" % name

    self.assertIn("clk", netnames) 

  def test_read_clk_with_period(self):
    filename = "dionysus.ucf" 
    clock_rate = utils.read_clock_rate(filename, debug = self.dbg)
    self.assertEqual(int(clock_rate), 100000000)

  def test_read_clk_with_timespec(self):
    filename = "lx9.ucf" 
    clock_rate = utils.read_clock_rate(filename, debug = self.dbg)
    self.assertEqual(int(clock_rate), 100000000)


  def test_is_module_in_file(self):
    module_name = "uart"
    filename = "wb_gpio.v"
    result = utils.is_module_in_file(filename, module_name, debug = self.dbg)
    self.assertEqual(result, False)
    
    module_name = "wb_gpio"
    filename = "wb_gpio.v"
    result = utils.is_module_in_file(filename, module_name, debug = self.dbg)
    self.assertEqual(result, True)

  def test_get_slave_list(self):
    slave_list = utils.get_slave_list(debug = self.dbg)

  def test_find_module_filename(self):
    module_name = "uart"
    result = utils.find_module_filename(module_name, debug = self.dbg)
    self.assertEqual(len(result) > 0, True)
 


if __name__ == "__main__":
  unittest.main()

