#! /usr/bin/python

import unittest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.ibuilder import ibuilder

TEST_CONFIG_FILENAME = os.path.abspath( os.path.join(os.path.dirname(__file__),
                                        os.path.pardir,
                                        "fake",
                                        "test_config_file.json"))

class Test (unittest.TestCase):
    """Unit test for ibuilder"""

    def setUp(self):
        self.out_dir = os.path.join(os.path.expanduser("~"), "sandbox", "temp")

    def test_get_project_tags(self):
        test = ibuilder.get_project_tags(TEST_CONFIG_FILENAME)
        self.assertEqual(test["PROJECT_NAME"], "example_project")

    def test_get_output_dir(self):
        test = ibuilder.get_output_dir(TEST_CONFIG_FILENAME)
        output = os.path.join(os.path.expanduser("~"), "projects", "ibuilder_project")
        self.assertEqual(test, output)

    def test_generate_project(self):
        result = ibuilder.generate_project(TEST_CONFIG_FILENAME)
        self.assertEqual(result, True)

