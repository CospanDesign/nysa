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
    """Unit test for arbitor"""

    def setUp(self):
        self.sm = site_manager.SiteManager()
        if not self.sm._site_dir_exists():
            self.sm._create_site_dir()
        if not os.path.exists(self.sm.local_version_path):
            #Doesn't exists, create a reference to it
            f = open(self.sm.local_version_path, "w")
            f.write("{}")
            f.close()
 
        
    def tearDown(self):
        self.sm._remove_local_site_dir()

    """
    def test_set_remote_url(self):
        self.sm.set_remote_url(REMOTE_URL)
        assert REMOTE_URL == self.sm.remote_url
        rv = os.path.join(REMOTE_URL, "versions.json")
        assert rv == self.sm.remote_version_path

    def test_get_remote_version_dict(self):
        self.sm.set_remote_url(REMOTE_URL)
        #self.sm.set_remote_url("http://www.cospandesign.com/nysa/packages")
        assert len(self.sm.get_remote_version_dict()) > 0
    """

    def test_get_local_version_dict(self):
        d = self.sm.get_local_version_dict()
        d["nyes-verilog"] = ""
        f = open(self.sm.local_version_path, "w")
        f.write(json.dumps(d))
        f.close()
        assert len(self.sm.get_local_version_dict()) > 0

    """
    def test_compare_version_entry(self):
        try:
            self.sm.compare_version_entry("test")
            assert False
        except site_manager.RemoteDefinition:
            pass
        
        try:
            self.sm.compare_version_entry("nysa-verilog")
            assert False
        except site_manager.LocalDefinition:
            pass
            
        f = open(os.path.join(site.getuserbase(), TEST_NAME, "versions.json"), "r")
        lv = json.load(f)
        f.close()

        lv["nysa-verilog"] = ""

        f = open(os.path.join(site.getuserbase(), TEST_NAME, "versions.json"), "w")
        f.write(json.dumps(lv))
        f.close()
        
            
        assert not self.sm.compare_version_entry("nysa-verilog")
        rv = json.loads(urllib2.urlopen("http://www.cospandesign.com/nysa/packages/versions.json").read())
        lv["nysa-verilog"] = rv["nysa-verilog"]

        f = open(os.path.join(site.getuserbase(), TEST_NAME, "versions.json"), "w")
        f.write(json.dumps(lv))
        f.close()
 
        assert self.sm.compare_version_entry("nysa-verilog")

    """

    '''
    def test_update_local_version(self):
        f = open(os.path.join(site.getuserbase(), TEST_NAME, "versions.json"), "r")
        lv = json.load(f)
        f.close()

        rv = json.loads(urllib2.urlopen("http://www.cospandesign.com/nysa/packages/versions.json").read())
        lv["nysa-verilog"] = ""


        f = open(os.path.join(site.getuserbase(), TEST_NAME, "versions.json"), "w")
        f.write(json.dumps(lv))
        f.close()


        self.sm.update_local_version("nysa-verilog")

        f = open(os.path.join(site.getuserbase(), TEST_NAME, "versions.json"), "r")
        lv = json.load(f)
        f.close()


        assert rv["nysa-verilog"] == lv["nysa-verilog"]
    '''

    def test_create_local_entry(self):
        self.sm.create_local_entry("nysa-verilog", "test")
        f = open(os.path.join(site.getuserbase(), TEST_NAME, "versions.json"), "r")
        lv = json.load(f)
        f.close()
        assert lv["nysa-verilog"] == "test"

    def test_get_local_path_dict(self):
        pass

if __name__ == "__main__":
  unittest.main()


