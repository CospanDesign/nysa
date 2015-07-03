#!/usr/bin/python

import unittest
import json
import sys
import os
import time
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.host.driver.sf_camera import SFCamera
from nysa.common.status import Status

from nysa.host.platform_scanner import PlatformScanner

class Test (unittest.TestCase):

    def setUp(self):
        self.s = Status()
        self.s.set_level("fatal")
        plat = ["", None, None]
        pscanner = PlatformScanner()
        platform_dict = pscanner.get_platforms()
        platform_names = platform_dict.keys()

        if "sim" in platform_names:
            #If sim is in the platforms, move it to the end
            platform_names.remove("sim")
            platform_names.append("sim")
        urn = None
        for platform_name in platform_names:
            if plat[1] is not None:
                break

            self.s.Debug("Platform: %s" % str(platform_name))

            platform_instance = platform_dict[platform_name](self.s)
            #self.s.Verbose("Platform Instance: %s" % str(platform_instance))

            instances_dict = platform_instance.scan()

            for name in instances_dict:

                #s.Verbose("Found Platform Item: %s" % str(platform_item))
                n = instances_dict[name]
                plat = ["", None, None]

                if n is not None:
                    self.s.Important("Found a nysa instance: %s" % name)
                    n.read_sdb()
                    #import pdb; pdb.set_trace()
                    if n.is_device_in_platform(SFCamera):
                        plat = [platform_name, name, n]
                        break
                    continue

                #self.s.Verbose("\t%s" % psi)

        if plat[1] is None:
            self.camera = None
            return
        n = plat[2]
        urn = n.find_device(SFCamera)[0]
        self.s.set_level("verbose")
        self.s.Important("Using Platform: %s" % plat[0])
        self.s.Important("Instantiated a SFCamera Device: %s" % urn)
        self.camera = SFCamera(n, urn)

    def test_camera(self):
        if self.camera is None:
            self.s.Fatal("Cannot Run Test when no device is found!")
            return
        self.s.Info ("Testing output ports (like LEDs)")

if __name__ == "__main__":
    unittest.main()

