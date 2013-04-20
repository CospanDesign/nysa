#! /usr/bin/python

import os
import sys
import wx
import string
import unittest

sys.path.append(os.path.join( os.path.dirname(__file__), 
                              os.pardir, 
                              "cbuilder", 
                              "scripts"))

from wishbone_peripheral_cbuilder import WishbonePeripheralCBuilder
from wishbone_memory_cbuilder import WishboneMemoryCBuilder
from axi_peripheral_cbuilder import AxiPeripheralCBuilder
from axi_memory_cbuilder import AxiMemoryCBuilder


dbg = False

PROJECT_DIR = os.path.join( os.path.expanduser("~"), 
                            "Projects", 
                            "cbuilder_projects")

wbp_dict = {}
wbp_dict["base"] = PROJECT_DIR
wbp_dict["name"] = "wbp_test"
wbp_dict["type"] = "wishbone"
wbp_dict["subtype"] = "peripheral"
wbp_dict["master_count"] = 0
wbp_dict["drt_id"] = 0
wbp_dict["drt_flags"] = 1
wbp_dict["drt_size"] = 3

wbm_dict = {}
wbm_dict["base"] = PROJECT_DIR
wbm_dict["name"] = "wbm_test"
wbm_dict["type"] = "wishbone"
wbm_dict["subtype"] = "memory"
wbm_dict["master_count"] = 0
wbm_dict["drt_id"] = 0
wbm_dict["drt_flags"] = 1
wbm_dict["drt_size"] = 3

abp_dict = {}
abp_dict["base"] = PROJECT_DIR
abp_dict["name"] = "abp_test"
abp_dict["type"] = "axi"
abp_dict["subtype"] = "peripheral"
abp_dict["axi_type"] = "normal"
abp_dict["drt_id"] = 0
abp_dict["drt_flags"] = 1
abp_dict["drt_size"] = 3

abm_dict = {}
abm_dict["base"] = PROJECT_DIR
abm_dict["name"] = "abm_test"
abm_dict["type"] = "axi"
abm_dict["subtype"] = "memory"
abm_dict["axi_type"] = "normal"
abm_dict["drt_id"] = 0
abm_dict["drt_flags"] = 1
abm_dict["drt_size"] = 3


class PluginManagerTest (unittest.TestCase):

  def setUp(self):
    self.WPCB = WishbonePeripheralCBuilder(wbp_dict)
    self.WMCB = WishboneMemoryCBuilder(wbm_dict)
    self.APCB = AxiPeripheralCBuilder(abp_dict)
    self.AMCB = AxiMemoryCBuilder(abm_dict)

  def test_hello (self):
    self.assertEqual(0, 0)

  def test_generate_cbuilder_project(self):
    #Create a valid dictionary
    cpd = {}

  def test_get_template_dir(self):
    TB = os.path.join(os.path.join( os.path.dirname(__file__),
                                    os.pardir,
                                    "cbuilder",
                                    "template"))
    WPCB_TB = os.path.join(os.path.join(TB, "wishbone", "slave", "peripheral"))
    tb = self.WPCB.get_template_dir()
    #print "WPCB template base: %s" % tb
    self.assertEqual(os.path.abspath(WPCB_TB), tb)
    WMCB_TB = os.path.join(os.path.join(TB, "wishbone", "slave", "memory"))
    tb = self.WMCB.get_template_dir()
    #print "WMCB template base: %s" % tb
    self.assertEqual(os.path.abspath(WMCB_TB), tb)
    APCB_TB = os.path.join(os.path.join(TB, "axi", "slave", "peripheral"))
    tb = self.APCB.get_template_dir()
    #print "APCB template base: %s" % tb
    self.assertEqual(os.path.abspath(APCB_TB), tb)
    AMCB_TB = os.path.join(os.path.join(TB, "axi", "slave", "memory"))
    tb = self.AMCB.get_template_dir()
    #print "AMCB template base: %s" % tb
    self.assertEqual(os.path.abspath(AMCB_TB), tb)

  def test_project_dir(self):
    #Test WPCB get project dir
    pd = self.WPCB.get_project_dir()
    project_dir = os.path.join( wbp_dict["base"],
                                wbp_dict["type"],
                                wbp_dict["subtype"],
                                wbp_dict["name"])

    self.assertEqual(pd, project_dir)
    #Test WMCB get project dir
    pd = self.WMCB.get_project_dir()
    project_dir = os.path.join( wbm_dict["base"],
                                wbm_dict["type"],
                                wbm_dict["subtype"],
                                wbm_dict["name"])

    self.assertEqual(pd, project_dir)
    #Test APCB get project dir
    pd = self.APCB.get_project_dir()
    project_dir = os.path.join( abp_dict["base"],
                                abp_dict["type"],
                                abp_dict["subtype"],
                                abp_dict["name"])

    self.assertEqual(pd, project_dir)
    #Test AMCB get project dir
    pd = self.AMCB.get_project_dir()
    project_dir = os.path.join( abm_dict["base"],
                                abm_dict["type"],
                                abm_dict["subtype"],
                                abm_dict["name"])
    self.assertEqual(pd, project_dir)

  def test_create_project_dir(self):
    print "Create projects"
    self.WPCB.create_project_dir()
    self.assertTrue(os.path.exists(self.WPCB.get_project_dir()))
    self.WPCB.remove_project()
    self.assertFalse(os.path.exists(self.WPCB.get_project_dir()))
    
    self.WMCB.create_project_dir()
    self.assertTrue(os.path.exists(self.WMCB.get_project_dir()))
    self.WMCB.remove_project()
    self.assertFalse(os.path.exists(self.WMCB.get_project_dir()))
 
    self.APCB.create_project_dir()
    self.assertTrue(os.path.exists(self.APCB.get_project_dir()))
    self.APCB.remove_project()
    self.assertFalse(os.path.exists(self.APCB.get_project_dir()))
 
    self.AMCB.create_project_dir()
    self.assertTrue(os.path.exists(self.AMCB.get_project_dir()))
    self.AMCB.remove_project()
    self.assertFalse(os.path.exists(self.AMCB.get_project_dir()))

  def test_process_slave_template(self):
    #create a directory
    self.WPCB.create_project_dir()
    self.WPCB.process_slave_template()

    #Verify Results
    data = ""
    #open the new slave file
    fpath = os.path.join(self.WPCB.get_project_dir(), wbp_dict["name"])
    self.assertTrue(os.path.exists(fpath))
    f = open(fpath)
    data = f.read() 

    self.assertIn(wbp_dict["name"], data)
    #get the DRT lines
    for a in data.split('\n'):
      if "DRT_ID" in a:
        value = a.partition("DRT_ID")[2]
        if ":" in value:
          value = value.strip(":")
        value = value.strip()
        value = int(value)
        self.assertEqual(value, wbp_dict["drt_id"])
        break

    for a in data.split('\n'):
      if "DRT_SIZE" in a:
        value = a.partition("DRT_SIZE")[2]
        if ":" in value:
          value = value.strip(":")
        value = value.strip()
        value = int(value)
        self.assertEqual(value, wbp_dict["drt_size"])
        break

    for a in data.split('\n'):
      if "DRT_FLAGS" in a:
        value = a.partition("DRT_FLAGS")[2]
        if ":" in value:
          value = value.strip(":")
        value = value.strip()
        value = int(value)
        self.assertEqual(value, wbp_dict["drt_flags"])
        break

    self.WPCB.remove_project()

    self.WMCB.create_project_dir()
    self.WMCB.process_slave_template()

    #Verify Results
    data = ""
    #open the new slave file
    fpath = os.path.join(self.WMCB.get_project_dir(), wbm_dict["name"])
    self.assertTrue(os.path.exists(fpath))
    f = open(fpath)
    data = f.read() 

    self.assertIn(wbm_dict["name"], data)
    #get the DRT lines
    for a in data.split('\n'):
      if "DRT_ID" in a:
        value = a.partition("DRT_ID")[2]
        if ":" in value:
          value = value.strip(":")
        value = value.strip()
        value = int(value)
        self.assertEqual(value, wbm_dict["drt_id"])
        break

    for a in data.split('\n'):
      if "DRT_SIZE" in a:
        value = a.partition("DRT_SIZE")[2]
        if ":" in value:
          value = value.strip(":")
        value = value.strip()
        value = int(value)
        self.assertEqual(value, wbm_dict["drt_size"])
        break

    for a in data.split('\n'):
      if "DRT_FLAGS" in a:
        value = a.partition("DRT_FLAGS")[2]
        if ":" in value:
          value = value.strip(":")
        value = value.strip()
        value = int(value)
        self.assertEqual(value, wbm_dict["drt_flags"])
        break
    #Clean up
    self.WMCB.remove_project()

    self.APCB.create_project_dir()
    self.APCB.process_slave_template()

    #Verify Results
    data = ""
    #open the new slave file
    fpath = os.path.join(self.APCB.get_project_dir(), abp_dict["name"])
    self.assertTrue(os.path.exists(fpath))
    f = open(fpath)
    data = f.read() 

    self.assertIn(abp_dict["name"], data)
    #dbg = True
    #get the DRT lines
    for a in data.split('\n'):
      if "DRT_ID" in a:
        if dbg: print "DRT_ID string: %s" % a
        value = a.partition("DRT_ID")[2]
        if ":" in value:
          value = value.strip(":")
        value = value.strip()
        value = int(value)
        self.assertEqual(value, abp_dict["drt_id"])
        break

    for a in data.split('\n'):
      if "DRT_SIZE" in a:
        if dbg: print "DRT_SIZE string: %s" % a
        value = a.partition("DRT_SIZE")[2]
        if ":" in value:
          value = value.strip(":")
        value = value.strip()
        value = int(value)
        self.assertEqual(value, abp_dict["drt_size"])
        break

    for a in data.split('\n'):
      if "DRT_FLAGS" in a:
        if dbg: print "DRT_FLAGS string: %s" % a
        value = a.partition("DRT_FLAGS")[2]
        if ":" in value:
          value = value.strip(":")
        value = value.strip()
        value = int(value)
        self.assertEqual(value, abp_dict["drt_flags"])
        break

    #dbg = False

    self.APCB.remove_project()

    self.AMCB.create_project_dir()
    self.AMCB.process_slave_template()

    #Verify Results
    data = ""
    #open the new slave file
    fpath = os.path.join(self.AMCB.get_project_dir(), abm_dict["name"])
    self.assertTrue(os.path.exists(fpath))
    f = open(fpath)
    data = f.read() 

    self.assertIn(abm_dict["name"], data)
    #get the DRT lines
    for a in data.split('\n'):
      if "DRT_ID" in a:
        value = a.partition("DRT_ID")[2]
        if ":" in value:
          value = value.strip(":")
        value = value.strip()
        value = int(value)
        self.assertEqual(value, abm_dict["drt_id"])
        break

    for a in data.split('\n'):
      if "DRT_SIZE" in a:
        value = a.partition("DRT_SIZE")[2]
        if ":" in value:
          value = value.strip(":")
        value = value.strip()
        value = int(value)
        self.assertEqual(value, abm_dict["drt_size"])
        break

    for a in data.split('\n'):
      if "DRT_FLAGS" in a:
        value = a.partition("DRT_FLAGS")[2]
        if ":" in value:
          value = value.strip(":")
        value = value.strip()
        value = int(value)
        self.assertEqual(value, abm_dict["drt_flags"])
        break


    self.AMCB.remove_project()
 
  def test_copy_slave_files(self):
    self.WPCB.create_project_dir()
    self.WPCB.process_slave_template()
    self.WPCB.copy_slave_files()
    self.WPCB.remove_project()
    
    self.WMCB.create_project_dir()
    self.WMCB.process_slave_template()
    self.WMCB.copy_slave_files()
    self.WMCB.remove_project()
 
    self.APCB.create_project_dir()
    self.APCB.process_slave_template()
    self.APCB.copy_slave_files()
    self.APCB.remove_project()
 
    self.AMCB.create_project_dir()
    self.AMCB.process_slave_template()
    self.AMCB.copy_slave_files()
    self.AMCB.remove_project()






if __name__ == '__main__':
  unittest.main()
