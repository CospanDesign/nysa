#! /usr/bin/python
import unittest
import os
import sys
import string

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "site_scons"))

import xilinx


class env_dict(dict):

    """Mock class to fool the initialize environment"""

    def AppendENVPath(self, path_name, path):
        if path_name not in self.keys():
            self[path_name] = ""
        self[path_name] = string.join([self[path_name], path], sep = ":")


class Test (unittest.TestCase):

    """Unit test for the xilinx functions"""

    def setUp(self):
        self.dbg = False

    def test_initialize_environment(self):
        env = env_dict()
        env["ENV"] = {}
        xilinx.initialize_environment(env)
        #print "Env: %s" % env["PATH"]


if __name__ == "__main__":
  unittest.main()
