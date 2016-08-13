#!/usr/bin/python

import unittest
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.ibuilder import utils
from nysa.ibuilder import arbiter

GPIO_TAGS = json.load(open(os.path.join(os.path.dirname(__file__),
                           os.pardir,
                           "mock",
                           "gpio_module_tags.txt"), 'r'))
SF_CAMERA_TAGS = json.load( open(os.path.join(os.path.dirname(__file__),
                            os.pardir,
                            "mock",
                            "sf_camera_module_tags.txt"), 'r'))

class Test (unittest.TestCase):
    """Unit test for arbiter"""

    def setUp(self):
        base = os.path.join(os.path.dirname(__file__),
                            os.path.pardir,
                            os.path.pardir)
        self.nysa_base = os.path.abspath(base)
        self.dbg = False

    def test_get_number_of_arbiter_hosts_0(self):
        result = arbiter.get_number_of_arbiter_hosts(GPIO_TAGS, debug = self.dbg)
        self.assertEqual(len(result), 0)

    def test_get_number_of_arbiter_hosts_1(self):
        result = arbiter.get_number_of_arbiter_hosts(SF_CAMERA_TAGS, debug = self.dbg)
        self.assertEqual(len(result), 1)

    def test_is_arbiter_host(self):
        """test if the slave is an arbiter host"""
        #the first test should fail
        result = arbiter.is_arbiter_host(GPIO_TAGS, debug = self.dbg)
        self.assertEqual(result, False)

        #the second test should pass
        result = arbiter.is_arbiter_host(SF_CAMERA_TAGS, debug = self.dbg)
        self.assertEqual(result, True)

    def test_is_arbiter_not_requried(self):
        """test if the project_tags have been modified to show arbiter"""
        result = False
        tags = {}
        #get the example project data
        try:
            filename = os.path.join(  self.nysa_base,
                                      "test",
                                      "mock",
                                      "dionysus_default.json")

            filein = open(filename)
            filestr = filein.read()
            tags = json.loads(filestr)

        except IOError as err:
            print "File Error: " + str(err)
            self.assertEqual(False, True)

        result = arbiter.is_arbiter_required(tags, debug = self.dbg)
        self.assertEqual(result, False)

    def test_is_arbiter_requried(self):
        """test if the project_tags have been modified to show arbiter"""
        result = False
        tags = {}
        #get the example project data
        try:
            filename = os.path.join(  self.nysa_base,
                                      "test",
                                      "mock",
                                      "dionysus_sf_camera.json")

            filein = open(filename)
            filestr = filein.read()
            tags = json.loads(filestr)

        except IOError as err:
            print "File Error: " + str(err)
            self.assertEqual(False, True)

        result = arbiter.is_arbiter_required(tags, debug = self.dbg)
        self.assertEqual(result, True)

    def test_generate_arbiter_tags(self):
        """test if arbiter correctly determins if an arbiter is requried"""
        result = {}
        tags = {}
        #get the example project data
        try:
            filename = os.path.join(  self.nysa_base,
                                      "test",
                                      "mock",
                                      "dionysus_sf_camera.json")

            filein = open(filename)
            filestr = filein.read()
            tags = json.loads(filestr)

        except IOError as err:
            print "File Error: " + str(err)
            self.assertEqual(False, True)

        result = arbiter.generate_arbiter_tags(tags, debug = self.dbg)

        if (self.dbg):
            for aslave in result.keys():
                print "arbitrated slave: " + aslave

                for master in result[aslave]:
                    print "\tmaster: " + master + " bus: " + result[aslave][master]


        self.assertEqual((len(result.keys()) > 0), True)

    def test_generate_arbiter_buffer (self):
        """generate an arbiter buffer"""
        result = arbiter.generate_arbiter_buffer(2, debug = self.dbg)
        if (self.dbg): print "generated arbiter buffer: \n" + result
        self.assertEqual((len(result) > 0), True)

    def test_already_existing_arb_buf(self):
        arb_tags = {}
        arb_tags["slave"] = {}
        self.assertEqual(arbiter.already_existing_arb_bus(arb_tags, "bob"), False)
        self.assertEqual(arbiter.already_existing_arb_bus(arb_tags, "slave"), True)

if __name__ == "__main__":
  unittest.main()
