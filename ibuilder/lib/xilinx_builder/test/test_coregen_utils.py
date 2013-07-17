#! /usr/bin/python
import unittest
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "site_scons"))

import utils
import coregen_utils

class Test (unittest.TestCase):
    """Unit test for the verilog pre-processor module"""

    def setUp(self):
        self.dbg = False
        self.env = {}
        self.env["CONFIG_FILE"] = "config.json"
        self.config = utils.read_config(self.env)

    def test_create_coregen_dir(self):
        config = self.config
        corgen_dir = coregen_utils.create_coregen_dir(config)

    def test_create_temp_coregen_dir(self):
        config = self.config
        corgen_dir = coregen_utils.create_coregen_dir(config)

    def test_new_coregen_file_list (self):
        config = self.config
        filelist = coregen_utils.get_new_coregen_file_list(config)

    def test_customize_all_cores(self): 
        config = self.config
        filelist = coregen_utils.get_new_coregen_file_list(config)
        filelist = coregen_utils.customize_all_cores(config, filelist)

    def test_create_project_file(self):
        config = self.config
        coregen_utils.create_project_file(config)

    def test_get_target_files(self):
        config = self.config
        files = coregen_utils.get_target_files(config)
        print "files: %s" % str(files)


if __name__ == "__main__":
  unittest.main()

