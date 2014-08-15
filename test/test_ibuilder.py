#! /usr/bin/python

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, "ibuilder", "lib"))

import project_generator as pg
import arbitor
import utils


class Test (unittest.TestCase):
  """Unit test for pg"""

  def setUp(self):
    base = os.path.join( os.path.dirname(__file__),
                         os.pardir)
    self.nysa_base = os.path.abspath(base)
    self.dbg = False
    self.project = pg.ProjectGenerator() 

  def test_read_config_file(self):
    """confirm that a project config file can be read"""
    filename = os.path.join(  self.nysa_base,
                              "ibuilder",
                              "example_projects",
                              "dionysus_gpio_mem.json")
    self.project.read_config_file(filename, debug=self.dbg)
    #This should launch an error if there is a problem

  def test_read_template(self):
    """confirm that a template file can be loaded"""
    filename = "wishbone_template"

    #if there is an error while processing an error will be raised
    self.project.read_template_file(filename, debug=self.dbg)

#  def test_generate_project(self):
#    """test if a project can be generated with version 2"""
#    filename = os.path.join(  self.nysa_base,
#                              "ibuilder",
#                              "example_projects",
#                              "dionysus_gpio_mem.json")
#
#    result = self.project.generate_project(filename, debug=self.dbg)
#    self.assertEqual(result, True)
#
#  def test_generate_spi_project(self):
#    """test if a project can be generated with version 2"""
#    filename = os.path.join(  self.nysa_base,
#                              "ibuilder",
#                              "example_projects",
#                              "dionysus_gpio_mem.json")
#
#    save_debug = self.dbg
#    #self.dbg = True
#    result = self.project.generate_project(filename, debug=self.dbg)
#    self.dbg = save_debug
#    self.assertEqual(result, True)
#
#  def test_generate_ddr_project(self):
#    """test if the ddr project can be generated with version 2"""
#    filename = os.path.join(  self.nysa_base,
#                              "ibuilder",
#                              "example_projects",
#                              "dionysus_gpio_mem.json")
#
#    result = self.project.generate_project(filename, debug=self.dbg)
#    self.assertEqual(result, True)
#
#  def test_generate_mem_project(self):
#    """test if the new memory feature borks anything else"""
#    filename = os.path.join(  self.nysa_base,
#                              "ibuilder",
#                              "example_projects",
#                              "mem_example.json")
#
#    result = self.project.generate_project(filename, debug=self.dbg)
#    self.assertEqual(result, True)
#
#  def test_generate_arbitors_none(self):
#    """confirm that no arbitors are generated with this project tag"""
#    filename = os.path.join(  self.nysa_base,
#                              "ibuilder",
#                              "example_projects",
#                              "dionysus_gpio_mem.json")
#
#    result = self.project.generate_project(filename, debug=self.dbg)
#    self.assertEqual(result, True)
#    num_arbs = self.project.generate_arbitors(debug = self.dbg)
#    self.assertEqual(num_arbs, 0)
#
#  def test_generate_arbitors_simple(self):
#    """the project file is supposed to generate one file"""
#    #read in the configuration file
#    config_filename = os.path.join(   self.nysa_base,
#                                      "ibuilder",
#                                      "example_projects",
#                                      "arb_example.json")
#
#
#    try:
#      self.project.read_config_file(config_filename, debug=self.dbg)
#    except TypeError as err:
#      print "Error reading JSON Config File: %s" % str(err)
#      self.assertEqual(True, False)
#
#    #read in the template
#    #if there is an error an assertion will be raised
#    self.project.read_template_file(self.project.project_tags["TEMPLATE"])
#
#    self.project.filegen.set_tags(self.project.project_tags)
#    #get the clock rate from the constraint file
#    board_dict = utils.get_board_config("dionysus")
#    cfiles = board_dict["default_constraint_files"]
#    self.project.project_tags["CLOCK_RATE"] = utils.read_clock_rate(cfiles[0])
#    #generate the project directories and files
#    self.project.project_tags["BASE_DIR"] = os.path.join(os.path.expanduser("~"), "sandbox", "test_nysa")
#    utils.create_dir(self.project.project_tags["BASE_DIR"])
#
#    #print "Parent dir: " + self.project.project_tags["BASE_DIR"]
#    for key in self.project.template_tags["PROJECT_TEMPLATE"]["files"]:
#      self.project.recursive_structure_generator(
#              self.project.template_tags["PROJECT_TEMPLATE"]["files"],
#              key,
#              self.project.project_tags["BASE_DIR"])
#
#    arb_tags = arbitor.generate_arbitor_tags(self.project.project_tags)
#    self.project.project_tags["ARBITORS"] = arb_tags
#
#    result = self.project.generate_arbitors(debug = self.dbg)
#    self.assertEqual(result, 1)
#
#  def test_generate_arbitors_difficult(self):
#    """the project calls for three arbitors, but two are identical"""
#
#    #read in the configuration file
#    config_filename = os.path.join(   self.nysa_base,
#                                      "ibuilder",
#                                      "example_projects",
#                                      "arb_difficult_example.json")
#
#    result = False
#    self.project.read_config_file(config_filename, debug=self.dbg)
#    #this will throw an exception if something failed
#    self.project.read_template_file(self.project.project_tags["TEMPLATE"])
#
#    board_dict = utils.get_board_config(self.project.project_tags["board"])
#    print "board_dict: %s" % str(board_dict)
#    cfiles = board_dict["default_constraint_files"]
#    self.project.filegen.set_tags(self.project.project_tags)
#    #get the clock rate from the constraint file
#    self.project.project_tags["CLOCK_RATE"] = utils.read_clock_rate(cfiles[0])
#    #generate the project directories and files
#    self.project.project_tags["BASE_DIR"] = os.path.join(os.path.expanduser("~"), "sandbox", "test_nysa")
#    utils.create_dir(self.project.project_tags["BASE_DIR"])
#
#    #print "Parent dir: " + self.project.project_tags["BASE_DIR"]
#    for key in self.project.template_tags["PROJECT_TEMPLATE"]["files"]:
#      self.project.recursive_structure_generator(
#              self.project.template_tags["PROJECT_TEMPLATE"]["files"],
#              key,
#              self.project.project_tags["BASE_DIR"])
#
#    arb_tags = arbitor.generate_arbitor_tags(self.project.project_tags)
#    self.project.project_tags["ARBITORS"] = arb_tags
#
#    result = self.project.generate_arbitors(debug = self.dbg)
#    self.assertEqual(result, 2)

if __name__ == "__main__":
  unittest.main()

