#! /usr/bin/python

import unittest
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.ibuilder.lib.ibuilder_error import ModuleFactoryError
from nysa.ibuilder.lib.module_processor import ModuleProcessor

TEST_CONFIG_FILENAME = os.path.abspath( os.path.join(os.path.dirname(__file__),
                                        os.path.pardir,
                                        "fake",
                                        "test_config_file.json"))

TEST_MEM_CONFIG_FILENAME = os.path.abspath( os.path.join(os.path.dirname(__file__),
                                        os.path.pardir,
                                        "fake",
                                        "test_mem_config_file.json"))



class Test (unittest.TestCase):
  """Unit test for sapfile"""

  def setUp(self):
    """open up a sapfile class"""
    base = os.path.join( os.path.dirname(__file__),
                         os.pardir,
                         os.pardir)
    self.nysa_base = os.path.abspath(base)
    self.out_dir = os.path.join(os.path.expanduser("~"), "sandbox")

    self.mp = ModuleProcessor()
    self.dbg = False
    if "SAPLIB_DEBUG" in os.environ:
      if (os.environ["SAPLIB_DEBUG"] == "True"):
        self.dbg = True

  def test_write_file(self):
    """a file will end up in a directory after this is tested"""
    self.mp.buf = "crappidy crap data!"
    self.mp.write_file(self.out_dir, filename="test")
    #no error was raised!

  def test_apply_tags(self):
    """a file should be changed based on the tags"""
    project_name = "projjjjeeeecccttt NAME!!!"
 
    #This should raise an error if something went wrong
    filename = os.path.join(self.nysa_base,
                            "nysa",
                            "ibuilder", 
                            "bus", 
                            "NYSA_README.txt")
    filein = open(filename)
    self.mp.buf = filein.read()
    filein.close()
 
    #print self.mp.buf
    tag_map = {"PROJECT_NAME":project_name}
    self.mp.set_tags(tag_map)
    self.mp.apply_tags()
    #print self.mp.buf
    result = (self.mp.buf.find(project_name) == 0)
    self.assertEqual(result, True)

  def test_set_tags(self):
    """test to see if a tag file was loaded correctly"""
    tag_file = os.path.join(  self.nysa_base,
                              "nysa",
                              "ibuilder",
                              "tags",
                              "README.json")
    self.mp.set_tags(tag_file)
    self.assertEqual(True, True)



  def test_process_file_no_dir(self):
    """make sure the process_file fales when user doesn't put in directory"""
    self.assertRaises(  ModuleFactoryError,
                        self.mp.process_file,
                        filename = "README")

  def test_process_file_no_location(self):
    """make sue the process file fails when user doesn't give a location"""
    
    filein = open(TEST_MEM_CONFIG_FILENAME)
    json_tags = json.load(filein)
    self.mp.set_tags(json_tags)
    file_tags = {"location":"bus"}
    self.assertRaises(  ModuleFactoryError,
                        self.mp.process_file,
                        filename = "README",
                        directory=self.out_dir)


  def test_process_file_no_filename(self):
    """excercise the gen script only functionality"""
    
    filein = open(TEST_MEM_CONFIG_FILENAME)
    json_tags = json.load(filein)
    self.mp.set_tags(json_tags)
    file_tags = {"gen_script":"gen_top"}
    self.mp.process_file( "top",
                          directory=self.out_dir,
                          file_dict = file_tags,
                          debug=self.dbg)
                          #debug=True)

    #if this doesn't throw an error then we're good



  def test_process_file(self):
    """excercise all functions of the class"""
    #print "testing process file"
    filein = open(TEST_MEM_CONFIG_FILENAME)
    json_tags = json.load(filein)
    filein.close()

    self.mp.set_tags(json_tags)
    file_tags = {"location":"${NYSA}/ibuilder/bus"}
    self.mp.process_file( filename = "NYSA_README.txt",
                          directory=self.out_dir,
                          file_dict = file_tags,
                          debug = self.dbg)
    #print self.mp.buf

    #the test is to not raise an error

  def test_resolve_dependencies(self):
    #filename = "sdram.v"
    #result = self.mp.resolve_dependencies(filename, debug = True)
    #"dependencies found for " + filename
    #self.assertEqual(result, True)
    #harder dependency
    filename = "wb_sdram.v"
    self.mp.resolve_dependencies(filename, debug = self.dbg)
    #print "\n\n\n\n"
    #print "dependency for " + filename
#    for d in self.mp.verilog_dependency_list:
#      print d
    #print "\n\n\n\n"
    self.assertNotEqual(len (self.mp.verilog_dependency_list), 0)

  def test_has_dependency(self):
    #scan a file that is not a verilog file
    result = self.mp.has_dependencies("wb_gpio", debug=self.dbg)
    self.assertEqual(result, False)
    #scan for a file that is a verilog file with a full path
    file_location = os.path.join( self.nysa_base,
                                  "nysa",
                                  "cbuilder",
                                  "verilog",
                                  "wishbone",
                                  "host_interface",
                                  "uart",
                                  "uart_io_handler.v")

    #result = self.mp.has_dependencies(file_location, debug=self.dbg)
    result = self.mp.has_dependencies(file_location, debug=self.dbg)
    self.assertEqual(result, True)
    #scan a file that is a verilog file but not the full path
    result = self.mp.has_dependencies("uart_io_handler.v", debug=self.dbg)
    self.assertEqual(result, True)

    #scan a file that has multiple levels of dependencies
    result = self.mp.has_dependencies("sdram.v", debug=self.dbg)
    self.assertEqual(result, True)

    result = self.mp.has_dependencies("wb_gpio.v", debug=self.dbg)
    self.assertEqual(result, False)



  def test_process_bram_file(self):
    """excercise all functions of the class"""
    #print "testing process file"
    #tag_file = os.path.join(  self.nysa_base,
    #                          "nysa",
    #                          "ibuilder",
    #                          "example_projects",
    #                          "mem_example.json")

    filein = open(TEST_MEM_CONFIG_FILENAME)
    json_tags = json.load(filein)
    filein.close()

    self.mp.set_tags(json_tags)
    file_tags = {"location":"bus"}
    self.mp.process_file( filename = "wb_bram.v",
                          directory=self.out_dir,
                          file_dict = file_tags,
                          debug = self.dbg)
    #print self.mp.buf

    #if this doesn't throw an error then we're good

  def test_process_gen_script(self):
    """excercise the script"""
    filein = open(TEST_CONFIG_FILENAME)
    json_tags = json.load(filein)
    self.mp.set_tags(json_tags)
    file_tags = { "location":"hdl/rtl/wishbone/interconnect",
                  "gen_script":"gen_interconnect"}
    self.mp.process_file( filename = "wishbone_interconnect.v",
                          directory=self.out_dir,
                          file_dict = file_tags,
                          debug = False)
    #print self.mp.buf

    #if this doesn't throw an error then we're good



  def test_get_list_of_dependencies(self):
    deps = self.mp.get_list_of_dependencies("wb_gpio.v", debug=self.dbg)
    self.assertEqual(len(deps) == 0, True)
    deps = self.mp.get_list_of_dependencies("uart_io_handler.v", debug=self.dbg)
    self.assertEqual(len(deps) > 0, True)
    deps = self.mp.get_list_of_dependencies("sdram.v", debug=self.dbg)
    self.assertEqual(len(deps) > 0, True)


if __name__ == "__main__":
  unittest.main()
