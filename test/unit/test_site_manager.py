#!/usr/bin/python

import unittest
import json
import sys
import os
import site
import shutil
import urllib2

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.common import site_manager

test_rv = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, "fake"))
#REMOTE_URL = "http:://127.0.0.1/" + test_rv
REMOTE_URL = "http://www.cospandesign.com/nysa/packages"

TEST_NAME = "nysa"


class Test (unittest.TestCase):
    """Unit test for arbiter"""

    def setUp(self):
        self.sm = site_manager.SiteManager()
        #print "user base: %s" % site_manager.get_site_path()
        #print "board id: %s" % str(self.sm.get_board_id_dict())
 
    def test_get_local_verilog_package_names(self):
        pn = self.sm.get_local_verilog_package_names()
        #print "pn: %s" % str(pn)

    def test_get_local_verilog_package_path(self):
        path = self.sm.get_local_verilog_package_path("nysa-verilog")
        #print "path: %s" % path
        assert os.path.exists(path)
        
    def test_verilog_package_exists(self):
        assert self.sm.verilog_package_exists("nysa-verilog")

    def test_get_verilog_package_names(self):
        #print "package names: %s" % str(self.sm.get_local_verilog_package_names())
        assert len(self.sm.get_local_verilog_package_names()) > 0

    def get_local_verilog_package_names(self):
        assert len(self.sm.get_verilog_paths()) > 0
#    def test_update_verilog_package(self):
#        self.sm.update_verilog_package()

if __name__ == "__main__":
  unittest.main()


