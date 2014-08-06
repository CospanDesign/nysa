#!/usr/bin/python

import unittest
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.ibuilder.lib import utils
from nysa.ibuilder.lib import arbitor

GPIO_TAGS = json.load(open(os.path.join(os.path.dirname(__file__),
                           os.pardir,
                           "mock",
                           "gpio_module_tags.txt"), 'r'))
SF_CAMERA_TAGS = json.load( open(os.path.join(os.path.dirname(__file__),
                            os.pardir,
                            "mock",
                            "sf_camera_module_tags.txt"), 'r'))

class Test (unittest.TestCase):
    """Unit test for arbitor"""

    def setUp(self):
        base = os.path.join(os.path.dirname(__file__),
                            os.path.pardir,
                            os.path.pardir)
        self.nysa_base = os.path.abspath(base)
        self.dbg = False

    def test_get_number_of_arbitor_hosts_0(self):
        result = arbitor.get_number_of_arbitor_hosts(GPIO_TAGS, debug = self.dbg)
        self.assertEqual(len(result), 0)

    def test_get_number_of_arbitor_hosts_1(self):
        result = arbitor.get_number_of_arbitor_hosts(SF_CAMERA_TAGS, debug = self.dbg)
        self.assertEqual(len(result), 1)

    def test_is_arbitor_host(self):
        """test if the slave is an arbitor host"""
        #the first test should fail
        result = arbitor.is_arbitor_host(GPIO_TAGS, debug = self.dbg)
        self.assertEqual(result, False)

        #the second test should pass
        result = arbitor.is_arbitor_host(SF_CAMERA_TAGS, debug = self.dbg)
        self.assertEqual(result, True)

    def test_is_arbitor_not_requried(self):
        """test if the project_tags have been modified to show arbitor"""
        result = False
        tags = {}
        #get the example project data
        try:
            filename = os.path.join(  self.nysa_base,
                                      "nysa",
                                      "ibuilder",
                                      "example_projects",
                                      "dionysus_default.json")

            filein = open(filename)
            filestr = filein.read()
            tags = json.loads(filestr)

        except IOError as err:
            print "File Error: " + str(err)
            self.assertEqual(False, True)

        result = arbitor.is_arbitor_required(tags, debug = self.dbg)
        self.assertEqual(result, False)

    def test_is_arbitor_requried(self):
        """test if the project_tags have been modified to show arbitor"""
        result = False
        tags = {}
        #get the example project data
        try:
            filename = os.path.join(  self.nysa_base,
                                      "nysa",
                                      "ibuilder",
                                      "example_projects",
                                      "dionysus_sf_camera.json")

            filein = open(filename)
            filestr = filein.read()
            tags = json.loads(filestr)

        except IOError as err:
            print "File Error: " + str(err)
            self.assertEqual(False, True)

        result = arbitor.is_arbitor_required(tags, debug = self.dbg)
        self.assertEqual(result, True)


    def test_generate_arbitor_tags(self):
        """test if arbitor correctly determins if an arbitor is requried"""
        result = {}
        tags = {}
        #get the example project data
        try:
            filename = os.path.join(  self.nysa_base,
                                      "nysa",
                                      "ibuilder",
                                      "example_projects",
                                      "dionysus_sf_camera.json")

            filein = open(filename)
            filestr = filein.read()
            tags = json.loads(filestr)

        except IOError as err:
            print "File Error: " + str(err)
            self.assertEqual(False, True)

        result = arbitor.generate_arbitor_tags(tags, debug = self.dbg)

        if (self.dbg):
            for aslave in result.keys():
                print "arbitrated slave: " + aslave

                for master in result[aslave]:
                    print "\tmaster: " + master + " bus: " + result[aslave][master]


        self.assertEqual((len(result.keys()) > 0), True)


    def test_generate_arbitor_buffer (self):
        """generate an arbitor buffer"""
        result = arbitor.generate_arbitor_buffer(2, debug = self.dbg)
        if (self.dbg): print "generated arbitor buffer: \n" + result
        self.assertEqual((len(result) > 0), True)

if __name__ == "__main__":
  unittest.main()
